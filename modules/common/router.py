from modules.common.keyboards import (
    MAIN_MENU_BTN,
)
from modules.common.instances import common_handler


class CommonRouter:
    def __init__(self):
        # Map common text buttons to CommonHandler method names
        self.routes = {
            MAIN_MENU_BTN: "back_to_main_menu",
        }
        self.handler = common_handler

    def can_handle(self, message_text: str) -> bool:
        return message_text in self.routes

    def get_handler(self, message_text: str):
        method_name = self.routes[message_text]
        return getattr(self.handler, method_name)