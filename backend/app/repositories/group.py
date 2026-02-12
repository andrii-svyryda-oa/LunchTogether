import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

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
        """Count how many groups a user is a member of (as owner)."""
        query = select(func.count()).select_from(Group).where(Group.owner_id == user_id)
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

    async def set_permissions(
        self,
        group_member_id: uuid.UUID,
        permissions: dict[str, str],
    ) -> list[GroupMemberPermission]:
        """Set permissions for a group member. Creates or updates each permission type."""
        result = []
        for perm_type, level in permissions.items():
            existing = await self.session.execute(
                select(GroupMemberPermission).where(
                    GroupMemberPermission.group_member_id == group_member_id,
                    GroupMemberPermission.permission_type == perm_type,
                )
            )
            existing_perm = existing.scalar_one_or_none()
            if existing_perm:
                existing_perm.level = level
                await self.session.flush()
                await self.session.refresh(existing_perm)
                result.append(existing_perm)
            else:
                perm = GroupMemberPermission(
                    group_member_id=group_member_id,
                    permission_type=perm_type,
                    level=level,
                )
                self.session.add(perm)
                await self.session.flush()
                await self.session.refresh(perm)
                result.append(perm)
        return result

    async def get_for_member(self, group_member_id: uuid.UUID) -> list[GroupMemberPermission]:
        query = select(GroupMemberPermission).where(GroupMemberPermission.group_member_id == group_member_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())


class GroupInvitationRepository(BaseRepository[GroupInvitation]):
    def __init__(self, session: AsyncSession):
        super().__init__(GroupInvitation, session)

    async def get_by_token(self, token: str) -> GroupInvitation | None:
        query = select(GroupInvitation).where(GroupInvitation.token == token)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_pending_for_email(self, email: str, group_id: uuid.UUID) -> GroupInvitation | None:
        query = select(GroupInvitation).where(
            GroupInvitation.invitee_email == email,
            GroupInvitation.group_id == group_id,
            GroupInvitation.status == "pending",
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_pending_for_user(self, user_id: uuid.UUID) -> list[GroupInvitation]:
        query = (
            select(GroupInvitation)
            .where(
                GroupInvitation.invitee_id == user_id,
                GroupInvitation.status == "pending",
            )
            .options(joinedload(GroupInvitation.group))
        )
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())
