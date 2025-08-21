from .handler import AccountHandler
from .service import AccountService

account_service = AccountService()

account_handler = AccountHandler(account_service)


