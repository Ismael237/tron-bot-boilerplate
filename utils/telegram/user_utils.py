from telegram import Update


def tg_user_id(update: Update) -> int | None:
    return getattr(getattr(update, "effective_user", None), "id", None)


def tg_username(update: Update) -> str | None:
    return getattr(getattr(update, "effective_user", None), "username", None)
