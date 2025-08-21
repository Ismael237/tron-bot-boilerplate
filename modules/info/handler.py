from telegram import Update
from telegram.ext import ContextTypes


from utils.telegram import format_trx_escaped
from .keyboards import (
    info_reply_keyboard,
)
from .messages import (
    msg_info_menu,
    msg_help_panel,
    msg_support_panel,
    msg_about_panel,
    msg_faq_panel,
)
from modules.referral.instances import referral_handler
from config import (
    DAILY_WITHDRAWAL_LIMIT,
    MIN_WITHDRAWAL_AMOUNT,
    TELEGRAM_ADMIN_USERNAME,
    WITHDRAWAL_FEE_RATE,
)


class InfoHandler:
    def __init__(self) -> None:
        self._referral = referral_handler

    async def handle_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle info command."""
        await self.show_info_menu(update, context)

    async def show_info_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show info menu."""
        await update.message.reply_markdown_v2(
            msg_info_menu(),
            reply_markup=info_reply_keyboard(),
        )

    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle help command."""
        await self.show_help(update, context)

    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help panel."""
        await update.message.reply_markdown_v2(
            msg_help_panel(),
            reply_markup=info_reply_keyboard(),
        )

    async def handle_support(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle support command."""
        await self.show_support(update, context)

    async def show_support(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show support panel."""
        await update.message.reply_markdown_v2(
            msg_support_panel(TELEGRAM_ADMIN_USERNAME),
            reply_markup=info_reply_keyboard(),
        )

    async def handle_about(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle about command."""
        await self.show_about(update, context)

    async def show_about(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show about panel."""
        await update.message.reply_markdown_v2(
            msg_about_panel(),
            reply_markup=info_reply_keyboard(),
        )

    async def handle_faq(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle faq command."""
        await self.show_faq(update, context)

    async def show_faq(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show faq panel."""
        daily = DAILY_WITHDRAWAL_LIMIT
        minimum = MIN_WITHDRAWAL_AMOUNT
        fee_percent = f"{int(WITHDRAWAL_FEE_RATE * 100)}%"
        await update.message.reply_markdown_v2(
            msg_faq_panel(daily, minimum, fee_percent),
            reply_markup=info_reply_keyboard(),
        )

    async def handle_referral_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle referral info command."""
        # Delegate to referral module's info handler to keep single source of truth
        return await self._referral.show_referral_info(update, context)