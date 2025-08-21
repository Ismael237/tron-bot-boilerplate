from .handler import WithdrawalHandler
from .service import WithdrawalService

withdrawal_service = WithdrawalService()
withdrawal_handler = WithdrawalHandler(withdrawal_service)
