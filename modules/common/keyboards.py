from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# Common button labels (used by multiple domains)
DEPOSIT_BTN = "💰 Deposit"
BALANCE_BTN = "💳 Balance"
WITHDRAW_BTN = "🏧 Withdraw"
SHARE_EARN_BTN = "👥 Share & Earn"
HISTORY_BTN = "📜 History"
INFO_BTN = "ℹ️ Info"

# Navigation
MAIN_MENU_BTN = "🏠 Main Menu"
BACK_BTN = "🔙 Back"
CANCEL_BTN = "❌ Cancel"

# History filters
ALL_TRANSACTIONS_BTN = "📋 All Transactions"
DEPOSITS_ONLY_BTN = "📥 Deposits Only"
WITHDRAWALS_ONLY_BTN = "📤 Withdrawals Only"


# ==================== REPLY KEYBOARDS (COMMON) ====================

def main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Main menu keyboard with primary bot functions (common across the app)."""
    keyboard = [
        [BALANCE_BTN],
        [DEPOSIT_BTN, WITHDRAW_BTN, HISTORY_BTN],
        [SHARE_EARN_BTN, INFO_BTN],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


def history_reply_keyboard() -> ReplyKeyboardMarkup:
    """History submenu keyboard with common filters."""
    keyboard = [
        [ALL_TRANSACTIONS_BTN],
        [DEPOSITS_ONLY_BTN, WITHDRAWALS_ONLY_BTN],
        [MAIN_MENU_BTN],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)



# ==================== INLINE KEYBOARDS (COMMON) ====================

def pagination_inline_keyboard(current_page: int, total_pages: int, callback_prefix: str) -> InlineKeyboardMarkup:
    """Generic pagination keyboard used across history or other lists."""
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"{callback_prefix}_page_{current_page-1}"))

    nav_buttons.append(InlineKeyboardButton(f"📄 {current_page}/{total_pages}", callback_data="current_page"))

    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"{callback_prefix}_page_{current_page+1}"))

    return InlineKeyboardMarkup([nav_buttons])