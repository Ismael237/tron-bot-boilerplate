from decimal import Decimal
from typing import List, Optional

from database.database import SessionLocal
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


class WithdrawalService:
    """DB/business logic for withdrawals."""

    @staticmethod
    def get_user_by_telegram(telegram_id: str):
        session = SessionLocal()
        try:
            return session.query(User).filter_by(telegram_id=telegram_id).first()
        finally:
            session.close()

    @staticmethod
    def get_daily_withdrawals(user_id: int) -> List[Withdrawal]:
        session = SessionLocal()
        try:
            today = get_utc_date()
            return session.query(Withdrawal).filter(
                Withdrawal.user_id == user_id,
                Withdrawal.status != WithdrawalStatus.failed,
                Withdrawal.created_at >= today,
            ).all()
        finally:
            session.close()

    @staticmethod
    def create_withdrawal(user_id: int, amount: Decimal, to_address: str) -> Withdrawal:
        session = SessionLocal()
        try:
            withdrawal = Withdrawal(
                user_id=user_id,
                amount_trx=amount,
                to_address=to_address,
                status=WithdrawalStatus.pending,
                created_at=get_utc_time(),
            )
            session.add(withdrawal)
            session.commit()
            session.refresh(withdrawal)
            return withdrawal
        finally:
            session.close()

    @staticmethod
    def create_withdrawal_transaction(user_id: int, amount: Decimal, withdrawal_id: int) -> Transaction:
        session = SessionLocal()
        try:
            tx = Transaction(
                user_id=user_id,
                type=TransactionType.withdrawal,
                amount=amount,
                status=TransactionStatus.pending,
                description="User initiated withdrawal",
                reference_id=str(withdrawal_id),
                created_at=get_utc_time(),
            )
            session.add(tx)
            session.commit()
            session.refresh(tx)
            return tx
        finally:
            session.close()

    @staticmethod
    def validate_amount(amount: Decimal):
        if amount < Decimal(str(MIN_WITHDRAWAL_AMOUNT)) or amount > Decimal(str(DAILY_WITHDRAWAL_LIMIT)):
            return False
        return True

    @staticmethod
    def calculate_net_amount(amount: Decimal):
        fee_rate = Decimal(str(WITHDRAWAL_FEE_RATE))
        return amount * (Decimal('1') - fee_rate)

    @staticmethod
    def validate_address(address: str):
        return is_valid_tron_address(address)

    # -------- Helpers used by the withdrawal processor worker --------
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        session = SessionLocal()
        try:
            return session.query(User).get(user_id)
        finally:
            session.close()

    @staticmethod
    def list_pending_withdrawals() -> List[Withdrawal]:
        session = SessionLocal()
        try:
            return session.query(Withdrawal).filter(
                Withdrawal.status.in_([WithdrawalStatus.pending, WithdrawalStatus.processing])
            ).all()
        finally:
            session.close()

    @staticmethod
    def complete_withdrawal(user_id: int, withdrawal_id: int, amount_trx: Decimal, tx_hash: str) -> None:
        """Mark withdrawal completed, set tx_hash and processed_at, decrement user earn_balance, update tx record."""
        session = SessionLocal()
        try:
            wd = session.query(Withdrawal).get(withdrawal_id)
            user = session.query(User).get(user_id)
            if not wd or not user:
                raise ValueError("Withdrawal or User not found")

            wd.tx_hash = tx_hash
            wd.status = WithdrawalStatus.completed
            wd.processed_at = get_utc_time()
            user.earn_balance -= Decimal(amount_trx)

            tx_record = session.query(Transaction).filter_by(
                reference_id=str(withdrawal_id), type=TransactionType.withdrawal
            ).first()
            if tx_record:
                tx_record.description = f"Withdrawal {tx_hash}"
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def fail_withdrawal(withdrawal_id: int, reason: str, tx_hash: Optional[str] = None) -> None:
        """Mark withdrawal as failed and update related transaction description."""
        session = SessionLocal()
        try:
            wd = session.query(Withdrawal).get(withdrawal_id)
            if not wd:
                raise ValueError("Withdrawal not found")
            wd.status = WithdrawalStatus.failed
            tx_record = session.query(Transaction).filter_by(
                reference_id=str(withdrawal_id), type=TransactionType.withdrawal
            ).first()
            if tx_record:
                suffix = f" (tx {tx_hash})" if tx_hash else ""
                tx_record.description = f"Withdrawal failed: {reason}{suffix}"
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()