import uuid

from pydantic import BaseModel, ConfigDict

from app.models.user import User
from app.repositories.order import FavoriteDishRepository
from app.schemas.internal import FavoriteDishInternalCreate, FavoriteDishStatusUpdate


class ToggleFavoriteInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dish_id: uuid.UUID
    current_user: User


class ToggleFavoriteOutput(BaseModel):
    is_favorite: bool
    message: str


class ToggleFavoriteWorkflow:
    def __init__(self, favorite_dish_repository: FavoriteDishRepository):
        self.favorite_dish_repository = favorite_dish_repository

    async def execute(self, input_data: ToggleFavoriteInput) -> ToggleFavoriteOutput:
        user = input_data.current_user
        existing = await self.favorite_dish_repository.get_by_user_and_dish(user.id, input_data.dish_id)
        if existing:
            new_status = not existing.is_favorite
            await self.favorite_dish_repository.update(existing.id, FavoriteDishStatusUpdate(is_favorite=new_status))
            return ToggleFavoriteOutput(
                is_favorite=new_status,
                message=f"Dish {'favorited' if new_status else 'unfavorited'}",
            )

        await self.favorite_dish_repository.create(
            FavoriteDishInternalCreate(user_id=user.id, dish_id=input_data.dish_id)
        )
        return ToggleFavoriteOutput(is_favorite=True, message="Dish favorited")
