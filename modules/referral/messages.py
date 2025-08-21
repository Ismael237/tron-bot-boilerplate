from utils.helpers import escape_markdown_v2, get_separator


def msg_referral_overview(share_link: str, total_referrals: str, total_paid_trx: str, total_pending_trx: str) -> str:
    sep = get_separator()
    link = escape_markdown_v2(share_link)
    return (
        "👥 *Referral Program*\n"
        f"{sep}\n\n"
        f"Share link:\n `{link}`\n\n"
        f"• Direct referrals: {escape_markdown_v2(total_referrals)}\n"
        f"• Paid commissions: {escape_markdown_v2(total_paid_trx)} TRX\n"
        f"• Pending commissions: {escape_markdown_v2(total_pending_trx)} TRX\n"
    )


def msg_referral_info_single_level(rate_percent: str) -> str:
    rate = escape_markdown_v2(rate_percent)
    return (
        "ℹ️ *Referral Info*\n\n"
        f"You earn {rate}\% of your direct referrals' eligible operations\.\n"
        "Rewards are paid automatically when conditions are met\.\n"
    )


def msg_new_referral(sponsor_username: str, friend_username: str) -> str:
    """Notify a sponsor that a new referral joined."""
    friend_username_esc = escape_markdown_v2(friend_username)
    return (
        "🎉 *You got a new referral\!* 🎉\n"
        f"Your friend, {friend_username_esc}, has joined the bot \!\n"
    )