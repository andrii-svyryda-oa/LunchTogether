export type UserRole = "admin" | "user";

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  role: UserRole;
  navigate_to_active_order: boolean;
  created_at: string;
  updated_at: string;
}

// --- Groups ---

export interface Group {
  id: string;
  name: string;
  description: string | null;
  logo_path: string | null;
  owner_id: string;
  member_count?: number;
  created_at: string;
  updated_at: string;
}

export interface GroupDetail extends Group {
  members: GroupMember[];
}

export interface GroupMemberPermission {
  permission_type: string;
  level: string;
}

export interface GroupMember {
  id: string;
  user_id: string;
  group_id: string;
  permissions: GroupMemberPermission[];
  user_full_name?: string;
  user_email?: string;
  created_at: string;
  updated_at: string;
}

export interface GroupInvitation {
  id: string;
  group_id: string;
  inviter_id: string;
  invitee_email: string;
  invitee_id: string | null;
  status: string;
  token: string;
  created_at: string;
  updated_at: string;
}

// --- Restaurants ---

export interface Restaurant {
  id: string;
  name: string;
  description: string | null;
  group_id: string;
  created_at: string;
  updated_at: string;
}

export interface RestaurantDetail extends Restaurant {
  dishes: Dish[];
}

export interface Dish {
  id: string;
  name: string;
  detail: string | null;
  price: number;
  restaurant_id: string;
  created_at: string;
  updated_at: string;
}

// --- Orders ---

export type OrderStatus =
  | "initiated"
  | "confirmed"
  | "ordered"
  | "finished"
  | "cancelled";

export interface Order {
  id: string;
  group_id: string;
  restaurant_id: string | null;
  restaurant_name: string | null;
  initiator_id: string;
  status: OrderStatus;
  delivery_fee_total: number | null;
  delivery_fee_per_person: number | null;
  created_at: string;
  updated_at: string;
}

export interface OrderDetail extends Order {
  items: OrderItem[];
  initiator_name: string | null;
  participant_count: number;
  total_amount: number;
}

export interface OrderItem {
  id: string;
  order_id: string;
  user_id: string;
  name: string;
  detail: string | null;
  price: number;
  dish_id: string | null;
  user_full_name?: string;
  created_at: string;
  updated_at: string;
}

export interface FavoriteDish {
  id: string;
  user_id: string;
  dish_id: string;
  dish_name?: string;
  dish_detail?: string;
  dish_price?: number;
  restaurant_id?: string;
}

// --- Balances ---

export interface Balance {
  id: string;
  user_id: string;
  group_id: string;
  amount: number;
  user_full_name?: string;
  created_at: string;
  updated_at: string;
}

export interface BalanceHistory {
  id: string;
  balance_id: string;
  amount: number;
  balance_after: number;
  note: string | null;
  change_type: string;
  order_id: string | null;
  created_by_id: string | null;
  created_by_name?: string;
  created_at: string;
  updated_at: string;
}

// --- Analytics ---

export interface GroupAnalytics {
  total_orders: number;
  completed_orders: number;
  cancelled_orders: number;
  active_orders: number;
  total_members: number;
  total_spent: number;
  average_order_value: number;
  most_popular_restaurant: string | null;
  most_active_member: string | null;
}

export interface UserAnalytics {
  total_groups: number;
  total_orders_participated: number;
  total_spent: number;
  average_order_value: number;
  favorite_restaurant: string | null;
  total_balance_across_groups: number;
}

// --- Enums ---

export const MEMBERS_SCOPES = ["editor", "viewer", "none"] as const;
export const ORDERS_SCOPES = ["editor", "initiator", "participant"] as const;
export const BALANCES_SCOPES = ["editor", "viewer", "none"] as const;
export const ANALYTICS_SCOPES = ["viewer", "none"] as const;
export const RESTAURANTS_SCOPES = ["editor", "viewer"] as const;
export const GROUP_ROLES = ["admin", "supervisor_member", "member"] as const;
