from decimal import Decimal
from config import TELEGRAM_ADMIN_USERNAME
from utils.helpers import escape_markdown_v2, get_separator
from utils.telegram import format_trx_escaped, format_date


def msg_already_registered() -> str:
    sep = get_separator()
    return (
        "⚠️ *You are already registered\!* ⚠️\n"
        f"{sep}\n\n"
        "🎯 *Available actions :*\n\n"
        "💰 Use /balance to check your balance\n"
        "🏦 Type /deposit to see your deposit address\n"
        "👥 Use /referral for your referral code\n\n"
        f"{sep}\n"
        "🚀 *Ready\?* Start now \!"
    )


def msg_welcome_registration(
    username: str,
    address: str,
    share_link: str,
    support_username: str | None = None,
    sponsor_line: str | None = None,
) -> str:
    sep = get_separator()
    escaped_address = escape_markdown_v2(address)
    escaped_username = escape_markdown_v2(username)
    support_username = support_username or f"@{TELEGRAM_ADMIN_USERNAME}"
    escaped_support_username = escape_markdown_v2(support_username)
    escaped_share_link = escape_markdown_v2(share_link)

    return (
        "🎉 *WELCOME TO THE TRON BOT \!* 🎉\n"
        f"{sep}\n\n"
        f"👋 Hi {escaped_username} \!\n"
        f"✅ Registration successful \!\n\n"
        "🏦 *YOUR WALLET*\n"
        f"{sep}\n\n"
        f"💰 *TRON Deposit Address :*\n"
        f"`{escaped_address}`\n\n"
        "👥 *REFERRAL LINK*\n"
        f"{sep}\n\n"
        f"📤 *Your referral link\\(click to copy\\):*\n\n"
        f"`{escaped_share_link}`\n\n"
        "💡 Share it to earn commissions \!\n"
        f"{sponsor_line or ''}\n"
        "🚀 *START*\n"
        f"{sep}\n\n"
        "📋 *Next Steps :*\n\n"
        "1️⃣ Deposit TRON \\(TRX\\) to your address\n"
        "2️⃣ Use /balance to check your balance\n"
        "4️⃣ Start earning profits \!\n"
        f"{sep}\n"
        "💬 *Useful Commands :*\n\n"
        "• /deposit \\- See your deposit address\n"
        "• /balance \\- Check your balance\n"
        "• /referral \\- Referral system\n"
        "• /help \\- Help and support\n\n"
        "🎯 *Ready to start \?*\n"
        f"📞 Support : {escaped_support_username}"
    )


def msg_balance(
    balance_trx: Decimal,
    total_deposited_trx: Decimal,
    total_withdrawn_trx: Decimal,
) -> str:
    balance_trx_esc = format_trx_escaped(balance_trx)
    total_deposited_trx_esc = format_trx_escaped(total_deposited_trx)
    total_withdrawn_trx_esc = format_trx_escaped(total_withdrawn_trx)
    sep = get_separator()
    return (
        "💰 *Your TRX Balance*\n"
        f"{sep}\n"
        f"💵 *Balance*: `{balance_trx_esc}`\n"
        f"{sep}\n"
        f"💳 *Total Deposited*: `{total_deposited_trx_esc}`\n"
        f"🏧 *Total Withdrawn*: `{total_withdrawn_trx_esc}`\n"
    )


def msg_select_history_filter() -> str:
    return escape_markdown_v2("Select a transaction filter:")


def msg_no_transactions_for_filter() -> str:
    return "\u2139 _No transactions found for this filter\\._"


def msg_history_page(transactions, page: int, total_pages: int) -> str:
    sep = get_separator()
    lines = [
        f"📝 *Transaction History* \\(Page {page}/{total_pages}\\)\n",
        f"{sep}\n",
    ]

    emoji_map = {
        "deposit": "➕",
        "withdrawal": "➖",
        "investment": "💼",
        "reward": "💸",
        "commission": "🎁",
    }
    status_emoji = {
        "pending": "⏳",
        "completed": "✅",
        "failed": "❌",
        "paid": "💰",
    }

    for tx in transactions:
        type_key = getattr(getattr(tx, 'type', None), 'value', str(getattr(tx, 'type', ''))).lower()
        status_key = getattr(getattr(tx, 'status', None), 'value', str(getattr(tx, 'status', ''))).lower()
        type_emoji = emoji_map.get(type_key, "🔹")
        stat_emoji = status_emoji.get(status_key, "🔸")
        lines.extend([
            f"  {type_emoji} *Type*: {escape_markdown_v2(getattr(getattr(tx, 'type', None), 'value', ''))}\n",
            f"  📅 *Date*: `{escape_markdown_v2(format_date(tx.created_at))}`\n",
            f"  💵 *Amount*: {format_trx_escaped(tx.amount_trx)}\n",
            f"  {stat_emoji} *Status*: _{escape_markdown_v2(getattr(getattr(tx, 'status', None), 'value', ''))}_\n",
            f"{sep}\n",
        ])

    return "".join(lines)
