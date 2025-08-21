# Backward-compat shim: import from new specialized modules
from utils.crypto.address_validator import is_valid_tron_address
from utils.data.validators import is_valid_amount

__all__ = ["is_valid_tron_address", "is_valid_amount"]