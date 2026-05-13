"""Integration tests for analytics endpoints (§6.4.10 — 7 tests)."""

from decimal import Decimal

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import GroupRole, OrderStatus
from app.repositories.balance import BalanceRepository
from app.repositories.order import OrderRepository


async def _transition(ac: AsyncClient, group_id, order_id, status: str):
    return await ac.post(f"/api/groups/{group_id}/orders/{order_id}/status", json={"status": status})


async def _finish_order(ac: AsyncClient, group_id, order_id):
    await _transition(ac, group_id, order_id, "confirmed")
    await _transition(ac, group_id, order_id, "ordered")
    await _transition(ac, group_id, order_id, "finished")


class TestGroupAnalytics:
    async def test_analytics_requires_analytics_viewer(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, auth_client, db
    ):
        owner = await factory_user(email="ana_req_own@example.com")
        member = await factory_user(email="ana_req_mem@example.com")
        group = await factory_group_with_members(owner, [(member, GroupRole.MEMBER)])
        # MEMBER has analytics=none → 403

        ac = await auth_client(member)
        resp = await ac.get(f"/api/groups/{group.id}/analytics")
        assert resp.status_code == 403

    async def test_analytics_counts_orders_by_status(
        self, client: AsyncClient, factory_user, factory_group, factory_order, auth_client, db
    ):
        owner = await factory_user(email="ana_count_own@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)

        # 1 finished order
        o1 = await factory_order(group, owner)
        await _finish_order(ac, group.id, o1.id)

        # 1 cancelled order
        o2 = await factory_order(group, owner)
        await _transition(ac, group.id, o2.id, "cancelled")

        # 1 active (initiated)
        await factory_order(group, owner)

        resp = await ac.get(f"/api/groups/{group.id}/analytics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_orders"] == 3
        assert data["completed_orders"] == 1
        assert data["cancelled_orders"] == 1
        assert data["active_orders"] == 1

    async def test_total_spent_and_avg_on_finished_orders(
        self, client: AsyncClient, factory_user, factory_group, factory_order, auth_client, db
    ):
        owner = await factory_user(email="ana_spent_own@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)

        order = await factory_order(group, owner, items=[(owner, "Burger", Decimal("10.00"))])
        await _finish_order(ac, group.id, order.id)

        resp = await ac.get(f"/api/groups/{group.id}/analytics")
        assert resp.status_code == 200
        data = resp.json()
        assert Decimal(data["total_spent"]) == Decimal("10.00")
        assert Decimal(data["average_order_value"]) == Decimal("10.00")

    async def test_most_popular_restaurant(
        self, client: AsyncClient, factory_user, factory_group, factory_order, auth_client, db
    ):
        owner = await factory_user(email="ana_pop_own@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)

        # 2 orders from "Pizza Place", 1 from "Sushi"
        o1 = await factory_order(group, owner)
        # We can't easily set restaurant_name through factory, use API
        await _transition(ac, group.id, o1.id, "cancelled")

        # Create orders via API to set restaurant_name
        r1 = await ac.post(f"/api/groups/{group.id}/orders", json={"restaurant_name": "Pizza Place"})
        oid1 = r1.json()["id"]
        await _finish_order(ac, group.id, oid1)

        r2 = await ac.post(f"/api/groups/{group.id}/orders", json={"restaurant_name": "Pizza Place"})
        oid2 = r2.json()["id"]
        await _finish_order(ac, group.id, oid2)

        r3 = await ac.post(f"/api/groups/{group.id}/orders", json={"restaurant_name": "Sushi"})
        oid3 = r3.json()["id"]
        await _finish_order(ac, group.id, oid3)

        resp = await ac.get(f"/api/groups/{group.id}/analytics")
        assert resp.status_code == 200
        assert resp.json()["most_popular_restaurant"] == "Pizza Place"


class TestUserAnalytics:
    async def test_user_analytics_returns_groups_count(
        self, client: AsyncClient, factory_user, factory_group, auth_client
    ):
        user = await factory_user(email="ua_groups@example.com")
        await factory_group(user, name="G1")
        await factory_group(user, name="G2")
        ac = await auth_client(user)
        resp = await ac.get("/api/users/me/analytics")
        assert resp.status_code == 200
        assert resp.json()["total_groups"] == 2

    async def test_user_analytics_distinct_orders_participated(
        self, client: AsyncClient, factory_user, factory_group, factory_order, auth_client, db
    ):
        owner = await factory_user(email="ua_orders_own@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)

        o1 = await ac.post(f"/api/groups/{group.id}/orders", json={"restaurant_name": "R1"})
        oid1 = o1.json()["id"]
        await ac.post(
            f"/api/groups/{group.id}/orders/{oid1}/items",
            json={"name": "Item", "price": "5.00"},
        )
        await _finish_order(ac, group.id, oid1)

        resp = await ac.get("/api/users/me/analytics")
        assert resp.status_code == 200
        assert resp.json()["total_orders_participated"] >= 1

    async def test_user_analytics_total_balance_across_groups(
        self, client: AsyncClient, factory_user, factory_group, auth_client, db
    ):
        owner = await factory_user(email="ua_bal_own@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)

        # Create a balance via adjust
        target = owner  # adjust own balance (owner is editor of own group)
        await ac.post(
            f"/api/groups/{group.id}/balances/adjust",
            json={"user_id": str(owner.id), "amount": "25.00", "note": "topup"},
        )

        resp = await ac.get("/api/users/me/analytics")
        assert resp.status_code == 200
        assert Decimal(resp.json()["total_balance_across_groups"]) == Decimal("25.00")
