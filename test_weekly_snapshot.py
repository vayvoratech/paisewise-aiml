from datetime import date

from app.repositories.holdings_repository import (
    HoldingsRepository,
)
from app.services.portfolio_analytics_snapshot_service import (
    PortfolioAnalyticsSnapshotService,
)


holdings_repository = HoldingsRepository()
snapshot_service = PortfolioAnalyticsSnapshotService()

user_ids = (
    holdings_repository
    .get_users_with_more_than_two_holdings()
)

print("Users with more than 2 holdings:")
print(user_ids)

for user_id in user_ids:
    snapshot_service.create_snapshot(
        user_id=user_id,
        snapshot_date=date.today(),
    )

print("Weekly portfolio analytics snapshots saved.")