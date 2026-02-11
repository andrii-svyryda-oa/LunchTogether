import { API_ENDPOINTS } from "@/constants";
import type {
  AdminUserCreateRequest,
  AdminUserUpdateRequest,
  User,
  UserListParams,
  UserListResponse,
  UserUpdateRequest,
} from "@/types";
import { baseApi } from "./baseApi";

export const userApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getUsers: builder.query<UserListResponse, UserListParams | void>({
      query: (params) => ({
        url: API_ENDPOINTS.USERS.LIST,
        params: params ?? undefined,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.items.map(({ id }) => ({
                type: "User" as const,
                id,
              })),
              { type: "User" as const, id: "LIST" },
            ]
          : [{ type: "User" as const, id: "LIST" }],
    }),

    getUser: builder.query<User, string>({
      query: (id) => API_ENDPOINTS.USERS.DETAIL(id),
      providesTags: (_result, _error, id) => [{ type: "User" as const, id }],
    }),

    createUser: builder.mutation<User, AdminUserCreateRequest>({
      query: (data) => ({
        url: API_ENDPOINTS.USERS.LIST,
        method: "POST",
        body: data,
      }),
      invalidatesTags: [{ type: "User" as const, id: "LIST" }],
    }),

    updateUser: builder.mutation<User, { id: string; data: UserUpdateRequest }>(
      {
        query: ({ id, data }) => ({
          url: API_ENDPOINTS.USERS.DETAIL(id),
          method: "PATCH",
          body: data,
        }),
        invalidatesTags: (_result, _error, { id }) => [
          { type: "User" as const, id },
          { type: "User" as const, id: "LIST" },
          "Auth",
        ],
      },
    ),

    adminUpdateUser: builder.mutation<
      User,
      { id: string; data: AdminUserUpdateRequest }
    >({
      query: ({ id, data }) => ({
        url: API_ENDPOINTS.USERS.ADMIN_UPDATE(id),
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (_result, _error, { id }) => [
        { type: "User" as const, id },
        { type: "User" as const, id: "LIST" },
      ],
    }),
  }),
});

export const {
  useGetUsersQuery,
  useGetUserQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
  useAdminUpdateUserMutation,
} = userApi;
