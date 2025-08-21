from typing import List, Dict, Optional

from shared.base_service import BaseService
from database.models import User, ReferralCommission, CommissionStatus


class ReferralService(BaseService):
    """Referral module service: fetch referrals and summarize commissions."""

    def get_user_by_telegram(self, telegram_id: str) -> Optional[User]:  # type: ignore[override]
        return super().get_user_by_telegram(telegram_id)

    def get_direct_referrals(self, user_id: int) -> List[User]:
        with self.db() as session:
            return session.query(User).filter(User.sponsor_id == user_id).all()

    def summarize_commissions(self, user_id: int) -> Dict[str, float]:
        with self.db() as session:
            paid = (
                session.query(ReferralCommission)
                .filter(
                    ReferralCommission.user_id == user_id,
                    ReferralCommission.status == CommissionStatus.paid,
                )
                .all()
            )
            pending = (
                session.query(ReferralCommission)
                .filter(
                    ReferralCommission.user_id == user_id,
                    ReferralCommission.status == CommissionStatus.pending,
                )
                .all()
            )
        total_paid = float(sum(c.amount_trx for c in paid)) if paid else 0.0
        total_pending = float(sum(c.amount_trx for c in pending)) if pending else 0.0
        return {"total_paid": total_paid, "total_pending": total_pending}


referral_service = ReferralService()