"""Integration tests for user management endpoints."""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import UserRole


class TestListUsers:
    async def test_list_users_admin_ok(self, client: AsyncClient, factory_user, auth_client):
        admin = await factory_user(email="admin@example.com", role=UserRole.ADMIN)
        await factory_user(email="u1@example.com")
        ac = await auth_client(admin)
        resp = await ac.get("/api/users")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert data["total"] >= 2

    async def test_list_users_non_admin_forbidden(self, client: AsyncClient, factory_user, auth_client):
        user = await factory_user(email="regular@example.com")
        ac = await auth_client(user)
        resp = await ac.get("/api/users")
        assert resp.status_code == 403


class TestCreateUser:
    async def test_admin_can_create_user(self, client: AsyncClient, factory_user, auth_client):
        admin = await factory_user(email="admin2@example.com", role=UserRole.ADMIN)
        ac = await auth_client(admin)
        resp = await ac.post(
            "/api/users",
            json={"email": "newuser@example.com", "password": "password123", "full_name": "New User"},
        )
        assert resp.status_code == 201
        assert resp.json()["email"] == "newuser@example.com"


class TestUpdateUser:
    async def test_patch_own_profile(self, client: AsyncClient, factory_user, auth_client):
        user = await factory_user(email="patchme@example.com")
        ac = await auth_client(user)
        resp = await ac.patch(f"/api/users/{user.id}", json={"full_name": "Updated Name"})
        assert resp.status_code == 200
        assert resp.json()["full_name"] == "Updated Name"

    async def test_patch_other_user_as_regular_forbidden(self, client: AsyncClient, factory_user, auth_client):
        user = await factory_user(email="patcher@example.com")
        target = await factory_user(email="target@example.com")
        ac = await auth_client(user)
        resp = await ac.patch(f"/api/users/{target.id}", json={"full_name": "Sneaky"})
        assert resp.status_code == 403

    async def test_admin_put_updates_role_and_is_active(self, client: AsyncClient, factory_user, auth_client):
        admin = await factory_user(email="admin3@example.com", role=UserRole.ADMIN)
        target = await factory_user(email="promote@example.com")
        ac = await auth_client(admin)
        resp = await ac.put(f"/api/users/{target.id}/admin", json={"role": "admin", "is_active": True})
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "admin"

