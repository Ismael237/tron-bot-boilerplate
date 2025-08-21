from telegram import ReplyKeyboardMarkup
from modules.common.keyboards import (
    # button labels
    DEPOSIT_BTN,
    BALANCE_BTN,
    WITHDRAW_BTN,
    SHARE_EARN_BTN,
    HISTORY_BTN,
    INFO_BTN,
    MAIN_MENU_BTN,
    BACK_BTN,
    CANCEL_BTN,
    ALL_TRANSACTIONS_BTN,
    DEPOSITS_ONLY_BTN,
    WITHDRAWALS_ONLY_BTN,
    # builders
    pagination_inline_keyboard as _common_pagination_inline_keyboard,
)

__all__ = [
    # buttons
    "DEPOSIT_BTN",
    "BALANCE_BTN",
    "WITHDRAW_BTN",
    "SHARE_EARN_BTN",
    "HISTORY_BTN",
    "INFO_BTN",
    "MAIN_MENU_BTN",
    "BACK_BTN",
    "CANCEL_BTN",
    "ALL_TRANSACTIONS_BTN",
    "DEPOSITS_ONLY_BTN",
    "WITHDRAWALS_ONLY_BTN",
    # builders
    "history_reply_keyboard",
    "pagination_inline_keyboard",
]


def history_reply_keyboard() -> ReplyKeyboardMarkup:
    """History submenu keyboard with common filters."""
    keyboard = [
        [ALL_TRANSACTIONS_BTN],
        [DEPOSITS_ONLY_BTN, WITHDRAWALS_ONLY_BTN],
        [MAIN_MENU_BTN],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


def pagination_inline_keyboard(current_page: int, total_pages: int, callback_prefix: str):
    """Account domain pagination (delegates to common)."""
    return _common_pagination_inline_keyboard(current_page, total_pages, callback_prefix)
