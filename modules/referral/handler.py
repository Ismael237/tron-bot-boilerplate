from telegram import Update
from telegram.ext import ContextTypes

from modules.common.keyboards import main_reply_keyboard
from modules.common.messages import msg_not_registered_prompt_start
from modules.referral.messages import (
    msg_referral_overview,
    msg_referral_info_single_level,
)
from modules.referral.services import referral_service
from bot.utils import format_trx
from config import REFERRAL_RATE
from utils.helpers import generate_share_link


class ReferralHandler:
    async def handle_referral(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle referral command."""
        await self.show_referral_overview(update, context)
    
    async def show_referral_overview(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = referral_service.get_user_by_telegram(str(update.effective_user.id))
        if not user:
            await update.message.reply_markdown_v2(
                msg_not_registered_prompt_start(),
                reply_markup=main_reply_keyboard(),
            )
            return

        direct_refs = referral_service.get_direct_referrals(user.id)
        total_referrals = str(len(direct_refs))

        summary = referral_service.summarize_commissions(user.id)
        total_paid_trx = format_trx(summary.get("total_paid", 0.0))
        total_pending_trx = format_trx(summary.get("total_pending", 0.0))

        bot_username = context.bot.username
        share_link = generate_share_link(bot_username, user.referral_code)

        msg = msg_referral_overview(
            share_link=share_link,
            total_referrals=total_referrals,
            total_paid_trx=total_paid_trx,
            total_pending_trx=total_pending_trx,
        )
        await update.message.reply_markdown_v2(msg, reply_markup=main_reply_keyboard())

    async def show_referral_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        rate_percent = str(int(REFERRAL_RATE * 100))
        msg = msg_referral_info_single_level(rate_percent)
        if update.message:
            await update.message.reply_markdown_v2(msg, reply_markup=main_reply_keyboard())
        elif update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.message.reply_markdown_v2(msg, reply_markup=main_reply_keyboard())