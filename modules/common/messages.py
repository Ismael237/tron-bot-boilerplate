# Common message builders (MarkdownV2 strings)
# Keep only messages that are used across multiple domains/handlers.

def msg_not_registered_prompt_start() -> str:
    """Generic prompt asking the user to register first."""
    return "\u2757 *You are not registered\\.* Use /start to register\\."


def msg_user_not_found() -> str:
    """Generic user-not-found message for callbacks/paginations."""
    return "User not found\\."