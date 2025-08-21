import re
import datetime
from decimal import Decimal

from utils.constants import SEPARATOR


def escape_markdown_v2(text: str) -> str:
    """Escape Markdown V2 characters."""
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text


def format_amount(amount: float | Decimal, unit: str = "TRX", decimals: int = 2) -> str:
    return f"{float(amount):.{decimals}f} {unit}"


def format_trx(amount: float | Decimal, decimals: int = 2) -> str:
    """Format a numeric amount as TRX with the given decimal precision.

    This function mirrors existing call sites that expect a TRX-specific formatter.
    """
    return format_amount(amount, unit="TRX", decimals=decimals)


def format_trx_escaped(amount: float | Decimal, decimals: int = 2) -> str:
    """Format TRX and escape markdown for safe Telegram display."""
    return escape_markdown_v2(format_trx(amount, decimals))


def format_date(dt: datetime.datetime | None) -> str:
    return dt.strftime("%Y-%m-%d") if dt else "-"


def format_time(dt: datetime.datetime | None) -> str:
    return dt.strftime("%H:%M:%S") if dt else "-"


def format_datetime(dt: datetime.datetime | None) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "-"

def get_separator() -> str:
    return SEPARATOR
