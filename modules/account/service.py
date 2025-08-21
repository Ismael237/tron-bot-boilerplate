from shared.user_service import UserService as SharedUserService


class AccountService(SharedUserService):
    """Account-scoped service.

    Reuses shared `UserService` logic while keeping a module-level entry point,
    similar to `modules/deposit/service.py`. Extend here with account-specific
    business rules if needed.
    """

    # The methods below are inherited from SharedUserService and available for handlers:
    # - get_user_by_telegram(self, telegram_id: str) -> Optional[User]
    # - get_or_create_user(self, telegram_id: str, username: Optional[str] = None) -> User
    # - generate_unique_referral_code(self) -> str
    # - find_sponsor_by_code(self, referral_code: Optional[str]) -> Optional[User]
    # - create_user(...)
    # - get_or_create_wallet_for_user(self, user_id: int)
    # - build_share_link(self, bot_username: str, referral_code: str) -> str
    # - list_transactions(self, user_id: int, filter_key: Optional[str] = None) -> List[Transaction]
    pass

