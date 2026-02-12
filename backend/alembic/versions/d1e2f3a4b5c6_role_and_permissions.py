"""Add user role field and group_member_permissions table

Revision ID: d1e2f3a4b5c6
Revises: c8849dcdeddf
Create Date: 2026-02-11 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d1e2f3a4b5c6"
down_revision: str | None = "c8849dcdeddf"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Add role column to users (default 'user')
    op.add_column("users", sa.Column("role", sa.String(length=20), nullable=False, server_default="user"))

    # 2. Migrate is_admin=True to role='admin'
    op.execute("UPDATE users SET role = 'admin' WHERE is_admin = true")

    # 3. Drop is_admin column
    op.drop_column("users", "is_admin")

    # 4. Create group_member_permissions table
    op.create_table(
        "group_member_permissions",
        sa.Column("group_member_id", sa.UUID(), nullable=False),
        sa.Column("permission_type", sa.String(length=30), nullable=False),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["group_member_id"], ["group_members.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("group_member_id", "permission_type", name="uq_group_member_permission_type"),
    )

    # 5. Migrate existing scope columns to permission rows
    op.execute("""
        INSERT INTO group_member_permissions (id, group_member_id, permission_type, level, created_at, updated_at)
        SELECT gen_random_uuid(), id, 'members', members_scope, now(), now() FROM group_members
        UNION ALL
        SELECT gen_random_uuid(), id, 'orders', orders_scope, now(), now() FROM group_members
        UNION ALL
        SELECT gen_random_uuid(), id, 'balances', balances_scope, now(), now() FROM group_members
        UNION ALL
        SELECT gen_random_uuid(), id, 'analytics', analytics_scope, now(), now() FROM group_members
        UNION ALL
        SELECT gen_random_uuid(), id, 'restaurants', restaurants_scope, now(), now() FROM group_members
    """)

    # 6. Drop old scope columns from group_members
    op.drop_column("group_members", "members_scope")
    op.drop_column("group_members", "orders_scope")
    op.drop_column("group_members", "balances_scope")
    op.drop_column("group_members", "analytics_scope")
    op.drop_column("group_members", "restaurants_scope")


def downgrade() -> None:
    # Re-add scope columns to group_members
    op.add_column(
        "group_members",
        sa.Column("members_scope", sa.String(length=20), nullable=False, server_default="none"),
    )
    op.add_column(
        "group_members",
        sa.Column("orders_scope", sa.String(length=20), nullable=False, server_default="participant"),
    )
    op.add_column(
        "group_members",
        sa.Column("balances_scope", sa.String(length=20), nullable=False, server_default="none"),
    )
    op.add_column(
        "group_members",
        sa.Column("analytics_scope", sa.String(length=20), nullable=False, server_default="none"),
    )
    op.add_column(
        "group_members",
        sa.Column("restaurants_scope", sa.String(length=20), nullable=False, server_default="viewer"),
    )

    # Migrate permissions back to columns
    op.execute("""
        UPDATE group_members gm SET
            members_scope = COALESCE((SELECT level FROM group_member_permissions WHERE group_member_id = gm.id AND permission_type = 'members'), 'none'),
            orders_scope = COALESCE((SELECT level FROM group_member_permissions WHERE group_member_id = gm.id AND permission_type = 'orders'), 'participant'),
            balances_scope = COALESCE((SELECT level FROM group_member_permissions WHERE group_member_id = gm.id AND permission_type = 'balances'), 'none'),
            analytics_scope = COALESCE((SELECT level FROM group_member_permissions WHERE group_member_id = gm.id AND permission_type = 'analytics'), 'none'),
            restaurants_scope = COALESCE((SELECT level FROM group_member_permissions WHERE group_member_id = gm.id AND permission_type = 'restaurants'), 'viewer')
    """)

    # Drop permissions table
    op.drop_table("group_member_permissions")

    # Re-add is_admin column and migrate from role
    op.add_column("users", sa.Column("is_admin", sa.Boolean(), nullable=False, server_default="false"))
    op.execute("UPDATE users SET is_admin = true WHERE role = 'admin'")
    op.drop_column("users", "role")
