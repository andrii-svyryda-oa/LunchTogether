from fastapi import APIRouter

from app.api.analytics import router as analytics_router
from app.api.auth import router as auth_router
from app.api.balances import router as balances_router
from app.api.groups import router as groups_router
from app.api.orders import router as orders_router
from app.api.restaurants import router as restaurants_router
from app.api.users import router as users_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(groups_router)
api_router.include_router(restaurants_router)
api_router.include_router(orders_router)
api_router.include_router(balances_router)
api_router.include_router(analytics_router)
