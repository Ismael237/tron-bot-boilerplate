# Import deposit handler
from .handler import DepositHandler
from .service import DepositService

# Create service instance
deposit_service = DepositService()

# Create handler instance
deposit_handler = DepositHandler(deposit_service)
