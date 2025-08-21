from telegram import ReplyKeyboardMarkup

from modules.common.keyboards import MAIN_MENU_BTN

# ==================== DEPOSIT BUTTONS ====================
COPY_ADDRESS_BTN = "📋 Copy Address"
SHOW_QR_BTN = "📸 QR Code"
DEPOSIT_HELP_BTN = "❓ Deposit Help"


def deposit_reply_keyboard() -> ReplyKeyboardMarkup:
    """Reply keyboard for deposit actions."""
    keyboard = [
        [COPY_ADDRESS_BTN, SHOW_QR_BTN],
        [DEPOSIT_HELP_BTN],
        [MAIN_MENU_BTN],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)