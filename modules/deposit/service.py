from decimal import Decimal
from typing import Optional, Tuple

from shared.base_service import BaseService
from database.models import (
    User,
    UserWallet,
    Deposit,
    Transaction,
    TransactionType,
    TransactionStatus,
    DepositStatus,
)
from utils.helpers import get_utc_time
from blockchain.tron_client import generate_wallet
from utils.encryption import encrypt_text


class DepositService(BaseService):
    """DB/business logic for deposits (module-scoped service)."""

    # ---- Users (reuse BaseService methods) ----
    def get_user_by_telegram(self, telegram_id: str) -> Optional[User]:  # type: ignore[override]
        return super().get_user_by_telegram(telegram_id)

    def get_user_by_id(self, user_id: int) -> Optional[User]:  # type: ignore[override]
        return super().get_user_by_id(user_id)

    # ---- Wallet helpers ----
    def get_wallet_for_user(self, user_id: int) -> Optional[UserWallet]:
        """Return the first active wallet for a user (is_active=True)."""
        with self.db() as session:
            return (
                session.query(UserWallet)
                .filter(UserWallet.user_id == user_id, UserWallet.is_active.is_(True))
                .order_by(UserWallet.id.asc())
                .first()
            )

    def get_or_create_wallet(self, user_id: int) -> Tuple[UserWallet, bool]:
        """Get first active wallet or create a new one. Returns (wallet, created)."""
        wallet = self.get_wallet_for_user(user_id)
        if wallet:
            return wallet, False

        db = self.get_db()
        address, priv_hex = generate_wallet()
        wallet = UserWallet(
            user_id=user_id,
            address=address,
            private_key_encrypted=encrypt_text(priv_hex),
            is_active=True,
        )
        db.add(wallet)
        self.commit()
        db.refresh(wallet)
        return wallet, True

    # ---- Deposit workflow (for workers and handlers) ----
    def create_deposit(self, user_id: int, wallet_id: int, tx_hash: str, amount: Decimal) -> Deposit:
        """Create a deposit record and a related pending transaction."""
        db = self.get_db()
        dep = Deposit(
            user_id=user_id,
            wallet_id=wallet_id,
            tx_hash=tx_hash,
            amount_trx=amount,
            confirmations=0,
            status=DepositStatus.pending,
        )
        db.add(dep)
        self.commit()
        db.refresh(dep)

        tx = Transaction(
            user_id=user_id,
            type=TransactionType.deposit,
            amount_trx=amount,
            status=TransactionStatus.pending,
            description="User deposit detected",
            reference_id=str(dep.id),
        )
        db.add(tx)
        self.commit()
        return dep

    def confirm_deposit(self, tx_hash: str, confirmations: int = 20) -> Optional[Deposit]:
        """Mark a deposit as confirmed, credit user's balance and stats, update transaction."""
        db = self.get_db()
        dep = db.query(Deposit).filter_by(tx_hash=tx_hash).first()
        if not dep:
            return None
        if dep.status == DepositStatus.confirmed:
            return dep

        dep.status = DepositStatus.confirmed
        dep.confirmations = confirmations
        dep.confirmed_at = get_utc_time()

        user = db.query(User).get(dep.user_id)
        if user:
            user.account_balance += dep.amount_trx
            user.total_deposited += dep.amount_trx

        tx = (
            db.query(Transaction)
            .filter_by(reference_id=str(dep.id), type=TransactionType.deposit)
            .first()
        )
        if tx:
            tx.status = TransactionStatus.completed
            tx.description = f"Deposit confirmed {tx_hash}"
            tx.tx_hash = tx_hash

        self.commit()
        return dep

    def fail_deposit(self, tx_hash: str, reason: str) -> Optional[Deposit]:
        """Mark a deposit as failed and update related transaction description."""
        db = self.get_db()
        dep = db.query(Deposit).filter_by(tx_hash=tx_hash).first()
        if not dep:
            return None
        dep.status = DepositStatus.failed

        tx = (
            db.query(Transaction)
            .filter_by(reference_id=str(dep.id), type=TransactionType.deposit)
            .first()
        )
        if tx:
            tx.status = TransactionStatus.failed
            tx.description = f"Deposit failed: {reason}"
        self.commit()
        return dep


# Singleton instance for easy reuse
deposit_service = DepositService()