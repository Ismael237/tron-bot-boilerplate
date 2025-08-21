# Withdrawal-specific message builders (MarkdownV2)
from decimal import Decimal
from utils.helpers import escape_markdown_v2, get_separator
from utils.telegram import format_trx


def msg_withdraw_start(balance_trx: str, min_trx: str, max_trx: str, main_menu_btn: str) -> str:
    sep = get_separator()
    return (
        "🏧 *WITHDRAW TRX*\n"
        f"{sep}\n\n"
        f"Current balance: *{escape_markdown_v2(balance_trx)}* TRX\n"
        f"Minimum: *{escape_markdown_v2(min_trx)}* TRX\n"
        f"Daily limit: *{escape_markdown_v2(max_trx)}* TRX\n\n"
        f"Use the keyboard below to continue or tap *{escape_markdown_v2(main_menu_btn)}* to return\\."
    )


def msg_invalid_amount() -> str:
    return "❌ Invalid amount\\. Please enter a valid TRX value\\."


def msg_amount_out_of_bounds(min_trx: str, max_trx: str) -> str:
    return (
        "❌ Amount out of bounds\\.\n"
        f"Minimum: *{escape_markdown_v2(min_trx)}* TRX\n"
        f"Daily limit: *{escape_markdown_v2(max_trx)}* TRX"
    )


def msg_insufficient_balance() -> str:
    return "❌ Insufficient balance\\."


def msg_ask_address(amount_trx: str, net_trx: str, fee_percent: str) -> str:
    return (
        "📤 Please enter your TRX address\n\n"
        f"Amount: *{escape_markdown_v2(amount_trx)}* TRX\n"
        f"Net after fees \({escape_markdown_v2(fee_percent)}\): *{escape_markdown_v2(net_trx)}* TRX"
    )


def msg_invalid_address() -> str:
    return "❌ Invalid TRX address\\. Please try again\\."


def msg_confirm_withdraw(amount_trx: Decimal, address: str) -> str:
    amount_trx = format_trx(amount_trx)
    return (
        "✅ Confirm withdrawal\n\n"
        f"Amount: *{escape_markdown_v2(amount_trx)}* TRX\n"
        f"To: `{escape_markdown_v2(address)}`\n\n"
        "Use the keyboard to Confirm or Cancel\\."
    )


def msg_daily_limit_exceeded(limit_trx: str, withdrawn_today_trx: str, remaining_trx: str, requested_trx: str) -> str:
    return (
        "❌ Daily limit exceeded\!\n\n"
        f"Limit: *{escape_markdown_v2(limit_trx)}* TRX\n"
        f"Withdrawn today: *{escape_markdown_v2(withdrawn_today_trx)}* TRX\n"
        f"Remaining: *{escape_markdown_v2(remaining_trx)}* TRX\n"
        f"Requested: *{escape_markdown_v2(requested_trx)}* TRX"
    )


def msg_withdraw_submitted(amount_trx: str, remaining_trx: str) -> str:
    return (
        "🕒 Withdrawal submitted\!\n\n"
        f"Amount: *{escape_markdown_v2(amount_trx)}* TRX\n"
        f"Daily remaining after this: *{escape_markdown_v2(remaining_trx)}* TRX\n"
        "You will receive a notification once processed\\."
    )


def msg_withdraw_cancelled() -> str:
    return "❎ Withdrawal cancelled\\."


def msg_session_expired() -> str:
    return "⌛ Session expired\\. Please start again\\."