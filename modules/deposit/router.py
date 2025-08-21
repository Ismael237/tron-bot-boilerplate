from modules.common.keyboards import DEPOSIT_BTN
from .instances import deposit_handler


class DepositRouter:
    """Deposit domain router."""
    def __init__(self):
        self.routes = {
            DEPOSIT_BTN: "show_deposit_menu",
        }
        self.handler = deposit_handler

    def can_handle(self, message_text: str) -> bool:
        return message_text in self.routes

    def get_handler(self, message_text: str):
        method_name = self.routes[message_text]
        return getattr(self.handler, method_name)