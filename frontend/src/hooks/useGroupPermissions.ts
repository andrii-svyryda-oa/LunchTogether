import {
  ANALYTICS_SCOPE,
  BALANCES_SCOPE,
  MEMBERS_SCOPE,
  ORDERS_SCOPE,
  PERMISSION_TYPE,
  RESTAURANTS_SCOPE,
} from "@/constants";
import { useGetGroupQuery } from "@/store/api/groupApi";
import { useAuth } from "./useAuth";

export interface GroupPermissions {
  isLoading: boolean;
  /** Platform-level admin (user.role === "admin") */
  isPlatformAdmin: boolean;
  isOwner: boolean;
  isMember: boolean;

  // Raw permission levels for the current user in this group (null = not found)
  members: "editor" | "viewer" | "none" | null;
  orders: "editor" | "initiator" | "participant" | null;
  balances: "editor" | "viewer" | "none" | null;
  analytics: "viewer" | "none" | null;
  restaurants: "editor" | "viewer" | null;

  // Derived capability flags — platform admins and group owners always get full access
  canViewMembersTab: boolean;
  canManageMembers: boolean;
  canInviteMembers: boolean;
  canViewGroupAnalytics: boolean;
  canViewGroupBalances: boolean;
  canAdjustBalances: boolean;
  canEditRestaurants: boolean;
  canCreateOrder: boolean;
  canManageOrderLifecycle: (initiatorId: string) => boolean;
}

const DEFAULT_PERMISSIONS: GroupPermissions = {
  isLoading: true,
  isPlatformAdmin: false,
  isOwner: false,
  isMember: false,
  members: null,
  orders: null,
  balances: null,
  analytics: null,
  restaurants: null,
  canViewMembersTab: false,
  canManageMembers: false,
  canInviteMembers: false,
  canViewGroupAnalytics: false,
  canViewGroupBalances: false,
  canAdjustBalances: false,
  canEditRestaurants: false,
  canCreateOrder: false,
  canManageOrderLifecycle: () => false,
};

export function useGroupPermissions(
  groupId: string | undefined
): GroupPermissions {
  const { user } = useAuth();
  const { data: group, isLoading } = useGetGroupQuery(groupId!, {
    skip: !groupId,
  });

  if (!groupId || isLoading) {
    return { ...DEFAULT_PERMISSIONS, isLoading: !!groupId && isLoading };
  }

  if (!group || !user) {
    return { ...DEFAULT_PERMISSIONS, isLoading: false };
  }

  const isPlatformAdmin = user.role === "admin";
  const isOwner = group.owner_id === user.id;
  // Platform admins and owners bypass all checks
  const isPrivileged = isPlatformAdmin || isOwner;

  const myMembership = group.members?.find((m) => m.user_id === user.id);
  const isMember = isPrivileged || !!myMembership;

  const getLevel = (type: string): string | null => {
    if (!myMembership) return null;
    return (
      myMembership.permissions.find((p) => p.permission_type === type)?.level ??
      null
    );
  };

  const members = getLevel(PERMISSION_TYPE.MEMBERS) as GroupPermissions["members"];
  const orders = getLevel(PERMISSION_TYPE.ORDERS) as GroupPermissions["orders"];
  const balances = getLevel(PERMISSION_TYPE.BALANCES) as GroupPermissions["balances"];
  const analytics = getLevel(PERMISSION_TYPE.ANALYTICS) as GroupPermissions["analytics"];
  const restaurants = getLevel(PERMISSION_TYPE.RESTAURANTS) as GroupPermissions["restaurants"];

  const canViewMembersTab =
    isPrivileged || (members !== null && members !== MEMBERS_SCOPE.NONE);
  const canManageMembers = isPrivileged || members === MEMBERS_SCOPE.EDITOR;
  const canInviteMembers =
    isPrivileged || (members !== null && members !== MEMBERS_SCOPE.NONE);
  const canViewGroupAnalytics =
    isPrivileged || analytics === ANALYTICS_SCOPE.VIEWER;
  const canViewGroupBalances =
    isPrivileged ||
    balances === BALANCES_SCOPE.VIEWER ||
    balances === BALANCES_SCOPE.EDITOR;
  const canAdjustBalances = isPrivileged || balances === BALANCES_SCOPE.EDITOR;
  const canEditRestaurants =
    isPrivileged || restaurants === RESTAURANTS_SCOPE.EDITOR;
  const canCreateOrder =
    isPrivileged ||
    orders === ORDERS_SCOPE.EDITOR ||
    orders === ORDERS_SCOPE.INITIATOR;
  const canManageOrderLifecycle = (initiatorId: string) =>
    isPrivileged ||
    user.id === initiatorId ||
    orders === ORDERS_SCOPE.EDITOR;

  return {
    isLoading: false,
    isPlatformAdmin,
    isOwner,
    isMember,
    members,
    orders,
    balances,
    analytics,
    restaurants,
    canViewMembersTab,
    canManageMembers,
    canInviteMembers,
    canViewGroupAnalytics,
    canViewGroupBalances,
    canAdjustBalances,
    canEditRestaurants,
    canCreateOrder,
    canManageOrderLifecycle,
  };
}
