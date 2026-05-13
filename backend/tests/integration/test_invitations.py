"""Integration tests for the invitation flow (§6.4.4 — 11 tests)."""

from httpx import AsyncClient

from app.models.enums import GroupRole


class TestCreateInvitation:
    async def test_member_can_invite(self, client: AsyncClient, factory_user, factory_group, auth_client, mock_email):
        owner = await factory_user(email="invowner@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)
        resp = await ac.post(f"/api/groups/{group.id}/invitations", json={"email": "newperson@example.com"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["invitee_email"] == "newperson@example.com"
        assert data["status"] == "pending"
        assert "token" in data

    async def test_non_member_cannot_invite(
        self, client: AsyncClient, factory_user, factory_group, auth_client, mock_email
    ):
        owner = await factory_user(email="invown2@example.com")
        stranger = await factory_user(email="stranger3@example.com")
        group = await factory_group(owner)
        ac = await auth_client(stranger)
        resp = await ac.post(f"/api/groups/{group.id}/invitations", json={"email": "target@example.com"})
        assert resp.status_code == 403

    async def test_duplicate_pending_invitation_rejected(
        self, client: AsyncClient, factory_user, factory_group, auth_client, mock_email
    ):
        owner = await factory_user(email="dupinvowner@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)
        await ac.post(f"/api/groups/{group.id}/invitations", json={"email": "dup@example.com"})
        resp = await ac.post(f"/api/groups/{group.id}/invitations", json={"email": "dup@example.com"})
        assert resp.status_code == 409

    async def test_invite_already_member_rejected(
        self, client: AsyncClient, factory_user, factory_group, auth_client, mock_email
    ):
        owner = await factory_user(email="invown3@example.com")
        existing_member = await factory_user(email="existing@example.com")
        group = await factory_group(owner)
        # Add existing_member to the group
        ac = await auth_client(owner)
        await ac.post(f"/api/groups/{group.id}/members", json={"user_id": str(existing_member.id), "role": "member"})
        # Try to invite them
        resp = await ac.post(f"/api/groups/{group.id}/invitations", json={"email": existing_member.email})
        assert resp.status_code == 409


class TestListInvitations:
    async def test_member_can_list_pending(
        self, client: AsyncClient, factory_user, factory_group, auth_client, mock_email
    ):
        owner = await factory_user(email="listinv@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)
        await ac.post(f"/api/groups/{group.id}/invitations", json={"email": "invitee1@example.com"})
        resp = await ac.get(f"/api/groups/{group.id}/invitations")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1


class TestCancelInvitation:
    async def test_owner_can_cancel(self, client: AsyncClient, factory_user, factory_group, auth_client, mock_email):
        owner = await factory_user(email="cancelown@example.com")
        group = await factory_group(owner)
        ac = await auth_client(owner)
        inv_resp = await ac.post(f"/api/groups/{group.id}/invitations", json={"email": "canceltarget@example.com"})
        invitation_id = inv_resp.json()["id"]
        resp = await ac.delete(f"/api/groups/{group.id}/invitations/{invitation_id}")
        assert resp.status_code == 200

    async def test_random_member_cannot_cancel_others_invite(
        self, client: AsyncClient, factory_user, factory_group, factory_group_with_members, auth_client, mock_email, db
    ):
        owner = await factory_user(email="canown2@example.com")
        regular = await factory_user(email="regular2@example.com")
        group = await factory_group_with_members(owner, [(regular, GroupRole.MEMBER)])
        ac_owner = await auth_client(owner)
        inv_resp = await ac_owner.post(f"/api/groups/{group.id}/invitations", json={"email": "victim@example.com"})
        invitation_id = inv_resp.json()["id"]

        ac_regular = await auth_client(regular)
        resp = await ac_regular.delete(f"/api/groups/{group.id}/invitations/{invitation_id}")
        assert resp.status_code == 403


class TestAcceptInvitation:
    async def test_correct_user_can_accept(
        self, client: AsyncClient, factory_user, factory_group, auth_client, mock_email
    ):
        owner = await factory_user(email="accown@example.com")
        invitee = await factory_user(email="invitee@example.com")
        group = await factory_group(owner)
        ac_owner = await auth_client(owner)
        inv_resp = await ac_owner.post(f"/api/groups/{group.id}/invitations", json={"email": invitee.email})
        token = inv_resp.json()["token"]

        ac_invitee = await auth_client(invitee)
        resp = await ac_invitee.post(f"/api/groups/invitations/{token}/accept")
        assert resp.status_code == 200
        assert resp.json()["group_id"] == str(group.id)

    async def test_wrong_email_cannot_accept(
        self, client: AsyncClient, factory_user, factory_group, auth_client, mock_email
    ):
        owner = await factory_user(email="wrongo@example.com")
        invitee = await factory_user(email="rightperson@example.com")
        wrong = await factory_user(email="wrongperson@example.com")
        group = await factory_group(owner)
        ac_owner = await auth_client(owner)
        inv_resp = await ac_owner.post(f"/api/groups/{group.id}/invitations", json={"email": invitee.email})
        token = inv_resp.json()["token"]

        ac_wrong = await auth_client(wrong)
        resp = await ac_wrong.post(f"/api/groups/invitations/{token}/accept")
        assert resp.status_code == 403

    async def test_already_accepted_invitation_rejected(
        self, client: AsyncClient, factory_user, factory_group, auth_client, mock_email
    ):
        owner = await factory_user(email="reaccown@example.com")
        invitee = await factory_user(email="reaccinvitee@example.com")
        group = await factory_group(owner)
        ac_owner = await auth_client(owner)
        inv_resp = await ac_owner.post(f"/api/groups/{group.id}/invitations", json={"email": invitee.email})
        token = inv_resp.json()["token"]

        ac_invitee = await auth_client(invitee)
        await ac_invitee.post(f"/api/groups/invitations/{token}/accept")
        resp = await ac_invitee.post(f"/api/groups/invitations/{token}/accept")
        assert resp.status_code in (403, 409)

    async def test_accept_enforces_25_member_cap(
        self, client: AsyncClient, factory_user, factory_group, auth_client, mock_email, db
    ):
        owner = await factory_user(email="capown@example.com")
        group = await factory_group(owner)
        ac_owner = await auth_client(owner)

        # Add 24 more members (owner is already member 1) to reach 25
        for i in range(24):
            extra = await factory_user(email=f"capuser{i}@example.com")
            await ac_owner.post(f"/api/groups/{group.id}/members", json={"user_id": str(extra.id), "role": "member"})

        # Now try to accept an invitation as the 26th member
        invitee = await factory_user(email="cap26th@example.com")
        inv_resp = await ac_owner.post(f"/api/groups/{group.id}/invitations", json={"email": invitee.email})
        token = inv_resp.json()["token"]

        ac_invitee = await auth_client(invitee)
        resp = await ac_invitee.post(f"/api/groups/invitations/{token}/accept")
        assert resp.status_code == 403


class TestDeclineInvitation:
    async def test_invitee_can_decline(self, client: AsyncClient, factory_user, factory_group, auth_client, mock_email):
        owner = await factory_user(email="decown@example.com")
        invitee = await factory_user(email="decinvitee@example.com")
        group = await factory_group(owner)
        ac_owner = await auth_client(owner)
        inv_resp = await ac_owner.post(f"/api/groups/{group.id}/invitations", json={"email": invitee.email})
        token = inv_resp.json()["token"]

        ac_invitee = await auth_client(invitee)
        resp = await ac_invitee.post(f"/api/groups/invitations/{token}/decline")
        assert resp.status_code == 200
