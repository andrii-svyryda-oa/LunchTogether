import uuid

from pydantic import BaseModel, ConfigDict

from app.models.user import User
from app.repositories.order import FavoriteDishRepository
from app.schemas.order import FavoriteDishResponse


class ListFavoritesInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    restaurant_id: uuid.UUID
    current_user: User


class ListFavoritesOutput(BaseModel):
    favorites: list[FavoriteDishResponse]


class ListFavoritesWorkflow:
    def __init__(self, favorite_dish_repository: FavoriteDishRepository):
        self.favorite_dish_repository = favorite_dish_repository

    async def execute(self, input_data: ListFavoritesInput) -> ListFavoritesOutput:
        favorites = await self.favorite_dish_repository.get_favorites_for_user(
            input_data.current_user.id, input_data.restaurant_id
        )
        return ListFavoritesOutput(
            favorites=[
                FavoriteDishResponse(
                    id=f.id,
                    user_id=f.user_id,
                    dish_id=f.dish_id,
                    dish_name=f.dish.name if f.dish else None,
                    dish_detail=f.dish.detail if f.dish else None,
                    dish_price=f.dish.price if f.dish else None,
                    restaurant_id=f.dish.restaurant_id if f.dish else None,
                )
                for f in favorites
            ]
        )
