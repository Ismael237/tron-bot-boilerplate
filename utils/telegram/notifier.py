import asyncio
from telegram import Bot, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from utils.logger import logger
from config import TELEGRAM_BOT_TOKEN


async def notify_user(telegram_id: str, message: str, reply_markup: ReplyKeyboardMarkup | None = None) -> None:
    """Send a Markdown-v2 formatted message to the given Telegram user, if possible."""
    if not telegram_id:
        return
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=message,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=reply_markup,
        )
    except Exception as e:
        logger.error(f"[Notify] Failed to send message to {telegram_id}: {e}")


def safe_notify_user(telegram_id: str, message: str, reply_markup: ReplyKeyboardMarkup | None = None) -> None:
    """Safely send a message, handling missing or running event loop."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as e:
        if "There is no current event loop" in str(e):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            raise

    try:
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(notify_user(telegram_id, message, reply_markup), loop)
        else:
            loop.run_until_complete(notify_user(telegram_id, message, reply_markup))
    except Exception as e:
        logger.error(f"[Notify] Failed to notify {telegram_id}: {e}")
