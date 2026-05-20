import { baseApi } from "./baseApi";
import { API_ENDPOINTS, API_TAG_TYPES } from "@/constants";
import type {
  AuthResponse,
  LoginRequest,
  MessageResponse,
  PasswordResetConfirmPayload,
  PasswordResetRequestPayload,
  RegisterRequest,
} from "@/types";
import type { User } from "@/types";

export const authApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    login: builder.mutation<AuthResponse, LoginRequest>({
      query: (credentials) => ({
        url: API_ENDPOINTS.AUTH.LOGIN,
        method: "POST",
        body: credentials,
      }),
      invalidatesTags: [API_TAG_TYPES.AUTH],
    }),

    register: builder.mutation<AuthResponse, RegisterRequest>({
      query: (data) => ({
        url: API_ENDPOINTS.AUTH.REGISTER,
        method: "POST",
        body: data,
      }),
    }),

    logout: builder.mutation<void, void>({
      query: () => ({
        url: API_ENDPOINTS.AUTH.LOGOUT,
        method: "POST",
      }),
      invalidatesTags: [API_TAG_TYPES.AUTH, API_TAG_TYPES.USER],
    }),

    getCurrentUser: builder.query<User, void>({
      query: () => API_ENDPOINTS.AUTH.ME,
      providesTags: [API_TAG_TYPES.AUTH],
    }),

    requestPasswordReset: builder.mutation<
      MessageResponse,
      PasswordResetRequestPayload
    >({
      query: (data) => ({
        url: API_ENDPOINTS.AUTH.REQUEST_PASSWORD_RESET,
        method: "POST",
        body: data,
      }),
    }),

    confirmPasswordReset: builder.mutation<
      MessageResponse,
      PasswordResetConfirmPayload
    >({
      query: (data) => ({
        url: API_ENDPOINTS.AUTH.CONFIRM_PASSWORD_RESET,
        method: "POST",
        body: data,
      }),
    }),
  }),
});

export const {
  useLoginMutation,
  useRegisterMutation,
  useLogoutMutation,
  useGetCurrentUserQuery,
  useRequestPasswordResetMutation,
  useConfirmPasswordResetMutation,
} = authApi;
