"""Integration tests for group management endpoints (§6.4.3 — 8 tests)."""

import io

from httpx import AsyncClient

from app.workflows.group.create import MAX_GROUPS_PER_USER


class TestCreateGroup:
    async def test_create_group_owner_becomes_admin_member(self, client: AsyncClient, factory_user, auth_client):
        user = await factory_user(email="owner@example.com")
        ac = await auth_client(user)
        resp = await ac.post("/api/groups", json={"name": "My Group"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "My Group"
        assert data["owner_id"] == str(user.id)

        # Verify the owner now appears in the member list with admin permissions
        group_id = data["id"]
        resp2 = await ac.get(f"/api/groups/{group_id}/members")
        assert resp2.status_code == 200
        members = resp2.json()
        assert len(members) == 1
        owner_member = members[0]
        assert owner_member["user_id"] == str(user.id)
        perm_types = {p["permission_type"] for p in owner_member["permissions"]}
        assert perm_types == {"members", "orders", "balances", "analytics", "restaurants"}

    async def test_create_group_max_groups_per_user_enforced(self, client: AsyncClient, factory_user, auth_client):
        user = await factory_user(email="toomanygroups@example.com")
        ac = await auth_client(user)
        for i in range(MAX_GROUPS_PER_USER):
            r = await ac.post("/api/groups", json={"name": f"Group {i}"})
            assert r.status_code == 201
        # The (MAX+1)-th group should be rejected
        resp = await ac.post("/api/groups", json={"name": "One Too Many"})
        assert resp.status_code == 403


class TestGetGroup:
    async def test_get_group_detail_member_ok(self, client: AsyncClient, factory_user, factory_group, auth_client):
        owner = await factory_user(email="gowner@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)
        resp = await ac.get(f"/api/groups/{group.id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == str(group.id)

    async def test_get_group_detail_non_member_forbidden(
        self, client: AsyncClient, factory_user, factory_group, auth_client
    ):
        owner = await factory_user(email="owner2@example.com")
        stranger = await factory_user(email="stranger@example.com")
        group = await factory_group(owner)
        ac = await auth_client(stranger)
        resp = await ac.get(f"/api/groups/{group.id}")
        assert resp.status_code == 403


class TestListGroups:
    async def test_list_returns_own_groups(self, client: AsyncClient, factory_user, factory_group, auth_client):
        user = await factory_user(email="listme@example.com")
        group = await factory_group(user, name="Listed Group")
        ac = await auth_client(user)
        resp = await ac.get("/api/groups")
        assert resp.status_code == 200
        ids = [g["id"] for g in resp.json()]
        assert str(group.id) in ids


class TestUpdateGroup:
    async def test_patch_group_owner_ok(self, client: AsyncClient, factory_user, factory_group, auth_client):
        owner = await factory_user(email="patchowner@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)
        resp = await ac.patch(f"/api/groups/{group.id}", json={"name": "Renamed"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Renamed"

    async def test_patch_group_non_member_forbidden(
        self, client: AsyncClient, factory_user, factory_group, auth_client
    ):
        owner = await factory_user(email="patchown2@example.com")
        stranger = await factory_user(email="stranger2@example.com")
        group = await factory_group(owner)
        ac = await auth_client(stranger)
        resp = await ac.patch(f"/api/groups/{group.id}", json={"name": "Hacked"})
        assert resp.status_code == 403


class TestUploadLogo:
    async def test_upload_logo_sets_logo_path(
        self, client: AsyncClient, factory_user, factory_group, auth_client, tmp_path, monkeypatch
    ):
        import app.core.storage as storage_module

        saved: list[str] = []

        async def fake_save_upload(file, subdirectory=""):
            path = str(tmp_path / "logo.png")
            saved.append(path)
            return path

        monkeypatch.setattr(storage_module, "save_upload", fake_save_upload)

        owner = await factory_user(email="logoowner@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)
        resp = await ac.post(
            f"/api/groups/{group.id}/logo",
            files={"file": ("logo.png", io.BytesIO(b"fake-png-content"), "image/png")},
        )
        assert resp.status_code == 200
        assert resp.json()["logo_path"] is not None


class TestDeleteGroup:
    async def test_delete_group_owner_ok(self, client: AsyncClient, factory_user, factory_group, auth_client):
        owner = await factory_user(email="delowner@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)
        resp = await ac.delete(f"/api/groups/{group.id}")
        assert resp.status_code == 200

    async def test_delete_group_non_owner_forbidden(
        self, client: AsyncClient, factory_user, factory_group, auth_client
    ):
        owner = await factory_user(email="delown2@example.com")
        member = await factory_user(email="member@example.com")
        group = await factory_group(owner)
        # Add member manually through the direct member endpoint (owner can do it)
        ac_owner = await auth_client(owner)
        await ac_owner.post(
            f"/api/groups/{group.id}/members",
            json={"user_id": str(member.id), "role": "member"},
        )
        # member tries to delete
        ac_member = await auth_client(member)
        resp = await ac_member.delete(f"/api/groups/{group.id}")
        assert resp.status_code == 403
