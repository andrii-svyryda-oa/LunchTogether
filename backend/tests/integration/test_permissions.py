"""Integration tests for permission enforcement (§6.4.5 — 8 tests)."""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import (
    AnalyticsScope,
    BalancesScope,
    GroupRole,
    MembersScope,
    OrdersScope,
    PermissionType,
    UserRole,
)
from tests.conftest import set_member_permission


class TestMembersPermission:
    async def test_update_member_requires_members_editor(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, auth_client, db
    ):
        owner = await factory_user(email="perm_own@example.com")
        viewer = await factory_user(email="perm_viewer@example.com")
        target = await factory_user(email="perm_target@example.com")
        group = await factory_group_with_members(owner, [(viewer, GroupRole.SUPERVISOR_MEMBER), (target, GroupRole.MEMBER)])
        # Supervisor member has MembersScope.VIEWER — not editor
        ac = await auth_client(viewer)
        resp = await ac.patch(
            f"/api/groups/{group.id}/members/{target.id}",
            json={"role": "member"},
        )
        assert resp.status_code == 403

    async def test_members_editor_can_update_member(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, auth_client, db
    ):
        owner = await factory_user(email="perm_meditor@example.com")
        editor = await factory_user(email="perm_meditoruser@example.com")
        target = await factory_user(email="perm_target2@example.com")
        group = await factory_group_with_members(owner, [(editor, GroupRole.MEMBER), (target, GroupRole.MEMBER)])
        # Elevate editor's members permission to EDITOR
        await set_member_permission(db, group, editor, PermissionType.MEMBERS, MembersScope.EDITOR)

        ac = await auth_client(editor)
        resp = await ac.patch(
            f"/api/groups/{group.id}/members/{target.id}",
            json={"role": "supervisor_member"},
        )
        assert resp.status_code == 200

    async def test_member_preset_applied_on_accept(
        self, client: AsyncClient, factory_user, factory_group, auth_client, mock_email
    ):
        owner = await factory_user(email="preset_own@example.com")
        invitee = await factory_user(email="preset_invitee@example.com")
        group = await factory_group(owner)
        ac_owner = await auth_client(owner)
        inv_resp = await ac_owner.post(f"/api/groups/{group.id}/invitations", json={"email": invitee.email})
        token = inv_resp.json()["token"]

        ac_invitee = await auth_client(invitee)
        await ac_invitee.post(f"/api/groups/invitations/{token}/accept")

        # Now check that the MEMBER preset was applied
        resp = await ac_owner.get(f"/api/groups/{group.id}/members")
        members = resp.json()
        new_member = next(m for m in members if m["user_id"] == str(invitee.id))
        perm_dict = {p["permission_type"]: p["level"] for p in new_member["permissions"]}
        assert perm_dict.get("orders") == "participant"
        assert perm_dict.get("balances") == "none"
        assert perm_dict.get("analytics") == "none"

    async def test_remove_other_member_as_editor(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, auth_client, db
    ):
        owner = await factory_user(email="rem_own@example.com")
        editor = await factory_user(email="rem_editor@example.com")
        target = await factory_user(email="rem_target@example.com")
        group = await factory_group_with_members(owner, [(editor, GroupRole.MEMBER), (target, GroupRole.MEMBER)])
        await set_member_permission(db, group, editor, PermissionType.MEMBERS, MembersScope.EDITOR)

        ac = await auth_client(editor)
        resp = await ac.delete(f"/api/groups/{group.id}/members/{target.id}")
        assert resp.status_code == 200


class TestOrdersPermission:
    async def test_orders_editor_can_transition_others_order(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, factory_order, auth_client, db
    ):
        owner = await factory_user(email="ord_own@example.com")
        initiator = await factory_user(email="ord_initiator@example.com")
        editor = await factory_user(email="ord_editor@example.com")
        group = await factory_group_with_members(
            owner, [(initiator, GroupRole.SUPERVISOR_MEMBER), (editor, GroupRole.MEMBER)]
        )
        await set_member_permission(db, group, editor, PermissionType.ORDERS, OrdersScope.EDITOR)

        order = await factory_order(group, initiator)
        # editor transitions to confirmed even though they are not the initiator
        ac = await auth_client(editor)
        resp = await ac.post(
            f"/api/groups/{group.id}/orders/{order.id}/status",
            json={"status": "confirmed"},
        )
        assert resp.status_code == 200


class TestBalancesPermission:
    async def test_balances_viewer_can_list_but_not_adjust(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, auth_client, db
    ):
        owner = await factory_user(email="bal_own@example.com")
        viewer = await factory_user(email="bal_viewer@example.com")
        group = await factory_group_with_members(owner, [(viewer, GroupRole.SUPERVISOR_MEMBER)])
        # SUPERVISOR_MEMBER gets BALANCES=viewer by default

        ac = await auth_client(viewer)
        # List OK
        resp = await ac.get(f"/api/groups/{group.id}/balances")
        assert resp.status_code == 200

        # Adjust denied
        resp2 = await ac.post(
            f"/api/groups/{group.id}/balances/adjust",
            json={"user_id": str(owner.id), "amount": "10.00", "note": "test"},
        )
        assert resp2.status_code == 403


class TestAnalyticsPermission:
    async def test_analytics_none_returns_403(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, auth_client, db
    ):
        owner = await factory_user(email="ana_own@example.com")
        member = await factory_user(email="ana_member@example.com")
        group = await factory_group_with_members(owner, [(member, GroupRole.MEMBER)])
        # MEMBER has analytics=none

        ac = await auth_client(member)
        resp = await ac.get(f"/api/groups/{group.id}/analytics")
        assert resp.status_code == 403
