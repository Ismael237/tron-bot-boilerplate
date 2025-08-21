from abc import ABC
from typing import Optional
from sqlalchemy.orm import Session

from database.database import get_db_session
from database.models import User
from config import TELEGRAM_ADMIN_ID


class BaseService(ABC):
    """Base service with shared DB/session utilities and user helpers.

    - Opens sessions via database.get_db_session (context manager).
    - Reuses a single Session per service instance (lazy opened).
    - Provides explicit close and safe commit with rollback.
    - Offers a db() helper to use the context manager ad-hoc: `with self.db() as db:`
    """

    def __init__(self) -> None:
        self._session: Optional[Session] = None
        self._db_ctx = None  # holds the active context manager when get_db() is used

    # ---- Session handling ----
    def db(self):
        """Return the database session context manager (no persistence)."""
        return get_db_session()

    def get_db(self) -> Session:
        """Return a reusable Session, opened via the context manager on first use."""
        if self._session is None:
            self._db_ctx = get_db_session()
            self._session = self._db_ctx.__enter__()
        return self._session

    def commit(self) -> None:
        """Commit current session safely (rollback on failure)."""
        if self._session is None:
            return
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

    def close_db(self) -> None:
        """Close the persisted Session if opened via get_db()."""
        if self._session is not None and self._db_ctx is not None:
            try:
                # Exit the context manager, which will close the session
                self._db_ctx.__exit__(None, None, None)
            finally:
                self._session = None
                self._db_ctx = None

    # Context manager support
    def __enter__(self):
        self.get_db()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close_db()

    # ---- Common user helpers ----
    def get_user_by_telegram(self, telegram_id: str) -> Optional[User]:
        """Fetch user by Telegram ID."""
        with self.db() as session:
            return session.query(User).filter_by(telegram_id=telegram_id).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Fetch user by internal numeric ID."""
        with self.db() as session:
            return session.query(User).get(user_id)

    def get_or_create_user(self, telegram_id: str, username: Optional[str] = None) -> User:
        """Fetch an existing user or create a minimal one."""
        with self.db() as session:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                return user
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def get_admin_user(self) -> Optional[User]:
        """Return the admin user based on TELEGRAM_ADMIN_ID from config (if set)."""
        if not TELEGRAM_ADMIN_ID:
            return None
        with self.db() as session:
            return session.query(User).filter_by(telegram_id=str(TELEGRAM_ADMIN_ID)).first()