from database.database import SessionLocal
from database.models import User, Transaction, TransactionType
from services.wallet_service import get_or_create_wallet
from utils.helpers import generate_referral_code, generate_share_link

class UserService:
    """Encapsulates all DB interactions related to users and their transactions."""

    @staticmethod
    def get_user_by_telegram(telegram_id: str):
        session = SessionLocal()
        try:
            return session.query(User).filter_by(telegram_id=telegram_id).first()
        finally:
            session.close()

    @staticmethod
    def generate_unique_referral_code() -> str:
        session = SessionLocal()
        try:
            code = generate_referral_code()
            while session.query(User).filter_by(referral_code=code).first():
                code = generate_referral_code()
            return code
        finally:
            session.close()

    @staticmethod
    def find_sponsor_by_code(referral_code: str):
        if not referral_code:
            return None
        session = SessionLocal()
        try:
            return session.query(User).filter_by(referral_code=referral_code).first()
        finally:
            session.close()

    @staticmethod
    def create_user(telegram_id: str, username: str, referral_code: str, sponsor_id: int | None):
        session = SessionLocal()
        try:
            user = User(
                telegram_id=telegram_id,
                username=username,
                referral_code=referral_code,
                sponsor_id=sponsor_id,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        finally:
            session.close()

    @staticmethod
    def get_or_create_wallet_for_user(user_id: int):
        return get_or_create_wallet(user_id)

    @staticmethod
    def build_share_link(bot_username: str, referral_code: str) -> str:
        return generate_share_link(bot_username, referral_code)

    @staticmethod
    def list_transactions(user_id: int, filter_key: str | None = None):
        session = SessionLocal()
        try:
            query = session.query(Transaction).filter_by(user_id=user_id)
            if filter_key == "deposits":
                query = query.filter_by(type=TransactionType.deposit)
            elif filter_key == "withdrawals":
                query = query.filter_by(type=TransactionType.withdrawal)
            return query.order_by(Transaction.created_at.desc()).all()
        finally:
            session.close()
