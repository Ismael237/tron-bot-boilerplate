from decimal import Decimal
from typing import List, Optional

from database.database import SessionLocal
from database.models import (
    User,
    UserWallet,
    Deposit,
    DepositStatus,
    Transaction,
    TransactionType,
    BalanceType,
)
from services.wallet_service import get_wallet
from utils.helpers import get_utc_time


class DepositService:
    """DB/business logic for deposit domain. Telegram logic lives in bot/handlers/deposit_handler.py"""

    @staticmethod
    def get_user_by_telegram(telegram_id: str):
        session = SessionLocal()
        try:
            return session.query(User).filter_by(telegram_id=telegram_id).first()
        finally:
            session.close()

    @staticmethod
    def get_wallet_for_user(user_id: int):
        return get_wallet(user_id)

    # -------- Added helpers for deposit monitor --------
    @staticmethod
    def list_user_wallets() -> List[UserWallet]:
        session = SessionLocal()
        try:
            return session.query(UserWallet).all()
        finally:
            session.close()

    @staticmethod
    def get_deposit_by_tx_hash(tx_hash: str) -> Optional[Deposit]:
        session = SessionLocal()
        try:
            return session.query(Deposit).filter_by(tx_hash=tx_hash).first()
        finally:
            session.close()

    @staticmethod
    def create_deposit_if_new(
        user_id: int,
        wallet_id: int,
        tx_hash: str,
        amount_trx: Decimal,
        confirmations: int,
    ) -> Deposit:
        """Create a deposit row if not exists. Returns the persisted row."""
        session = SessionLocal()
        try:
            existing = session.query(Deposit).filter_by(tx_hash=tx_hash).first()
            if existing:
                return existing

            status = DepositStatus.confirmed if confirmations >= 19 else DepositStatus.pending
            deposit = Deposit(
                user_id=user_id,
                wallet_id=wallet_id,
                tx_hash=tx_hash,
                amount_trx=amount_trx,
                confirmations=confirmations,
                status=status,
                created_at=get_utc_time(),
                confirmed_at=get_utc_time() if status == DepositStatus.confirmed else None,
            )
            session.add(deposit)
            session.commit()
            session.refresh(deposit)
            return deposit
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def credit_user_ad_balance_and_log_tx(user_id: int, amount_trx: Decimal, reference_tx_id: str) -> Transaction:
        """Credits user's ad balance and records a deposit transaction."""
        session = SessionLocal()
        try:
            user = session.query(User).get(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")

            user.ad_balance += amount_trx
            tx = Transaction(
                user_id=user.id,
                type=TransactionType.deposit,
                amount_trx=amount_trx,
                balance_type=BalanceType.ad_balance,
                description=f"Deposit {reference_tx_id}",
                reference_id=reference_tx_id,
            )
            session.add(tx)
            session.commit()
            session.refresh(tx)
            return tx
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        session = SessionLocal()
        try:
            return session.query(User).get(user_id)
        finally:
            session.close()