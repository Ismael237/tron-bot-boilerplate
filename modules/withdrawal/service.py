from decimal import Decimal
from typing import List, Optional

from shared.base_service import BaseService
from database.models import (
    User,
    Withdrawal,
    WithdrawalStatus,
    Transaction,
    TransactionType,
    TransactionStatus,
)
from utils.helpers import get_utc_date, get_utc_time
from config import DAILY_WITHDRAWAL_LIMIT, MIN_WITHDRAWAL_AMOUNT, WITHDRAWAL_FEE_RATE
from utils.validators import is_valid_tron_address


class WithdrawalService(BaseService):
    """DB/business logic for withdrawals (module-scoped service)."""

    # ---- Users ----
    def get_user_by_telegram(self, telegram_id: str) -> Optional[User]:  # type: ignore[override]
        return super().get_user_by_telegram(telegram_id)

    def get_user_by_id(self, user_id: int) -> Optional[User]:  # type: ignore[override]
        return super().get_user_by_id(user_id)

    # ---- Queries ----
    def get_daily_withdrawals(self, user_id: int) -> List[Withdrawal]:
        with self.db() as session:
            today = get_utc_date()
            return (
                session.query(Withdrawal)
                .filter(
                    Withdrawal.user_id == user_id,
                    Withdrawal.status != WithdrawalStatus.failed,
                    Withdrawal.created_at >= today,
                )
                .all()
            )

    def list_pending_withdrawals(self) -> List[Withdrawal]:
        with self.db() as session:
            return (
                session.query(Withdrawal)
                .filter(Withdrawal.status.in_([WithdrawalStatus.pending, WithdrawalStatus.processing]))
                .all()
            )

    # ---- Mutations ----
    def create_withdrawal(self, user_id: int, amount: Decimal, to_address: str) -> Withdrawal:
        db = self.get_db()
        user = db.query(User).get(user_id)
        if not user:
            raise ValueError("User not found")
        if Decimal(user.account_balance) < amount:
            raise ValueError("Insufficient balance")

        fee_rate = Decimal(str(WITHDRAWAL_FEE_RATE))
        fee = amount * fee_rate

        # Deduct immediately; refunds handled on failure
        user.account_balance -= amount

        wd = Withdrawal(
            user_id=user_id,
            amount_trx=amount,
            fee_trx=fee,
            to_address=to_address,
            status=WithdrawalStatus.pending,
            created_at=get_utc_time(),
        )
        db.add(wd)
        self.commit()
        db.refresh(wd)
        return wd

    def create_withdrawal_transaction(self, user_id: int, amount: Decimal, withdrawal_id: int) -> Transaction:
        db = self.get_db()
        tx = Transaction(
            user_id=user_id,
            type=TransactionType.withdrawal,
            amount_trx=amount,
            status=TransactionStatus.pending,
            description="User initiated withdrawal",
            reference_id=str(withdrawal_id),
        )
        db.add(tx)
        self.commit()
        db.refresh(tx)
        return tx

    def complete_withdrawal(self, user_id: int, withdrawal_id: int, amount_trx: Decimal, tx_hash: str) -> None:
        """Mark withdrawal completed and update related records."""
        db = self.get_db()
        wd = db.query(Withdrawal).get(withdrawal_id)
        user = db.query(User).get(user_id)
        if not wd or not user:
            raise ValueError("Withdrawal or User not found")

        wd.tx_hash = tx_hash
        wd.status = WithdrawalStatus.completed
        wd.processed_at = get_utc_time()

        user.total_withdrawn += Decimal(amount_trx)

        tx_record = (
            db.query(Transaction)
            .filter_by(reference_id=str(withdrawal_id), type=TransactionType.withdrawal)
            .first()
        )
        if tx_record:
            tx_record.description = f"Withdrawal {tx_hash}"
        self.commit()

    def fail_withdrawal(self, withdrawal_id: int, user_id: int, reason: str, tx_hash: Optional[str] = None) -> None:
        """Mark withdrawal as failed and refund balance; update transaction description."""
        db = self.get_db()
        wd = db.query(Withdrawal).get(withdrawal_id)
        user = db.query(User).get(user_id)
        if not wd or not user:
            raise ValueError("Withdrawal or User not found")

        user.account_balance += wd.amount_trx + wd.fee_trx
        wd.status = WithdrawalStatus.failed

        tx_record = (
            db.query(Transaction)
            .filter_by(reference_id=str(withdrawal_id), type=TransactionType.withdrawal)
            .first()
        )
        if tx_record:
            suffix = f" (tx {tx_hash})" if tx_hash else ""
            tx_record.description = f"Withdrawal failed: {reason}{suffix}"
        self.commit()

    # ---- Validation/helpers ----
    @staticmethod
    def validate_amount(amount: Decimal) -> bool:
        return not (
            amount < Decimal(str(MIN_WITHDRAWAL_AMOUNT))
            or amount > Decimal(str(DAILY_WITHDRAWAL_LIMIT))
        )

    @staticmethod
    def calculate_net_amount(amount: Decimal) -> Decimal:
        fee_rate = Decimal(str(WITHDRAWAL_FEE_RATE))
        return amount * (Decimal("1") - fee_rate)

    @staticmethod
    def validate_address(address: str) -> bool:
        return is_valid_tron_address(address)