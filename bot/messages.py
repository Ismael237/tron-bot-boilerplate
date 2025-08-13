from config import TELEGRAM_ADMIN_USERNAME
from utils.helpers import escape_markdown_v2, get_separator
from bot.utils import format_trx, format_date, format_trx_escaped

# Message builders (return MarkdownV2 strings)

def msg_already_registered() -> str:
    sep = get_separator()
    return (
        "⚠️ *You are already registered\\!* ⚠️\n"
        f"{sep}\n\n"
        "🎯 *Available actions \\:*\n\n"
        "💰 Use /balance to check your balance\n"
        "🏦 Type /deposit to see your deposit address\n"
        "👥 Use /referral for your referral code\n\n"
        f"{sep}\n"
        "🚀 *Ready to invest \\?* Start now \\!"
    )


def msg_new_referral(sponsor_username: str, friend_username: str) -> str:
    sponsor_username_esc = escape_markdown_v2(sponsor_username)
    friend_username_esc = escape_markdown_v2(friend_username)
    return (
        "🎉 *You got a new referral\\!* 🎉\n"
        f"Your friend, {friend_username_esc}, has joined the bot \\!\n"
        "You will receive a commission on their investment \\!\n"
    )


def msg_welcome_registration(
    username: str,
    address: str,
    share_link: str,
    support_username: str = None,
    sponsor_line: str | None = None,
) -> str:
    sep = get_separator()
    escaped_address = escape_markdown_v2(address)
    escaped_username = escape_markdown_v2(username)
    support_username = support_username or f"@{TELEGRAM_ADMIN_USERNAME}"
    escaped_support_username = escape_markdown_v2(support_username)
    escaped_share_link = escape_markdown_v2(share_link)

    return (
        "🎉 *WELCOME TO THE TRON INVESTMENT BOT \\!* 🎉\n"
        f"{sep}\n\n"
        f"👋 Hi {escaped_username} \\!\n"
        f"✅ Registration successful \\!\n\n"
        "🏦 *YOUR WALLET*\n"
        f"{sep}\n\n"
        f"💰 *TRON Deposit Address \\:*\n"
        f"`{escaped_address}`\n\n"
        "👥 *REFERRAL LINK*\n"
        f"{sep}\n\n"
        f"📤 *Your referral link\\(click to copy\\)\\:*\n\n"
        f"`{escaped_share_link}`\n\n"
        "💡 Share it to earn commissions \\!\n"
        f"{sponsor_line or ''}\n"
        "🚀 *START INVESTING*\n"
        f"{sep}\n\n"
        "📋 *Next Steps \\:*\n\n"
        "1️⃣ Deposit TRON \\(TRX\\) to your address\n"
        "2️⃣ Use /balance to check your balance\n"
        "3️⃣ Choose an investment plan\n"
        "4️⃣ Start earning profits \\!\n"
        f"{sep}\n"
        "💬 *Useful Commands :*\n\n"
        "• /deposit \\- See your deposit address\n"
        "• /balance \\- Check your balance\n"
        "• /invest \\- Investment plans\n"
        "• /referral \\- Referral system\n"
        "• /help \\- Help and support\n\n"
        "🎯 *Ready to start your investment journey \\?*\n"
        f"📞 Support \\: {escaped_support_username}"
    )


def msg_not_registered_prompt_start() -> str:
    return "\u2757 *You are not registered\\.* Use /start to register\\."

def msg_user_not_found() -> str:
    return "User not found\\."


def msg_balance(
    balance_trx: str,
    total_invested_trx: str,
    total_earned_trx: str,
) -> str:
    sep = get_separator()
    return (
        "💰 *Your TRX Balance*\n"
        f"{sep}\n"
        f"💵 *Balance*\\: `{escape_markdown_v2(balance_trx)}`\n"
        f"{sep}\n"
        f"💳 *Total Invested*\\: `{escape_markdown_v2(total_invested_trx)}`\n"
        f"💸 *Total Earned*\\: `{escape_markdown_v2(total_earned_trx)}`\n"
        f"{sep}\n"
        f"📈 _{escape_markdown_v2('Keep investing to grow your earnings!')}_\n"
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
            f"  {type_emoji} *Type*\\: {escape_markdown_v2(getattr(getattr(tx, 'type', None), 'value', ''))}\n",
            f"  📅 *Date*\\: `{escape_markdown_v2(format_date(tx.created_at))}`\n",
            f"  💵 *Amount*\\: {format_trx_escaped(tx.amount)}\n",
            f"  {stat_emoji} *Status*\\: _{escape_markdown_v2(getattr(getattr(tx, 'status', None), 'value', ''))}_\n",
            f"{sep}\n",
        ])

    return "".join(lines)
