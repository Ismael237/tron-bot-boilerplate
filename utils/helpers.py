from datetime import datetime, timezone
import random
import string
from utils.telegram.message_formatter import escape_markdown_v2

def generate_referral_code(length: int = 8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_share_link(bot_username: str, referral_code: str):
    return f"https://t.me/{bot_username}?start={referral_code}"

def get_utc_time():
    return datetime.now(timezone.utc)

def get_utc_date():
    return get_utc_time().date()

def get_separator():
    from utils.constants import SEPARATOR
    return SEPARATOR