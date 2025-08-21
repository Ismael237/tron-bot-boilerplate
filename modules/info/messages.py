from utils.telegram import format_trx_escaped, escape_markdown_v2
from utils.helpers import get_separator


def msg_info_menu() -> str:
    return (
        "ℹ️ *Information & Help*\n\n"
        "Choose an option below for help, support, or info\\."
    )


def msg_help_panel() -> str:
    sep = get_separator()
    return (
        "❓ *Help*\n"
        f"{sep}\n\n"
        "Use the main menu to navigate\.\n"
        "• Deposit to fund your account\n"
        "• Withdraw to cash out\n"
        "• Share & Earn to get referral rewards\n"
    )


def msg_support_panel(admin_username: str | None) -> str:
    user = escape_markdown_v2(admin_username or "admin")
    return (
        "🆘 *Support*\n\n"
        f"Contact: @{user}\n"
        "We will assist you as soon as possible\."
    )


def msg_about_panel() -> str:
    return (
        "ℹ️ *About*\n\n"
        "This bot provides a simple TRX deposit and withdrawal experience\."
    )


def msg_faq_panel(daily_limit: str, minimum_withdrawal: str, fee_percent: str) -> str:
    return (
        "🤔 *Q&A*\n\n"
        f"• Daily withdrawal limit: {format_trx_escaped(daily_limit)} TRX\n"
        f"• Minimum withdrawal: {format_trx_escaped(minimum_withdrawal)} TRX\n"
        f"• Withdrawal fee: {escape_markdown_v2(fee_percent)}\n"
    )