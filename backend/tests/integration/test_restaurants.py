"""Integration tests for restaurants and dishes (§6.4.6 — 6 tests)."""

from httpx import AsyncClient

from app.models.enums import GroupRole


class TestRestaurantCRUD:
    async def test_member_can_list_restaurants(
        self, client: AsyncClient, factory_user, factory_group, factory_restaurant, auth_client
    ):
        owner = await factory_user(email="rlist_own@example.com")
        group = await factory_group(owner)
        await factory_restaurant(group, name="Sushi Place")
        ac = await auth_client(owner)
        resp = await ac.get(f"/api/groups/{group.id}/restaurants")
        assert resp.status_code == 200
        names = [r["name"] for r in resp.json()]
        assert "Sushi Place" in names

    async def test_create_restaurant_requires_editor(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, auth_client, db
    ):
        owner = await factory_user(email="rcreate_own@example.com")
        viewer = await factory_user(email="rcreate_viewer@example.com")
        group = await factory_group_with_members(owner, [(viewer, GroupRole.SUPERVISOR_MEMBER)])
        # SUPERVISOR_MEMBER has restaurants=viewer — not editor

        ac = await auth_client(viewer)
        resp = await ac.post(f"/api/groups/{group.id}/restaurants", json={"name": "Sneaky Restaurant"})
        assert resp.status_code == 403

    async def test_editor_can_create_and_update_restaurant(
        self, client: AsyncClient, factory_user, factory_group, auth_client
    ):
        owner = await factory_user(email="redit_own@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)
        # owner has restaurants=editor (admin preset)
        resp = await ac.post(f"/api/groups/{group.id}/restaurants", json={"name": "New Place"})
        assert resp.status_code == 201
        rid = resp.json()["id"]

        resp2 = await ac.patch(f"/api/groups/{group.id}/restaurants/{rid}", json={"name": "Updated Place"})
        assert resp2.status_code == 200
        assert resp2.json()["name"] == "Updated Place"

    async def test_delete_restaurant_editor_only(
        self,
        client: AsyncClient,
        factory_user,
        factory_group,
        factory_group_with_members,
        factory_restaurant,
        auth_client,
        db,
    ):
        owner = await factory_user(email="rdel_own@example.com")
        viewer = await factory_user(email="rdel_viewer@example.com")
        group = await factory_group_with_members(owner, [(viewer, GroupRole.SUPERVISOR_MEMBER)])
        restaurant = await factory_restaurant(group, name="To Delete")

        ac = await auth_client(viewer)
        resp = await ac.delete(f"/api/groups/{group.id}/restaurants/{restaurant.id}")
        assert resp.status_code == 403


class TestDishCRUD:
    async def test_dish_crud_nested_under_restaurant(
        self, client: AsyncClient, factory_user, factory_group, factory_restaurant, auth_client
    ):
        owner = await factory_user(email="dish_own@example.com")
        group = await factory_group(owner)
        restaurant = await factory_restaurant(group, name="Dish Host")
        ac = await auth_client(owner)

        # Create dish
        resp = await ac.post(
            f"/api/groups/{group.id}/restaurants/{restaurant.id}/dishes",
            json={"name": "Burger", "price": "9.99"},
        )
        assert resp.status_code == 201
        dish_id = resp.json()["id"]

        # Verify it appears in restaurant detail
        resp2 = await ac.get(f"/api/groups/{group.id}/restaurants/{restaurant.id}")
        assert resp2.status_code == 200
        dish_names = [d["name"] for d in resp2.json()["dishes"]]
        assert "Burger" in dish_names

        # Delete dish
        resp3 = await ac.delete(f"/api/groups/{group.id}/restaurants/{restaurant.id}/dishes/{dish_id}")
        assert resp3.status_code == 200

    async def test_dish_on_foreign_group_restaurant_returns_error(
        self, client: AsyncClient, factory_user, factory_group, factory_restaurant, auth_client
    ):
        owner_a = await factory_user(email="foreign_own_a@example.com")
        owner_b = await factory_user(email="foreign_own_b@example.com")
        group_a = await factory_group(owner_a)
        group_b = await factory_group(owner_b)
        restaurant_b = await factory_restaurant(group_b, name="Group B Restaurant")

        # owner_a tries to create a dish in group_a/ but uses restaurant from group_b
        ac = await auth_client(owner_a)
        resp = await ac.post(
            f"/api/groups/{group_a.id}/restaurants/{restaurant_b.id}/dishes",
            json={"name": "Salad", "price": "5.00"},
        )
        # Should be 404 (restaurant not in this group) or 403
        assert resp.status_code in (403, 404)
