from telegram import ReplyKeyboardMarkup

from modules.common.keyboards import MAIN_MENU_BTN

# ==================== WITHDRAWAL CONSTANTS ====================
CANCEL_WITHDRAW_BTN = "❌ Cancel Withdrawal"
CONFIRM_WITHDRAW_BTN = "✅ Confirm Withdrawal"

# Predefined amount buttons for quick withdraw selections
WITHDRAW_50_BTN = "50 TRX"
WITHDRAW_100_BTN = "100 TRX"
WITHDRAW_500_BTN = "500 TRX"
WITHDRAW_1000_BTN = "1,000 TRX"
WITHDRAW_5000_BTN = "5,000 TRX"


# ==================== REPLY KEYBOARDS ====================

def withdraw_reply_keyboard():
    """Withdraw submenu with predefined amounts"""
    keyboard = [
        [WITHDRAW_50_BTN],
        [WITHDRAW_100_BTN, WITHDRAW_500_BTN],
        [WITHDRAW_1000_BTN, WITHDRAW_5000_BTN],
        [MAIN_MENU_BTN],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def cancel_withdraw_keyboard():
    """Cancel withdrawal keyboard"""
    keyboard = [[CANCEL_WITHDRAW_BTN]]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def withdrawal_confirm_reply_keyboard():
    """Reply keyboard for confirming or cancelling a withdrawal"""
    keyboard = [
        [CONFIRM_WITHDRAW_BTN],
        [CANCEL_WITHDRAW_BTN],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
    )