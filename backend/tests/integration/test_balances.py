"""Integration tests for the balances API (§6.4.9 — 7 tests)."""

from decimal import Decimal

from httpx import AsyncClient

from app.models.enums import GroupRole


class TestListBalances:
    async def test_viewer_can_list_balances(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, auth_client, db
    ):
        owner = await factory_user(email="bl_own@example.com")
        viewer = await factory_user(email="bl_viewer@example.com")
        group = await factory_group_with_members(owner, [(viewer, GroupRole.SUPERVISOR_MEMBER)])
        # SUPERVISOR_MEMBER has balances=viewer

        ac = await auth_client(viewer)
        resp = await ac.get(f"/api/groups/{group.id}/balances")
        assert resp.status_code == 200

    async def test_none_permission_cannot_list_balances(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, auth_client, db
    ):
        owner = await factory_user(email="bl_none_own@example.com")
        member = await factory_user(email="bl_none_mem@example.com")
        group = await factory_group_with_members(owner, [(member, GroupRole.MEMBER)])
        # MEMBER has balances=none

        ac = await auth_client(member)
        resp = await ac.get(f"/api/groups/{group.id}/balances")
        assert resp.status_code == 403


class TestMyBalance:
    async def test_any_member_can_see_own_balance(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, auth_client, db
    ):
        """Documents the looser check on /balances/me — BALANCES=none members may still see their own balance."""
        owner = await factory_user(email="me_own@example.com")
        member = await factory_user(email="me_mem@example.com")
        group = await factory_group_with_members(owner, [(member, GroupRole.MEMBER)])
        # MEMBER has balances=none but /me endpoint only checks group membership

        ac = await auth_client(member)
        resp = await ac.get(f"/api/groups/{group.id}/balances/me")
        assert resp.status_code == 200


class TestAdjustBalance:
    async def test_editor_can_adjust_balance(
        self, client: AsyncClient, factory_user, factory_group, auth_client, db
    ):
        owner = await factory_user(email="adj_own@example.com")
        target = await factory_user(email="adj_target@example.com")
        group = await factory_group(owner)
        # Add target as member
        ac = await auth_client(owner)
        await ac.post(f"/api/groups/{group.id}/members", json={"user_id": str(target.id), "role": "member"})

        resp = await ac.post(
            f"/api/groups/{group.id}/balances/adjust",
            json={"user_id": str(target.id), "amount": "20.00", "note": "manual top-up"},
        )
        assert resp.status_code == 200
        assert Decimal(resp.json()["amount"]) == Decimal("20.00")

    async def test_viewer_cannot_adjust_balance(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, auth_client, db
    ):
        owner = await factory_user(email="adjv_own@example.com")
        viewer = await factory_user(email="adjv_viewer@example.com")
        group = await factory_group_with_members(owner, [(viewer, GroupRole.SUPERVISOR_MEMBER)])

        ac = await auth_client(viewer)
        resp = await ac.post(
            f"/api/groups/{group.id}/balances/adjust",
            json={"user_id": str(owner.id), "amount": "10.00"},
        )
        assert resp.status_code == 403

    async def test_positive_and_negative_adjustments_update_amount(
        self, client: AsyncClient, factory_user, factory_group, auth_client, db
    ):
        owner = await factory_user(email="adjpn_own@example.com")
        target = await factory_user(email="adjpn_target@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)
        await ac.post(f"/api/groups/{group.id}/members", json={"user_id": str(target.id), "role": "member"})

        await ac.post(
            f"/api/groups/{group.id}/balances/adjust",
            json={"user_id": str(target.id), "amount": "50.00"},
        )
        resp = await ac.post(
            f"/api/groups/{group.id}/balances/adjust",
            json={"user_id": str(target.id), "amount": "-30.00"},
        )
        assert resp.status_code == 200
        assert Decimal(resp.json()["amount"]) == Decimal("20.00")


class TestBalanceHistory:
    async def test_history_endpoint_returns_rows(
        self, client: AsyncClient, factory_user, factory_group, auth_client, db
    ):
        owner = await factory_user(email="hist_own@example.com")
        target = await factory_user(email="hist_target@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)
        await ac.post(f"/api/groups/{group.id}/members", json={"user_id": str(target.id), "role": "member"})
        await ac.post(
            f"/api/groups/{group.id}/balances/adjust",
            json={"user_id": str(target.id), "amount": "15.00", "note": "test adjust"},
        )
        resp = await ac.get(f"/api/groups/{group.id}/balances/{target.id}/history")
        assert resp.status_code == 200
        rows = resp.json()
        assert len(rows) >= 1
        assert rows[0]["change_type"] == "manual"

    async def test_history_for_nonexistent_balance_returns_404(
        self, client: AsyncClient, factory_user, factory_group, auth_client
    ):
        owner = await factory_user(email="hist404_own@example.com")
        stranger = await factory_user(email="hist404_stranger@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)
        resp = await ac.get(f"/api/groups/{group.id}/balances/{stranger.id}/history")
        assert resp.status_code == 404
