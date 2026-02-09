import { baseApi } from "./baseApi";
import { API_ENDPOINTS } from "@/constants";
import type {
  User,
  UserListParams,
  UserListResponse,
  UserUpdateRequest,
} from "@/types";

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
              ...result.users.map(({ id }) => ({
                type: "User" as const,
                id,
              })),
              { type: "User" as const, id: "LIST" },
            ]
          : [{ type: "User" as const, id: "LIST" }],
    }),

    getUser: builder.query<User, string>({
      query: (id) => API_ENDPOINTS.USERS.DETAIL(id),
      providesTags: (_result, _error, id) => [
        { type: "User" as const, id },
      ],
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
        ],
      }
    ),
  }),
});

export const { useGetUsersQuery, useGetUserQuery, useUpdateUserMutation } =
  userApi;
