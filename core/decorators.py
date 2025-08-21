from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Iterable, Optional, Tuple
import time
import functools

from utils.logger import logger
from config import TELEGRAM_ADMIN_ID
from telegram.constants import ChatAction

Handler = Callable[..., Awaitable[Any]]


def handle_errors(error_message: str = "❌ An unexpected error occurred") -> Callable[[Handler], Handler]:
    """Decorator that catches exceptions and replies with a generic message.

    Logs the exception with the function name.
    """

    def decorator(func: Handler) -> Handler:
        @functools.wraps(func)
        async def wrapper(update, context):  # type: ignore[misc]
            try:
                return await func(update, context)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                # Try to notify the user gracefully
                try:
                    if getattr(update, "message", None):
                        await update.message.reply_text(error_message)
                    elif getattr(update, "callback_query", None):
                        await update.callback_query.message.reply_text(error_message)
                except Exception:
                    pass
                return None

        return wrapper  # type: ignore[return-value]

    return decorator


def _parse_admin_ids_from_env() -> Tuple[int, ...]:
    """Parse TELEGRAM_ADMIN_ID which may contain one or multiple comma-separated IDs."""
    if not TELEGRAM_ADMIN_ID:
        return tuple()
    raw = str(TELEGRAM_ADMIN_ID)
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    ids: Tuple[int, ...] = tuple(int(p) for p in parts)
    return ids


def require_admin(admin_ids: Optional[Iterable[int]] = None) -> Callable[[Handler], Handler]:
    """Decorator that ensures the caller is an admin user.

    If admin_ids is None, falls back to TELEGRAM_ADMIN_ID from config (single or CSV list).
    """

    # Normalize configured admin(s)
    fallback_ids: Tuple[int, ...] = _parse_admin_ids_from_env()
    allowed: Tuple[int, ...] = tuple(admin_ids) if admin_ids is not None else fallback_ids

    def _decorator(func: Handler) -> Handler:
        @functools.wraps(func)
        async def _wrapper(update, context):  # type: ignore[misc]
            user_id = getattr(getattr(update, "effective_user", None), "id", None)
            if user_id is None or (allowed and user_id not in allowed):
                if getattr(update, "message", None):
                    await update.message.reply_text("❌ Access denied")
                return None
            return await func(update, context)

        return _wrapper  # type: ignore[return-value]

    return _decorator


def typing_action(func: Handler) -> Handler:
    """Decorator that displays the typing action while the handler runs."""

    @functools.wraps(func)
    async def _wrapper(update, context):  # type: ignore[misc]
        try:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action=ChatAction.TYPING,
            )
        except Exception:
            # Do not block the handler if sending chat action fails
            pass
        return await func(update, context)

    return _wrapper  # type: ignore[return-value]


def cache_result(duration: float = 300.0) -> Callable[[Handler], Handler]:
    """Cache async handler results in-memory for `duration` seconds.

    The cache key is built from positional and keyword args string representation.
    Suitable for idempotent read handlers.
    """

    def _decorator(func: Handler) -> Handler:
        cache: Dict[str, Tuple[Any, float]] = {}

        @functools.wraps(func)
        async def _wrapper(*args, **kwargs):  # type: ignore[misc]
            key = f"{args!r}|{kwargs!r}"
            if key in cache:
                result, ts = cache[key]
                if (time.time() - ts) < duration:
                    return result
            result = await func(*args, **kwargs)
            cache[key] = (result, time.time())
            return result

        return _wrapper  # type: ignore[return-value]

    return _decorator