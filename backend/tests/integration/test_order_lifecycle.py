"""Integration tests for the order lifecycle (§6.4.7 — 19 tests)."""

from decimal import Decimal

from httpx import AsyncClient

from app.models.enums import GroupRole
from app.repositories.balance import BalanceHistoryRepository, BalanceRepository

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _transition(ac: AsyncClient, group_id, order_id, status: str):
    return await ac.post(f"/api/groups/{group_id}/orders/{order_id}/status", json={"status": status})


# ---------------------------------------------------------------------------
# Create order rules
# ---------------------------------------------------------------------------


class TestCreateOrder:
    async def test_editor_can_create_order(
        self, client: AsyncClient, factory_user, factory_group, auth_client
    ):
        owner = await factory_user(email="co_own@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)
        resp = await ac.post(f"/api/groups/{group.id}/orders", json={"restaurant_name": "Pizza Hub"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "initiated"
        assert data["initiator_id"] == str(owner.id)

    async def test_initiator_scope_can_create_order(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, auth_client, db
    ):
        owner = await factory_user(email="co_init_own@example.com")
        initiator = await factory_user(email="co_initiator@example.com")
        group = await factory_group_with_members(owner, [(initiator, GroupRole.SUPERVISOR_MEMBER)])
        # SUPERVISOR_MEMBER has orders=initiator
        ac = await auth_client(initiator)
        resp = await ac.post(f"/api/groups/{group.id}/orders", json={"restaurant_name": "Noodle Bar"})
        assert resp.status_code == 201

    async def test_participant_cannot_create_order(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, auth_client, db
    ):
        owner = await factory_user(email="co_part_own@example.com")
        participant = await factory_user(email="co_participant@example.com")
        group = await factory_group_with_members(owner, [(participant, GroupRole.MEMBER)])
        # MEMBER has orders=participant — cannot create
        ac = await auth_client(participant)
        resp = await ac.post(f"/api/groups/{group.id}/orders", json={"restaurant_name": "Sushi"})
        assert resp.status_code == 403

    async def test_one_active_order_rule_enforced(
        self, client: AsyncClient, factory_user, factory_group, auth_client
    ):
        owner = await factory_user(email="one_own@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)
        r1 = await ac.post(f"/api/groups/{group.id}/orders", json={"restaurant_name": "First"})
        assert r1.status_code == 201
        r2 = await ac.post(f"/api/groups/{group.id}/orders", json={"restaurant_name": "Second"})
        assert r2.status_code == 403

    async def test_restaurant_by_name_auto_creates(
        self, client: AsyncClient, factory_user, factory_group, auth_client, db
    ):
        from app.repositories.restaurant import RestaurantRepository

        owner = await factory_user(email="autorest_own@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)
        resp = await ac.post(f"/api/groups/{group.id}/orders", json={"restaurant_name": "Brand New Place"})
        assert resp.status_code == 201
        # Verify the restaurant was auto-created
        from sqlalchemy import select

        from app.models.restaurant import Restaurant

        result = await db.execute(
            select(Restaurant).where(
                Restaurant.name == "Brand New Place", Restaurant.group_id == group.id
            )
        )
        restaurant = result.scalars().first()
        assert restaurant is not None


# ---------------------------------------------------------------------------
# Transition matrix
# ---------------------------------------------------------------------------


class TestTransitions:
    async def test_happy_path_initiated_to_finished(
        self, client: AsyncClient, factory_user, factory_group, factory_order, auth_client
    ):
        owner = await factory_user(email="happy_own@example.com")
        group = await factory_group(owner)
        order = await factory_order(group, owner)
        ac = await auth_client(owner)

        r1 = await _transition(ac, group.id, order.id, "confirmed")
        assert r1.status_code == 200
        assert r1.json()["status"] == "confirmed"

        r2 = await _transition(ac, group.id, order.id, "ordered")
        assert r2.status_code == 200

        r3 = await _transition(ac, group.id, order.id, "finished")
        assert r3.status_code == 200
        assert r3.json()["status"] == "finished"

    async def test_cancel_from_initiated(
        self, client: AsyncClient, factory_user, factory_group, factory_order, auth_client
    ):
        owner = await factory_user(email="cancel_init@example.com")
        group = await factory_group(owner)
        order = await factory_order(group, owner)
        ac = await auth_client(owner)
        resp = await _transition(ac, group.id, order.id, "cancelled")
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    async def test_cancel_from_confirmed(
        self, client: AsyncClient, factory_user, factory_group, factory_order, auth_client
    ):
        owner = await factory_user(email="cancel_conf@example.com")
        group = await factory_group(owner)
        order = await factory_order(group, owner)
        ac = await auth_client(owner)
        await _transition(ac, group.id, order.id, "confirmed")
        resp = await _transition(ac, group.id, order.id, "cancelled")
        assert resp.status_code == 200

    async def test_cancel_from_ordered(
        self, client: AsyncClient, factory_user, factory_group, factory_order, auth_client
    ):
        owner = await factory_user(email="cancel_ord@example.com")
        group = await factory_group(owner)
        order = await factory_order(group, owner)
        ac = await auth_client(owner)
        await _transition(ac, group.id, order.id, "confirmed")
        await _transition(ac, group.id, order.id, "ordered")
        resp = await _transition(ac, group.id, order.id, "cancelled")
        assert resp.status_code == 200

    async def test_illegal_skip_initiated_to_ordered(
        self, client: AsyncClient, factory_user, factory_group, factory_order, auth_client
    ):
        owner = await factory_user(email="skip_own@example.com")
        group = await factory_group(owner)
        order = await factory_order(group, owner)
        ac = await auth_client(owner)
        resp = await _transition(ac, group.id, order.id, "ordered")
        assert resp.status_code == 422

    async def test_cannot_transition_from_finished(
        self, client: AsyncClient, factory_user, factory_group, factory_order, auth_client
    ):
        owner = await factory_user(email="fromfin_own@example.com")
        group = await factory_group(owner)
        order = await factory_order(group, owner)
        ac = await auth_client(owner)
        await _transition(ac, group.id, order.id, "confirmed")
        await _transition(ac, group.id, order.id, "ordered")
        await _transition(ac, group.id, order.id, "finished")
        resp = await _transition(ac, group.id, order.id, "cancelled")
        assert resp.status_code == 422

    async def test_cannot_transition_from_cancelled(
        self, client: AsyncClient, factory_user, factory_group, factory_order, auth_client
    ):
        owner = await factory_user(email="fromcan_own@example.com")
        group = await factory_group(owner)
        order = await factory_order(group, owner)
        ac = await auth_client(owner)
        await _transition(ac, group.id, order.id, "cancelled")
        resp = await _transition(ac, group.id, order.id, "initiated")
        assert resp.status_code == 422

    async def test_non_initiator_non_editor_cannot_transition(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, factory_order, auth_client, db
    ):
        owner = await factory_user(email="nonedit_own@example.com")
        initiator = await factory_user(email="nonedit_init@example.com")
        participant = await factory_user(email="nonedit_part@example.com")
        group = await factory_group_with_members(
            owner, [(initiator, GroupRole.SUPERVISOR_MEMBER), (participant, GroupRole.MEMBER)]
        )
        order = await factory_order(group, initiator)
        ac = await auth_client(participant)
        resp = await _transition(ac, group.id, order.id, "confirmed")
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Item CRUD rules by order status
# ---------------------------------------------------------------------------


class TestItemCRUD:
    async def test_any_member_can_add_item_in_initiated(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, factory_order, auth_client, db
    ):
        owner = await factory_user(email="item_init_own@example.com")
        member = await factory_user(email="item_init_member@example.com")
        group = await factory_group_with_members(owner, [(member, GroupRole.MEMBER)])
        order = await factory_order(group, owner)
        ac = await auth_client(member)
        resp = await ac.post(
            f"/api/groups/{group.id}/orders/{order.id}/items",
            json={"name": "Pasta", "price": "8.50"},
        )
        assert resp.status_code == 201

    async def test_only_initiator_editor_can_add_item_in_confirmed(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, factory_order, auth_client, db
    ):
        owner = await factory_user(email="item_conf_own@example.com")
        participant = await factory_user(email="item_conf_part@example.com")
        group = await factory_group_with_members(owner, [(participant, GroupRole.MEMBER)])
        order = await factory_order(group, owner)
        ac_owner = await auth_client(owner)
        await _transition(ac_owner, group.id, order.id, "confirmed")

        ac_part = await auth_client(participant)
        resp = await ac_part.post(
            f"/api/groups/{group.id}/orders/{order.id}/items",
            json={"name": "Salad", "price": "5.00"},
        )
        assert resp.status_code == 403

    async def test_in_initiated_non_editor_can_only_edit_own_item(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, factory_order, auth_client, db
    ):
        owner = await factory_user(email="ownedit_own@example.com")
        member = await factory_user(email="ownedit_mem@example.com")
        group = await factory_group_with_members(owner, [(member, GroupRole.MEMBER)])
        order = await factory_order(group, owner)

        # Add an item for the owner
        ac_owner = await auth_client(owner)
        item_resp = await ac_owner.post(
            f"/api/groups/{group.id}/orders/{order.id}/items",
            json={"name": "Owner's Item", "price": "12.00"},
        )
        item_id = item_resp.json()["id"]

        # Member tries to edit owner's item
        ac_member = await auth_client(member)
        resp = await ac_member.patch(
            f"/api/groups/{group.id}/orders/{order.id}/items/{item_id}",
            json={"name": "Hacked Name"},
        )
        assert resp.status_code == 403

    async def test_cannot_add_item_to_finished_order(
        self, client: AsyncClient, factory_user, factory_group, factory_order, auth_client
    ):
        owner = await factory_user(email="fin_item_own@example.com")
        group = await factory_group(owner)
        order = await factory_order(group, owner)
        ac = await auth_client(owner)
        await _transition(ac, group.id, order.id, "confirmed")
        await _transition(ac, group.id, order.id, "ordered")
        await _transition(ac, group.id, order.id, "finished")

        resp = await ac.post(
            f"/api/groups/{group.id}/orders/{order.id}/items",
            json={"name": "Late Add", "price": "5.00"},
        )
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Balance side effects on finish
# ---------------------------------------------------------------------------


class TestFinishBalanceSideEffects:
    async def test_finishing_order_with_items_debits_balance(
        self, client: AsyncClient, factory_user, factory_group, factory_order, auth_client, db
    ):
        owner = await factory_user(email="debit_own@example.com")
        member = await factory_user(email="debit_mem@example.com")
        group = await factory_group(owner)
        from app.core.permissions import GROUP_ROLE_PRESETS
        from app.models.enums import GroupRole
        from app.repositories.group import GroupMemberPermissionRepository, GroupMemberRepository
        from app.schemas.internal import GroupMemberInternalCreate

        member_repo = GroupMemberRepository(db)
        perm_repo = GroupMemberPermissionRepository(db)
        m = await member_repo.create(GroupMemberInternalCreate(user_id=member.id, group_id=group.id))
        presets = GROUP_ROLE_PRESETS[GroupRole.MEMBER]
        await perm_repo.set_permissions(m.id, {pt.value: level for pt, level in presets.items()})
        await db.commit()

        order = await factory_order(group, owner, items=[(owner, "Pizza", Decimal("10.00"))])
        ac = await auth_client(owner)
        await _transition(ac, group.id, order.id, "confirmed")
        await _transition(ac, group.id, order.id, "ordered")
        resp = await _transition(ac, group.id, order.id, "finished")
        assert resp.status_code == 200

        # Check balance was debited for owner
        bal_repo = BalanceRepository(db)
        balance = await bal_repo.get_by_user_and_group(owner.id, group.id)
        assert balance is not None
        assert balance.amount == Decimal("-10.00")

        # Check history record
        hist_repo = BalanceHistoryRepository(db)
        histories = await hist_repo.get_history_for_balance(balance.id)
        assert any(h.change_type == "order" for h in histories)

    async def test_finishing_order_with_no_items_leaves_balances_unchanged(
        self, client: AsyncClient, factory_user, factory_group, factory_order, auth_client, db
    ):
        owner = await factory_user(email="noop_own@example.com")
        group = await factory_group(owner)
        order = await factory_order(group, owner, items=None)
        ac = await auth_client(owner)
        await _transition(ac, group.id, order.id, "confirmed")
        await _transition(ac, group.id, order.id, "ordered")
        resp = await _transition(ac, group.id, order.id, "finished")
        assert resp.status_code == 200

        # No balance record should exist
        from sqlalchemy import select

        from app.models.balance import Balance

        result = await db.execute(
            select(Balance).where(Balance.user_id == owner.id, Balance.group_id == group.id)
        )
        balance = result.scalars().first()
        assert balance is None


# ---------------------------------------------------------------------------
# Active order endpoint
# ---------------------------------------------------------------------------


class TestActiveOrder:
    async def test_active_order_returns_non_finished_order(
        self, client: AsyncClient, factory_user, factory_group, factory_order, auth_client
    ):
        owner = await factory_user(email="active_own@example.com")
        group = await factory_group(owner)
        order = await factory_order(group, owner)
        ac = await auth_client(owner)

        resp = await ac.get(f"/api/groups/{group.id}/orders/active")
        assert resp.status_code == 200
        assert resp.json() is not None
        assert resp.json()["id"] == str(order.id)

    async def test_active_order_returns_null_when_none(
        self, client: AsyncClient, factory_user, factory_group, auth_client
    ):
        owner = await factory_user(email="noactive_own@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)
        resp = await ac.get(f"/api/groups/{group.id}/orders/active")
        assert resp.status_code == 200
        assert resp.json() is None
