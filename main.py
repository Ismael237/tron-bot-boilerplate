import asyncio
import atexit

from modules.common.instances import common_handler
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.ext import CallbackQueryHandler

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor as APSchedulerThreadPoolExecutor

from config import (
    TELEGRAM_BOT_TOKEN, DATABASE_URL,
    DEPOSIT_CHECK_INTERVAL, WITHDRAWAL_PROCESS_INTERVAL,
    AP_SCHEDULER_THREAD_POOL_SIZE
)

from database import init_database

from core.middleware import AuthMiddleware, LoggingMiddleware, RateLimitMiddleware
from core.router_registry import RouterRegistry

from modules.account import AccountRouter, account_handler
from modules.common import CommonRouter
from modules.deposit import DepositRouter, deposit_handler
from modules.info import InfoRouter, info_handler
from modules.referral import ReferralRouter, referral_handler
from modules.withdrawal import WithdrawalRouter, withdrawal_handler

from workers.deposit_monitor import run_deposit_monitor
from workers.withdrawal_processor import run_withdrawal_processor

from utils.logger import get_logger


logger = get_logger(__name__)

# Build a single global RouterRegistry with all routers and middlewares
registry = RouterRegistry()
registry.register_module("account", AccountRouter())
registry.register_module("common", CommonRouter())
registry.register_module("info", InfoRouter())
registry.register_module("referral", ReferralRouter())
registry.register_module("deposit", DepositRouter())
registry.register_module("withdrawal", WithdrawalRouter())
registry.register_middleware(AuthMiddleware())
registry.register_middleware(LoggingMiddleware())
registry.register_middleware(RateLimitMiddleware(1.0))


def start_scheduler():
    jobstores = {'default': SQLAlchemyJobStore(url=DATABASE_URL)}
    executors = {'default': APSchedulerThreadPoolExecutor(AP_SCHEDULER_THREAD_POOL_SIZE)}
    scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, timezone='UTC')
    
    # cron job
    scheduler.add_job(run_deposit_monitor, 'interval', minutes=DEPOSIT_CHECK_INTERVAL, id='monitor_deposits', replace_existing=True)
    scheduler.add_job(run_withdrawal_processor, 'interval', minutes=WITHDRAWAL_PROCESS_INTERVAL, id='process_withdrawals', replace_existing=True)
    
    scheduler.start()
    logger.info("[Scheduler] APScheduler started with persistent jobs.")
    atexit.register(lambda: scheduler.shutdown())
    return scheduler


async def setup_bot():
    """Configure and setup the bot with all handlers"""
    # Create bot application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    async def handle_message(update, context):
        text = update.message.text if update.message else ""
        handler = registry.find_handler(text)
        if handler:
            await registry.execute_with_middlewares(handler, update, context)
            return
        if "withdraw" in context.user_data:
            await withdrawal_handler.handle_withdraw_free_text(update, context)
        else:
            await update.message.reply_text("❓ Invalid command")
    
    # Register command handlers (explicit)
    app.add_handler(CommandHandler("start", account_handler.handle_start))
    app.add_handler(CommandHandler("deposit", deposit_handler.handle_deposit))
    app.add_handler(CommandHandler("balance", account_handler.handle_balance))
    app.add_handler(CommandHandler("withdraw", withdrawal_handler.handle_withdraw))
    app.add_handler(CommandHandler("referral", referral_handler.handle_referral))
    app.add_handler(CommandHandler("history", account_handler.handle_history))
    app.add_handler(CommandHandler("help", info_handler.handle_help))
    app.add_handler(CommandHandler("about", info_handler.handle_about))
    app.add_handler(CommandHandler("support", info_handler.handle_support))
    app.add_handler(CommandHandler("faq", info_handler.handle_faq))
    app.add_handler(CommandHandler("main", common_handler.back_to_main_menu))
    
    # Register free-text message router
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register callback query handlers
    app.add_handler(CallbackQueryHandler(account_handler.handle_history_pagination, pattern=r"^history_(?:all|deposits|withdrawals)_page_\d+$"))
    app.add_handler(CallbackQueryHandler(info_handler.handle_referral_info, pattern=r"^referral_info$"))
    
    # Error handler
    # app.add_error_handler(common_handler.handle_error)
    
    return app

async def main():
    # Initialize DB
    init_database()
    
    # Start scheduler
    # start_scheduler()
    
    # Setup bot
    app = await setup_bot()
    
    # Use context manager for proper initialization
    async with app:
        logger.info("[Main] Bot is running...")
        await app.start()
        await app.updater.start_polling()
        
        # Keep the bot running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("[Main] Received interrupt signal, shutting down...")
        finally:
            logger.info("[Main] Bot stopped.")

def run_bot():
    """Entry point to run the bot"""
    logger.info("[Main] Starting bot...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("[Main] Bot interrupted by user.")
    except Exception as e:
        logger.error(f"[Main] Unexpected error: {e}")
        raise

if __name__ == "__main__":
    logger.info("[Main] Running main...")
    run_bot()