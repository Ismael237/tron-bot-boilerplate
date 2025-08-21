from modules.common.keyboards import MAIN_MENU_BTN
from telegram import ReplyKeyboardMarkup


# Info button labels
INFO_BTN = "ℹ️ Info"

# Info submenu
HELP_BTN = "❓ Help"
SUPPORT_BTN = "🆘 Support"
ABOUT_BTN = "ℹ️ About"
Q_A_BTN = "🤔 Q&A"
REFERRAL_INFO_BTN = "👥 Referral Info"


def info_reply_keyboard() -> ReplyKeyboardMarkup:
    """Info submenu keyboard with common help/support/about/faq entries."""
    keyboard = [
        [HELP_BTN, SUPPORT_BTN],
        [ABOUT_BTN, Q_A_BTN, REFERRAL_INFO_BTN],
        [MAIN_MENU_BTN],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
    )