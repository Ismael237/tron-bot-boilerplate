import re

def is_valid_tron_address(address: str) -> bool:
    return bool(re.match(r"^T[1-9A-HJ-NP-Za-km-z]{33}$", address))
