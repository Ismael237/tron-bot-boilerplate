from telegram import Update
from telegram.ext import ContextTypes

# Import common keyboards
from modules.common.keyboards import MAIN_MENU_BTN, main_reply_keyboard
from utils.logger import get_logger

logger = get_logger(__name__)


class CommonHandler:
    """Common handler for navigation."""

    async def back_to_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Simple navigation back to main menu."""
        await update.message.reply_markdown_v2(MAIN_MENU_BTN, reply_markup=main_reply_keyboard())

    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Log errors and attempt to notify the user gracefully."""
        logger.warning(f'Update "{update}" caused error "{context.error}"')
        try:
            await update.message.reply_text('An error occurred. Please try again or contact support.')
        except Exception:
            try:
                await update.callback_query.message.reply_text('An error occurred. Please try again or contact support.')
            except Exception:
                pass
