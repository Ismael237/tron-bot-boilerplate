from database.database import SessionLocal
from database.models import User
from services.wallet_service import get_wallet


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