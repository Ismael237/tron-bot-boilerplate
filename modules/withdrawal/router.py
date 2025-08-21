from modules.common.keyboards import WITHDRAW_BTN
from .keyboards import CONFIRM_WITHDRAW_BTN, CANCEL_WITHDRAW_BTN
from .instances import withdrawal_handler


class WithdrawalRouter:
    def __init__(self):
        self.routes = {
            WITHDRAW_BTN: "start_withdraw",
            CONFIRM_WITHDRAW_BTN: "handle_withdraw_free_text",
            CANCEL_WITHDRAW_BTN: "cancel_withdraw",
        }
        self.handler = withdrawal_handler

    def can_handle(self, message_text: str) -> bool:
        return message_text in self.routes

    def get_handler(self, message_text: str):
        method_name = self.routes[message_text]
        return getattr(self.handler, method_name)