from .keyboards import (
    INFO_BTN,
    HELP_BTN,
    SUPPORT_BTN,
    ABOUT_BTN,
    Q_A_BTN,
)
from .instances import info_handler


class InfoRouter:
    def __init__(self):
        self.routes = {
            INFO_BTN: "show_info_menu",
            HELP_BTN: "show_help",
            SUPPORT_BTN: "show_support",
            ABOUT_BTN: "show_about",
            Q_A_BTN: "show_faq",
        }
        self.handler = info_handler

    def can_handle(self, message_text: str) -> bool:
        return message_text in self.routes

    def get_handler(self, message_text: str):
        method_name = self.routes[message_text]
        return getattr(self.handler, method_name)