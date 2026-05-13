"""Root test fixtures for the LunchTogether integration test suite.

Isolation strategy: create all tables fresh per test function, then drop them
at teardown. Every test gets its own async engine so there is no event-loop
cross-scope sharing between fixtures and test functions (a common problem with
pytest-asyncio 1.x on Windows where ProactorEventLoop IOCP handles are
loop-bound).
"""

import asyncio
import os
import sys
from collections.abc import AsyncGenerator
from decimal import Decimal

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

# ---------------------------------------------------------------------------
# Windows fix: SelectorEventLoop avoids asyncpg IOCP handle cross-loop errors.
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ---------------------------------------------------------------------------
# Override settings BEFORE any app module is imported so the test DB URL and
# secret key are picked up by the Settings singleton.
# ---------------------------------------------------------------------------
os.environ.setdefault("TEST_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/lunchtogether_test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("UPLOAD_DIR", "/tmp/lunchtogether-uploads")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("SMTP_HOST", "")

TEST_DB_URL = os.environ["TEST_DATABASE_URL"]
# Point the main DATABASE_URL setting at the test DB so the app engine uses it.
os.environ["DATABASE_URL"] = TEST_DB_URL

from app.core.permissions import GROUP_ROLE_PRESETS  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.database import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base, Group, Order, Restaurant, User  # noqa: E402
from app.models.enums import (  # noqa: E402
    GroupRole,
    OrderStatus,  # noqa: E402
    PermissionType,
    UserRole,
)
from app.repositories.group import (  # noqa: E402
    GroupMemberPermissionRepository,
    GroupMemberRepository,
    GroupRepository,
)
from app.repositories.order import OrderItemRepository, OrderRepository  # noqa: E402
from app.repositories.restaurant import RestaurantRepository  # noqa: E402
from app.repositories.user import UserRepository  # noqa: E402
from app.schemas.internal import (  # noqa: E402
    GroupMemberInternalCreate,
    OrderInternalCreate,
    OrderItemInternalCreate,
    RestaurantInternalCreate,
    UserInternalCreate,
)
from app.workflows.group.create import CreateGroupInput, CreateGroupWorkflow  # noqa: E402

# ---------------------------------------------------------------------------
# Per-test engine, schema, and session
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create a fresh async engine per test, create all tables, drop them after."""
    eng = create_async_engine(TEST_DB_URL, echo=False, pool_pre_ping=True)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def db(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a function-scoped AsyncSession for direct DB assertions and factory helpers."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an AsyncClient wired to the FastAPI app with the test DB session."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db
    # Use https://testserver so secure=True cookies are retained by httpx.
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://testserver") as ac:
        yield ac
    app.dependency_overrides.pop(get_db, None)


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------


async def _make_user(
    db: AsyncSession,
    email: str,
    password: str = "password123",
    full_name: str = "Test User",
    role: str = UserRole.USER,
    is_active: bool = True,
) -> User:
    repo = UserRepository(db)
    user = await repo.create(
        UserInternalCreate(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role=role,
            is_active=is_active,
        )
    )
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
def factory_user(db: AsyncSession):
    """Factory: creates and persists a User. Call as `await factory_user(email=...)`."""

    async def _factory(
        email: str,
        password: str = "password123",
        full_name: str = "Test User",
        role: str = UserRole.USER,
        is_active: bool = True,
    ) -> User:
        return await _make_user(db, email, password, full_name, role, is_active)

    return _factory


@pytest.fixture
def factory_group(db: AsyncSession):
    """Factory: creates a Group owned by `owner` with full admin permissions."""

    async def _factory(owner: User, name: str = "Test Group") -> Group:
        group_repo = GroupRepository(db)
        member_repo = GroupMemberRepository(db)
        perm_repo = GroupMemberPermissionRepository(db)
        workflow = CreateGroupWorkflow(group_repo, member_repo, perm_repo)
        from app.schemas.group import GroupCreate

        result = await workflow.execute(CreateGroupInput(data=GroupCreate(name=name), current_user=owner))
        await db.commit()
        group = await group_repo.get_by_id(result.group.id)
        return group

    return _factory


@pytest.fixture
def factory_group_with_members(db: AsyncSession, factory_group, factory_user):
    """Factory: creates a group and adds extra members with the given GroupRole preset."""

    async def _factory(owner: User, members: list[tuple[User, GroupRole]]) -> Group:
        group = await factory_group(owner)
        member_repo = GroupMemberRepository(db)
        perm_repo = GroupMemberPermissionRepository(db)
        for user, role in members:
            member = await member_repo.create(GroupMemberInternalCreate(user_id=user.id, group_id=group.id))
            presets = GROUP_ROLE_PRESETS[role]
            await perm_repo.set_permissions(member.id, {pt.value: level for pt, level in presets.items()})
        await db.commit()
        return group

    return _factory


@pytest.fixture
def factory_restaurant(db: AsyncSession):
    """Factory: creates a Restaurant in the given group."""

    async def _factory(group: Group, name: str = "Test Restaurant") -> Restaurant:
        repo = RestaurantRepository(db)
        restaurant = await repo.create(RestaurantInternalCreate(name=name, group_id=group.id))
        await db.commit()
        return restaurant

    return _factory


@pytest.fixture
def factory_order(db: AsyncSession):
    """Factory: creates an Order (INITIATED) with optional items.

    items: list of (user, name, price) tuples.
    """

    async def _factory(
        group: Group,
        initiator: User,
        restaurant: Restaurant | None = None,
        items: list[tuple[User, str, Decimal]] | None = None,
    ) -> Order:
        order_repo = OrderRepository(db)
        item_repo = OrderItemRepository(db)
        order = await order_repo.create(
            OrderInternalCreate(
                group_id=group.id,
                initiator_id=initiator.id,
                restaurant_id=restaurant.id if restaurant else None,
                restaurant_name=restaurant.name if restaurant else None,
                status=OrderStatus.INITIATED,
            )
        )
        if items:
            for user, name, price in items:
                await item_repo.create(
                    OrderItemInternalCreate(
                        order_id=order.id,
                        user_id=user.id,
                        name=name,
                        price=price,
                        quantity=1,
                    )
                )
        await db.commit()
        await db.refresh(order)
        return order

    return _factory


@pytest.fixture
def mock_email(monkeypatch):
    """Stub email sending so invitation tests don't need SMTP."""

    async def _noop(*args, **kwargs):
        pass

    monkeypatch.setattr("app.core.email.EmailService.send_invitation_email", _noop)


# ---------------------------------------------------------------------------
# Authenticated clients
# ---------------------------------------------------------------------------


@pytest.fixture
def auth_client(client: AsyncClient):
    """Return a factory that logs in as the given user and returns a client with the cookie set."""

    async def _factory(user: User, password: str = "password123") -> AsyncClient:
        resp = await client.post("/api/auth/login", json={"email": user.email, "password": password})
        assert resp.status_code == 200, f"Login failed for {user.email}: {resp.text}"
        return client

    return _factory


@pytest.fixture
def admin_client(client: AsyncClient):
    """Return a factory that logs in as an admin user and returns a client with the cookie set."""

    async def _factory(user: User, password: str = "password123") -> AsyncClient:
        resp = await client.post("/api/auth/login", json={"email": user.email, "password": password})
        assert resp.status_code == 200, f"Admin login failed for {user.email}: {resp.text}"
        return client

    return _factory


# ---------------------------------------------------------------------------
# Convenience: set permissions on a group member directly
# ---------------------------------------------------------------------------


async def set_member_permission(
    db: AsyncSession,
    group: Group,
    user: User,
    permission_type: PermissionType,
    level: str,
) -> None:
    """Helper: update a single permission for a user in a group."""
    member_repo = GroupMemberRepository(db)
    perm_repo = GroupMemberPermissionRepository(db)
    membership = await member_repo.get_membership(user.id, group.id)
    assert membership is not None, f"User {user.email} is not a member of group {group.id}"
    await perm_repo.set_permissions(membership.id, {permission_type.value: level})
    await db.commit()
