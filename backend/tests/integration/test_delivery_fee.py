"""Integration tests for delivery fee calculation (§6.4.8 — 6 tests)."""

from decimal import Decimal

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import GroupRole
from app.repositories.balance import BalanceRepository


async def _transition(ac: AsyncClient, group_id, order_id, status: str):
    return await ac.post(f"/api/groups/{group_id}/orders/{order_id}/status", json={"status": status})


class TestDeliveryFeeCalculation:
    async def test_set_total_splits_to_per_person(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, factory_order, auth_client, db
    ):
        owner = await factory_user(email="fee_total_own@example.com")
        member = await factory_user(email="fee_total_mem@example.com")
        group = await factory_group_with_members(owner, [(member, GroupRole.MEMBER)])
        order = await factory_order(
            group, owner, items=[(owner, "Dish A", Decimal("10.00")), (member, "Dish B", Decimal("8.00"))]
        )
        ac = await auth_client(owner)
        resp = await ac.post(
            f"/api/groups/{group.id}/orders/{order.id}/delivery-fee",
            json={"delivery_fee_total": "6.00"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert Decimal(data["delivery_fee_total"]) == Decimal("6.00")
        # 6.00 / 2 participants = 3.00
        assert Decimal(data["delivery_fee_per_person"]) == Decimal("3.00")

    async def test_set_per_person_multiplies_to_total(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, factory_order, auth_client, db
    ):
        owner = await factory_user(email="fee_pp_own@example.com")
        member = await factory_user(email="fee_pp_mem@example.com")
        group = await factory_group_with_members(owner, [(member, GroupRole.MEMBER)])
        order = await factory_order(
            group, owner, items=[(owner, "Item A", Decimal("5.00")), (member, "Item B", Decimal("5.00"))]
        )
        ac = await auth_client(owner)
        resp = await ac.post(
            f"/api/groups/{group.id}/orders/{order.id}/delivery-fee",
            json={"delivery_fee_per_person": "2.50"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert Decimal(data["delivery_fee_per_person"]) == Decimal("2.50")
        # 2.50 * 2 participants = 5.00
        assert Decimal(data["delivery_fee_total"]) == Decimal("5.00")

    async def test_cannot_set_fee_on_finished_order(
        self, client: AsyncClient, factory_user, factory_group, factory_order, auth_client
    ):
        owner = await factory_user(email="fee_fin_own@example.com")
        group = await factory_group(owner)
        order = await factory_order(group, owner)
        ac = await auth_client(owner)
        await _transition(ac, group.id, order.id, "confirmed")
        await _transition(ac, group.id, order.id, "ordered")
        await _transition(ac, group.id, order.id, "finished")

        resp = await ac.post(
            f"/api/groups/{group.id}/orders/{order.id}/delivery-fee",
            json={"delivery_fee_total": "5.00"},
        )
        assert resp.status_code == 422

    async def test_fee_included_in_finish_debit(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, factory_order, auth_client, db
    ):
        owner = await factory_user(email="fee_debit_own@example.com")
        group = await factory_group(owner)
        order = await factory_order(group, owner, items=[(owner, "Pasta", Decimal("10.00"))])
        ac = await auth_client(owner)

        # Set 2 total fee → 2 per person (only 1 participant)
        await ac.post(
            f"/api/groups/{group.id}/orders/{order.id}/delivery-fee",
            json={"delivery_fee_total": "2.00"},
        )
        await _transition(ac, group.id, order.id, "confirmed")
        await _transition(ac, group.id, order.id, "ordered")
        await _transition(ac, group.id, order.id, "finished")

        bal_repo = BalanceRepository(db)
        balance = await bal_repo.get_or_create(owner.id, group.id)
        await db.refresh(balance)
        # 10.00 item + 2.00 delivery = 12.00 deducted
        assert balance.amount == Decimal("-12.00")

    async def test_rounding_quantize_to_two_decimal_places(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, factory_order, auth_client, db
    ):
        """Splitting 10.00 / 3 = 3.333... should be stored as 3.33."""
        owner = await factory_user(email="fee_round_own@example.com")
        m1 = await factory_user(email="fee_round_m1@example.com")
        m2 = await factory_user(email="fee_round_m2@example.com")
        group = await factory_group_with_members(owner, [(m1, GroupRole.MEMBER), (m2, GroupRole.MEMBER)])
        order = await factory_order(
            group,
            owner,
            items=[
                (owner, "Item O", Decimal("5.00")),
                (m1, "Item 1", Decimal("5.00")),
                (m2, "Item 2", Decimal("5.00")),
            ],
        )
        ac = await auth_client(owner)
        resp = await ac.post(
            f"/api/groups/{group.id}/orders/{order.id}/delivery-fee",
            json={"delivery_fee_total": "10.00"},
        )
        assert resp.status_code == 200
        per_person = Decimal(resp.json()["delivery_fee_per_person"])
        # Should be quantized to 2 decimal places
        assert per_person == per_person.quantize(Decimal("0.01"))
        assert per_person == Decimal("3.33")
