from telegram import Update
from telegram.ext import ContextTypes

from modules.common.keyboards import main_reply_keyboard
from modules.deposit.messages import (
    msg_deposit_not_registered,
    msg_deposit_wallet_not_found,
    msg_deposit_panel,
    msg_deposit_wallet_auto_created,
)
from modules.deposit.keyboards import deposit_reply_keyboard


class DepositHandler:
    """Deposit handlers. Keep business logic in services and reuse common keyboards."""

    def __init__(self, deposit_service):
        self.deposit_service = deposit_service

    async def handle_deposit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle deposit command."""
        await self.show_deposit_menu(update, context)

    async def show_deposit_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_id = str(update.effective_user.id)

        user = self.deposit_service.get_user_by_telegram(telegram_id)
        if not user:
            await update.message.reply_markdown_v2(
                msg_deposit_not_registered(),
                reply_markup=main_reply_keyboard(),
            )
            return

        wallet = self.deposit_service.get_wallet_for_user(user.id)
        if not wallet:
            # Create wallet on the fly and inform the user
            wallet, created = self.deposit_service.get_or_create_wallet(user.id)
            if created:
                await update.message.reply_markdown_v2(
                    msg_deposit_wallet_auto_created(wallet.address),
                    reply_markup=deposit_reply_keyboard(),
                )
            else:
                # Fallback safety, though created should be True here
                await update.message.reply_markdown_v2(
                    msg_deposit_wallet_not_found(),
                    reply_markup=main_reply_keyboard(),
                )
                return

        # Show the deposit panel with the user's address
        await update.message.reply_markdown_v2(
            msg_deposit_panel(wallet.address),
            reply_markup=deposit_reply_keyboard(),
        )