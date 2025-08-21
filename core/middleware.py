from __future__ import annotations

from typing import Dict, Optional
import time

from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import logger
from shared.user_service import UserService


class AuthMiddleware:
    """Authenticate user existence and attach the user object to context.

    If the user is not found, the pipeline is stopped and a message is sent.
    """

    def __init__(self, user_service: Optional[UserService] = None) -> None:
        self.user_service = user_service or UserService()

    async def before(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        # Handle only updates that have a user. For safety, allow others.
        if not update.effective_user:
            return True
        telegram_id = str(update.effective_user.id)
        user = self.user_service.get_user_by_telegram(telegram_id)
        if not user:
            if update.message:
                await update.message.reply_text("❌ User not found")
            return False
        context.user_data["user"] = user
        return True

    async def after(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        # No-op post hook to comply with pipeline interface
        return True


class LoggingMiddleware:
    """Log basic information about the incoming update before handling it."""

    async def before(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        uid = update.effective_user.id if update.effective_user else "unknown"
        text = update.message.text if getattr(update, "message", None) else None
        logger.info(f"Incoming update from {uid}: {text}")
        return True

    async def after(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        logger.info("Handler executed successfully")
        return True


class RateLimitMiddleware:
    """Simple per-user rate limiter to prevent spam.

    Blocks messages if the last one was received within `min_interval` seconds.
    """

    def __init__(self, min_interval: float = 1.0) -> None:
        self.user_last_message: Dict[int, float] = {}
        self.min_interval = float(min_interval)

    async def before(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        if not update.effective_user:
            return True
        user_id = int(update.effective_user.id)
        now = time.time()
        last = self.user_last_message.get(user_id)
        if last is not None and (now - last) < self.min_interval:
            # Too soon; silently drop or notify
            if update.message:
                await update.message.reply_text("⏳ Please slow down")
            return False
        self.user_last_message[user_id] = now
        return True

    async def after(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        return True