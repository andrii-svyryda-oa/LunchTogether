"""Integration tests for the authentication endpoints (§6.4.1 — 11 tests)."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/register",
            json={"email": "alice@example.com", "password": "password123", "full_name": "Alice"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "alice@example.com"
        assert data["full_name"] == "Alice"
        assert data["role"] == "user"
        assert data["is_active"] is True

    async def test_register_duplicate_email(self, client: AsyncClient, factory_user):
        await factory_user(email="bob@example.com")
        resp = await client.post(
            "/api/auth/register",
            json={"email": "bob@example.com", "password": "password123", "full_name": "Bob"},
        )
        assert resp.status_code == 409

    async def test_register_password_too_short(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/register",
            json={"email": "carol@example.com", "password": "short", "full_name": "Carol"},
        )
        assert resp.status_code == 422

    async def test_register_invalid_email(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/register",
            json={"email": "not-an-email", "password": "password123", "full_name": "Dave"},
        )
        assert resp.status_code == 422


class TestLogin:
    async def test_login_success_sets_cookie(self, client: AsyncClient, factory_user):
        await factory_user(email="user@example.com", password="password123")
        resp = await client.post("/api/auth/login", json={"email": "user@example.com", "password": "password123"})
        assert resp.status_code == 200
        # Cookie must be present with security attributes
        set_cookie = resp.headers.get("set-cookie", "")
        assert "access_token" in set_cookie
        assert "HttpOnly" in set_cookie
        assert "SameSite=lax" in set_cookie

    async def test_login_wrong_password(self, client: AsyncClient, factory_user):
        await factory_user(email="user2@example.com", password="password123")
        resp = await client.post("/api/auth/login", json={"email": "user2@example.com", "password": "wrongpass"})
        assert resp.status_code == 401

    async def test_login_unknown_email(self, client: AsyncClient):
        resp = await client.post("/api/auth/login", json={"email": "ghost@example.com", "password": "password123"})
        assert resp.status_code == 401

    async def test_login_inactive_user(self, client: AsyncClient, factory_user):
        await factory_user(email="inactive@example.com", password="password123", is_active=False)
        resp = await client.post("/api/auth/login", json={"email": "inactive@example.com", "password": "password123"})
        assert resp.status_code == 401


class TestMe:
    async def test_me_authenticated(self, client: AsyncClient, factory_user, auth_client):
        user = await factory_user(email="me@example.com")
        ac = await auth_client(user)
        resp = await ac.get("/api/auth/me")
        assert resp.status_code == 200
        assert resp.json()["email"] == "me@example.com"

    async def test_me_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401


class TestLogout:
    async def test_logout_clears_cookie(self, client: AsyncClient, factory_user, auth_client):
        user = await factory_user(email="logout@example.com")
        ac = await auth_client(user)
        resp = await ac.post("/api/auth/logout")
        assert resp.status_code == 200
        # After logout the /me endpoint must reject
        resp2 = await ac.get("/api/auth/me")
        assert resp2.status_code == 401
