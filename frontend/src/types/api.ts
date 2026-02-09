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
  limit?: number;
  search?: string;
}

export interface UserListResponse {
  users: User[];
  total: number;
  page: number;
  limit: number;
}

export interface UserUpdateRequest {
  full_name?: string;
  email?: string;
}

// Generic API
export interface ApiErrorResponse {
  detail: string;
  status_code: number;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
}
