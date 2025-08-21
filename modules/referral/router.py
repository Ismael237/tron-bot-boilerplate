from .keyboards import SHARE_EARN_BTN, REFERRAL_INFO_BTN
from .instances import referral_handler


class ReferralRouter:
    def __init__(self):
        self.routes = {
            SHARE_EARN_BTN: "show_referral_overview",
            REFERRAL_INFO_BTN: "show_referral_info",
        }
        self.handler = referral_handler

    def can_handle(self, message_text: str) -> bool:
        return message_text in self.routes

    def get_handler(self, message_text: str):
        method_name = self.routes[message_text]
        return getattr(self.handler, method_name)