from typing import Optional, List

from .base_service import BaseService
from database.models import User, Transaction, TransactionType
from services.wallet_service import get_or_create_wallet
from utils.helpers import generate_referral_code, generate_share_link


class UserService(BaseService):
    """Centralized user operations shared across modules.

    Provides helpers for fetching/creating users, referral code management,
    stats aggregation, share links, transactions listing, and wallet delegation.
    """

    # ---- User fetch/create ----
    def get_user_by_telegram(self, telegram_id: str) -> Optional[User]:  # type: ignore[override]
        """Fetch user by Telegram ID (overrides BaseService to keep signature)."""
        return super().get_user_by_telegram(telegram_id)

    def get_or_create_user(self, telegram_id: str, username: Optional[str] = None) -> User:  # type: ignore[override]
        """Fetch existing user or create a minimal one."""
        return super().get_or_create_user(telegram_id, username)

    # ---- Referral helpers ----
    def generate_unique_referral_code(self) -> str:
        """Generate a referral code unique across users."""
        db = self.get_db()
        code = generate_referral_code()
        while db.query(User).filter_by(referral_code=code).first():
            code = generate_referral_code()
        return code

    def find_sponsor_by_code(self, referral_code: Optional[str]) -> Optional[User]:
        """Find sponsor user by referral code."""
        if not referral_code:
            return None
        db = self.get_db()
        return db.query(User).filter_by(referral_code=referral_code).first()

    def list_direct_referrals(self, user_id: int) -> List[User]:
        """List direct referrals for a given user (users where sponsor_id = user_id)."""
        with self.db() as session:
            return session.query(User).filter_by(sponsor_id=user_id).all()

    def create_user(
        self,
        telegram_id: str,
        username: Optional[str],
        first_name: str,
        last_name: Optional[str],
        referral_code: str,
        sponsor_id: Optional[int],
    ) -> User:
        """Create and persist a new user."""
        db = self.get_db()
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            referral_code=referral_code,
            sponsor_id=sponsor_id,
        )
        db.add(user)
        self.commit()
        db.refresh(user)
        return user

    # ---- Wallet delegation ----
    def get_or_create_wallet_for_user(self, user_id: int):
        """Delegate to wallet service for idempotent wallet creation."""
        return get_or_create_wallet(user_id)

    # ---- Share links ----
    def build_share_link(self, bot_username: str, referral_code: str) -> str:
        """Build share link for Telegram bot with referral code."""
        return generate_share_link(bot_username, referral_code)

    # ---- Transactions ----
    def list_transactions(self, user_id: int, filter_key: Optional[str] = None) -> List[Transaction]:
        """List user transactions with optional filter (deposits/withdrawals)."""
        db = self.get_db()
        q = db.query(Transaction).filter_by(user_id=user_id)
        if filter_key == "deposits":
            q = q.filter_by(type=TransactionType.deposit)
        elif filter_key == "withdrawals":
            q = q.filter_by(type=TransactionType.withdrawal)
        return q.order_by(Transaction.created_at.desc()).all()

    # ---- User settings and stats ----
    def update_user_settings(self, telegram_id: str, **kwargs) -> Optional[User]:
        """Update user mutable fields by Telegram ID; ignore unknown fields."""
        db = self.get_db()
        user = db.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            return None
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        self.commit()
        db.refresh(user)
        return user

    def get_user_stats(self, telegram_id: str) -> dict:
        """Return simple aggregated user stats based on User model fields."""
        user = self.get_user_by_telegram(telegram_id)
        if not user:
            return {}
        # Align to database.models.User fields
        return {
            "total_deposited": float(user.total_deposited or 0),
            "total_withdrawn": float(user.total_withdrawn or 0),
            "total_referral_earnings": float(user.total_referral_earnings or 0),
            "account_balance": float(user.account_balance or 0),
        }


# Singleton instance (optional convenience)
user_service = UserService()