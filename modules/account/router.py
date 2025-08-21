from modules.common.keyboards import (
    BALANCE_BTN,
    HISTORY_BTN,
    ALL_TRANSACTIONS_BTN,
    DEPOSITS_ONLY_BTN,
    WITHDRAWALS_ONLY_BTN,
)
from .instances import account_handler


class AccountRouter:
    """Account domain router."""
    def __init__(self):
        self.routes = {
            BALANCE_BTN: "handle_balance",
            HISTORY_BTN: "handle_history",
            ALL_TRANSACTIONS_BTN: "handle_history",
            DEPOSITS_ONLY_BTN: "handle_history",
            WITHDRAWALS_ONLY_BTN: "handle_history",
        }
        self.handler = account_handler

    def can_handle(self, message_text: str) -> bool:
        return message_text in self.routes

    def get_handler(self, message_text: str):
        method_name = self.routes[message_text]
        return getattr(self.handler, method_name)
