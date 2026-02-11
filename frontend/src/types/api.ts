import type { User } from "./models";

// Auth
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthResponse {
  user: User;
  message?: string;
}

// Users
export interface UserListParams {
  page?: number;
  page_size?: number;
  search?: string;
}

export interface UserListResponse {
  items: User[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface UserUpdateRequest {
  full_name?: string;
  email?: string;
  navigate_to_active_order?: boolean;
}

export interface AdminUserCreateRequest {
  email: string;
  password: string;
  full_name: string;
  is_admin?: boolean;
}

export interface AdminUserUpdateRequest {
  full_name?: string;
  email?: string;
  is_active?: boolean;
  is_admin?: boolean;
  navigate_to_active_order?: boolean;
}

// Groups
export interface GroupCreateRequest {
  name: string;
  description?: string;
}

export interface GroupUpdateRequest {
  name?: string;
  description?: string;
}

export interface GroupMemberCreateRequest {
  user_id: string;
  role?: string;
  members_scope?: string;
  orders_scope?: string;
  balances_scope?: string;
  analytics_scope?: string;
  restaurants_scope?: string;
}

export interface GroupMemberUpdateRequest {
  role?: string;
  members_scope?: string;
  orders_scope?: string;
  balances_scope?: string;
  analytics_scope?: string;
  restaurants_scope?: string;
}

export interface InvitationCreateRequest {
  email: string;
  role?: string;
}

// Restaurants
export interface RestaurantCreateRequest {
  name: string;
  description?: string;
}

export interface RestaurantUpdateRequest {
  name?: string;
  description?: string;
}

export interface DishCreateRequest {
  name: string;
  detail?: string;
  price: number;
}

export interface DishUpdateRequest {
  name?: string;
  detail?: string;
  price?: number;
}

// Orders
export interface OrderCreateRequest {
  restaurant_id?: string;
  restaurant_name?: string;
}

export interface OrderItemCreateRequest {
  name: string;
  detail?: string;
  price: number;
  dish_id?: string;
}

export interface OrderItemUpdateRequest {
  name?: string;
  detail?: string;
  price?: number;
}

export interface OrderSetDeliveryFeeRequest {
  delivery_fee_total?: number;
  delivery_fee_per_person?: number;
}

// Balances
export interface BalanceAdjustmentRequest {
  user_id: string;
  amount: number;
  note?: string;
}

// Generic API
export interface ApiErrorResponse {
  detail: string;
  status_code: number;
}

export interface MessageResponse {
  message: string;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
