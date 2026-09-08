from datetime import date, timedelta

from app.repositories.user_repository import UserRepository
from app.services.churn_calculation_service import ChurnCalculationService
from app.services.churn_service import ChurnResponse


class ChurnBatchService:
    def __init__(
        self,
        user_repository: UserRepository | None = None,
        churn_calculation_service: ChurnCalculationService | None = None,
    ) -> None:
        self.user_repository = user_repository or UserRepository()
        self.churn_calculation_service = (
            churn_calculation_service or ChurnCalculationService()
        )

    def calculate_for_users_registered_seven_days_ago(
        self,
        today: date | None = None,
    ) -> list[ChurnResponse]:
        current_date = today or date.today()
        target_date = current_date - timedelta(days=7)

        users = self.user_repository.get_users_registered_on(
            target_date
        )

        results: list[ChurnResponse] = []

        for user in users:
            user_id = str(user["id"])

            try:
                result = self.churn_calculation_service.calculate_for_user(
                    user_id
                )
                results.append(result)
            except ValueError:
                # Skip users whose churn features are not available.
                continue

        return results