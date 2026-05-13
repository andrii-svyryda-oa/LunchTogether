from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.user import User
from app.repositories.analytics import UserAnalyticsRepository
from app.schemas.analytics import UserAnalyticsResponse


class GetUserAnalyticsInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    current_user: User


class GetUserAnalyticsOutput(BaseModel):
    analytics: UserAnalyticsResponse


class GetUserAnalyticsWorkflow:
    def __init__(self, analytics_repository: UserAnalyticsRepository):
        self.analytics_repository = analytics_repository

    async def execute(self, input_data: GetUserAnalyticsInput) -> GetUserAnalyticsOutput:
        user = input_data.current_user
        repo = self.analytics_repository

        total_groups = await repo.count_groups(user.id)
        total_orders = await repo.count_orders_participated(user.id)
        total_spent = await repo.get_total_spent(user.id)
        favorite_restaurant = await repo.get_favorite_restaurant(user.id)
        total_balance = await repo.get_total_balance(user.id)

        avg_value = total_spent / Decimal(str(total_orders)) if total_orders > 0 else Decimal("0.00")

        return GetUserAnalyticsOutput(
            analytics=UserAnalyticsResponse(
                total_groups=total_groups,
                total_orders_participated=total_orders,
                total_spent=total_spent.quantize(Decimal("0.01")),
                average_order_value=avg_value.quantize(Decimal("0.01")),
                favorite_restaurant=favorite_restaurant,
                total_balance_across_groups=total_balance,
            )
        )
