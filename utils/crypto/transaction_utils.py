from typing import Optional


try:
    from config import TRON_EXPLORER_URL
except Exception:
    TRON_EXPLORER_URL = None  # optional


def tx_link(tx_hash: str) -> Optional[str]:
    if not TRON_EXPLORER_URL or not tx_hash:
        return None
    return f"{TRON_EXPLORER_URL.rstrip('/')}/#/transaction/{tx_hash}"


def short_hash(tx_hash: str, length: int = 10) -> str:
    tx_hash = tx_hash or ""
    if len(tx_hash) <= length:
        return tx_hash
    half = max(1, length // 2)
    return f"{tx_hash[:half]}…{tx_hash[-half:]}"
