# Deposit-specific message builders (MarkdownV2)
from utils.telegram import escape_markdown_v2, get_separator

try:
    from config import MIN_DEPOSIT_AMOUNT  # type: ignore
except Exception:
    MIN_DEPOSIT_AMOUNT = 1  # Fallback if not defined in config


def msg_deposit_not_registered() -> str:
    return (
        "❌ *You are not registered yet\\!*\n\n"
        "Please use /start to register and get your deposit address\."
    )


def msg_deposit_wallet_not_found() -> str:
    return (
        "⚠️ *Wallet not found\\!*\n\n"
        "Please contact support to get your deposit address\.\n"
        "Use /support for assistance\."
    )


def msg_deposit_wallet_auto_created(address: str) -> str:
    sep = get_separator()
    addr = escape_markdown_v2(address)
    return (
        "🔧 *Wallet Issue Detected*\n"
        f"{sep}\n\n"
        "We noticed a problem with your deposit wallet\.\n"
        "A new wallet has just been created for you\.\n\n"
        f"`{addr}`\n\n"
        "If you were expecting another address, please contact support \(/support\)\."
    )


def msg_deposit_panel(address: str) -> str:
    sep = get_separator()
    addr = escape_markdown_v2(address)
    min_dep = escape_markdown_v2(str(MIN_DEPOSIT_AMOUNT))
    return (
        "🏦 *DEPOSIT TRX*\n"
        f"{sep}\n\n"
        "Send TRX to your personal address below\:\n\n"
        f"`{addr}`\n\n"
        "• Only send TRX to this address\n"
        f"• Minimum deposit: {min_dep} TRX\n"
        "• Funds are credited after confirmations\n"
    )