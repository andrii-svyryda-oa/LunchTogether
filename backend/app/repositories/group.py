import uuid

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.enums import InvitationStatus
from app.models.group import Group, GroupInvitation, GroupMember, GroupMemberPermission
from app.repositories.base import BaseRepository


class GroupRepository(BaseRepository[Group]):
    def __init__(self, session: AsyncSession):
        super().__init__(Group, session)

    async def get_by_owner(self, owner_id: uuid.UUID) -> list[Group]:
        query = select(Group).where(Group.owner_id == owner_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_by_owner(self, owner_id: uuid.UUID) -> int:
        query = select(func.count()).select_from(Group).where(Group.owner_id == owner_id)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_groups_for_user(self, user_id: uuid.UUID) -> list[Group]:
        """Get all groups where user is a member."""
        query = select(Group).join(GroupMember, Group.id == GroupMember.group_id).where(GroupMember.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_with_members(self, group_id: uuid.UUID) -> Group | None:
        query = (
            select(Group)
            .where(Group.id == group_id)
            .options(
                joinedload(Group.members).joinedload(GroupMember.user),
                joinedload(Group.members).joinedload(GroupMember.permissions),
            )
        )
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()


class GroupMemberRepository(BaseRepository[GroupMember]):
    def __init__(self, session: AsyncSession):
        super().__init__(GroupMember, session)

    async def get_membership(self, user_id: uuid.UUID, group_id: uuid.UUID) -> GroupMember | None:
        query = (
            select(GroupMember)
            .where(
                GroupMember.user_id == user_id,
                GroupMember.group_id == group_id,
            )
            .options(joinedload(GroupMember.permissions))
        )
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_members_for_group(self, group_id: uuid.UUID) -> list[GroupMember]:
        query = (
            select(GroupMember)
            .where(GroupMember.group_id == group_id)
            .options(joinedload(GroupMember.user), joinedload(GroupMember.permissions))
        )
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def count_members(self, group_id: uuid.UUID) -> int:
        query = select(func.count()).select_from(GroupMember).where(GroupMember.group_id == group_id)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def count_user_groups(self, user_id: uuid.UUID) -> int:
        """Count how many groups a user is a member of."""
        query = select(func.count()).select_from(GroupMember).where(GroupMember.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def delete_membership(self, user_id: uuid.UUID, group_id: uuid.UUID) -> bool:
        member = await self.get_membership(user_id, group_id)
        if member is None:
            return False
        await self.session.delete(member)
        await self.session.flush()
        return True


class GroupMemberPermissionRepository(BaseRepository[GroupMemberPermission]):
    def __init__(self, session: AsyncSession):
        super().__init__(GroupMemberPermission, session)

    async def get_for_member(self, group_member_id: uuid.UUID) -> list[GroupMemberPermission]:
        query = select(GroupMemberPermission).where(GroupMemberPermission.group_member_id == group_member_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_member_and_type(
        self, group_member_id: uuid.UUID, permission_type: str
    ) -> GroupMemberPermission | None:
        query = select(GroupMemberPermission).where(
            GroupMemberPermission.group_member_id == group_member_id,
            GroupMemberPermission.permission_type == permission_type,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def upsert_permission(
        self, group_member_id: uuid.UUID, permission_type: str, level: str
    ) -> GroupMemberPermission:
        """Create or update a single permission entry for a group member."""
        existing = await self.get_by_member_and_type(group_member_id, permission_type)
        if existing:
            existing.level = level
            await self.session.flush()
            await self.session.refresh(existing)
            return existing
        perm = GroupMemberPermission(
            group_member_id=group_member_id,
            permission_type=permission_type,
            level=level,
        )
        self.session.add(perm)
        await self.session.flush()
        await self.session.refresh(perm)
        return perm

    async def set_permissions(
        self,
        group_member_id: uuid.UUID,
        permissions: dict[str, str],
    ) -> list[GroupMemberPermission]:
        """Upsert a full set of permissions for a group member.

        The orchestration loop lives here temporarily; it will move to a
        dedicated workflow in Phase 3.
        """
        return [
            await self.upsert_permission(group_member_id, perm_type, level) for perm_type, level in permissions.items()
        ]


class GroupInvitationRepository(BaseRepository[GroupInvitation]):
    def __init__(self, session: AsyncSession):
        super().__init__(GroupInvitation, session)

    async def get_by_token(self, token: str) -> GroupInvitation | None:
        query = select(GroupInvitation).where(GroupInvitation.token == token)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_token_with_relations(self, token: str) -> GroupInvitation | None:
        """Load invitation with group and inviter eagerly joined (for public preview)."""
        query = (
            select(GroupInvitation)
            .where(GroupInvitation.token == token)
            .options(
                joinedload(GroupInvitation.group),
                joinedload(GroupInvitation.inviter),
            )
        )
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_pending_for_email(self, email: str, group_id: uuid.UUID) -> GroupInvitation | None:
        query = select(GroupInvitation).where(
            GroupInvitation.invitee_email == email,
            GroupInvitation.group_id == group_id,
            GroupInvitation.status == InvitationStatus.PENDING,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_pending_for_user(self, user_id: uuid.UUID, user_email: str) -> list[GroupInvitation]:
        """Return pending invitations for a user, matching by id OR by email (for pre-account invites)."""
        query = (
            select(GroupInvitation)
            .where(
                GroupInvitation.status == InvitationStatus.PENDING,
                or_(
                    GroupInvitation.invitee_id == user_id,
                    GroupInvitation.invitee_email == user_email,
                ),
            )
            .options(
                joinedload(GroupInvitation.group),
                joinedload(GroupInvitation.inviter),
            )
            .order_by(GroupInvitation.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def link_invitations_to_user(self, user_id: uuid.UUID, user_email: str) -> None:
        """Back-fill invitee_id on any existing pending invitations that match the email."""
        stmt = (
            update(GroupInvitation)
            .where(
                GroupInvitation.invitee_email == user_email,
                GroupInvitation.invitee_id.is_(None),
                GroupInvitation.status == InvitationStatus.PENDING,
            )
            .values(invitee_id=user_id)
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def get_pending_for_group(self, group_id: uuid.UUID) -> list[GroupInvitation]:
        query = (
            select(GroupInvitation)
            .where(
                GroupInvitation.group_id == group_id,
                GroupInvitation.status == InvitationStatus.PENDING,
            )
            .options(joinedload(GroupInvitation.inviter))
            .order_by(GroupInvitation.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())
