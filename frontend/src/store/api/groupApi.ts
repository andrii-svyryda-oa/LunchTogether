import { API_ENDPOINTS } from "@/constants";
import type {
  Group,
  GroupCreateRequest,
  GroupDetail,
  GroupInvitation,
  GroupMember,
  GroupMemberCreateRequest,
  GroupMemberUpdateRequest,
  GroupUpdateRequest,
  InvitationAcceptResult,
  InvitationCreateRequest,
  InvitationPreview,
  MessageResponse,
  MyInvitation,
} from "@/types";
import { baseApi } from "./baseApi";

export const groupApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    // Groups
    getGroups: builder.query<Group[], void>({
      query: () => API_ENDPOINTS.GROUPS.LIST,
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({
                type: "Group" as const,
                id,
              })),
              { type: "Group" as const, id: "LIST" },
            ]
          : [{ type: "Group" as const, id: "LIST" }],
    }),

    getGroup: builder.query<GroupDetail, string>({
      query: (id) => API_ENDPOINTS.GROUPS.DETAIL(id),
      providesTags: (_result, _error, id) => [
        { type: "Group" as const, id },
        { type: "GroupMember" as const, id: "LIST" },
      ],
    }),

    createGroup: builder.mutation<Group, GroupCreateRequest>({
      query: (data) => ({
        url: API_ENDPOINTS.GROUPS.LIST,
        method: "POST",
        body: data,
      }),
      invalidatesTags: [{ type: "Group" as const, id: "LIST" }],
    }),

    updateGroup: builder.mutation<
      Group,
      { groupId: string; data: GroupUpdateRequest }
    >({
      query: ({ groupId, data }) => ({
        url: API_ENDPOINTS.GROUPS.DETAIL(groupId),
        method: "PATCH",
        body: data,
      }),
      invalidatesTags: (_result, _error, { groupId }) => [
        { type: "Group" as const, id: groupId },
      ],
    }),

    deleteGroup: builder.mutation<MessageResponse, string>({
      query: (groupId) => ({
        url: API_ENDPOINTS.GROUPS.DETAIL(groupId),
        method: "DELETE",
      }),
      invalidatesTags: [{ type: "Group" as const, id: "LIST" }],
    }),

    // Members
    getGroupMembers: builder.query<GroupMember[], string>({
      query: (groupId) => API_ENDPOINTS.GROUPS.MEMBERS(groupId),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({
                type: "GroupMember" as const,
                id,
              })),
              { type: "GroupMember" as const, id: "LIST" },
            ]
          : [{ type: "GroupMember" as const, id: "LIST" }],
    }),

    addGroupMember: builder.mutation<
      GroupMember,
      { groupId: string; data: GroupMemberCreateRequest }
    >({
      query: ({ groupId, data }) => ({
        url: API_ENDPOINTS.GROUPS.MEMBERS(groupId),
        method: "POST",
        body: data,
      }),
      invalidatesTags: [
        { type: "GroupMember" as const, id: "LIST" },
        { type: "Group" as const, id: "LIST" },
      ],
    }),

    updateGroupMember: builder.mutation<
      GroupMember,
      { groupId: string; userId: string; data: GroupMemberUpdateRequest }
    >({
      query: ({ groupId, userId, data }) => ({
        url: API_ENDPOINTS.GROUPS.MEMBER_DETAIL(groupId, userId),
        method: "PATCH",
        body: data,
      }),
      invalidatesTags: [{ type: "GroupMember" as const, id: "LIST" }],
    }),

    removeGroupMember: builder.mutation<
      MessageResponse,
      { groupId: string; userId: string }
    >({
      query: ({ groupId, userId }) => ({
        url: API_ENDPOINTS.GROUPS.MEMBER_DETAIL(groupId, userId),
        method: "DELETE",
      }),
      invalidatesTags: [
        { type: "GroupMember" as const, id: "LIST" },
        { type: "Group" as const, id: "LIST" },
      ],
    }),

    // Invitations
    getInvitationByToken: builder.query<InvitationPreview, string>({
      query: (token) => API_ENDPOINTS.GROUPS.INVITATION_BY_TOKEN(token),
    }),

    getMyPendingInvitations: builder.query<MyInvitation[], void>({
      query: () => API_ENDPOINTS.GROUPS.MY_INVITATIONS,
      providesTags: [{ type: "GroupInvitation" as const, id: "MINE" }],
    }),

    getGroupInvitations: builder.query<GroupInvitation[], string>({
      query: (groupId) => API_ENDPOINTS.GROUPS.INVITATIONS(groupId),
      providesTags: (result, _error, groupId) =>
        result
          ? [
              ...result.map(({ id }) => ({
                type: "GroupInvitation" as const,
                id,
              })),
              { type: "GroupInvitation" as const, id: `LIST-${groupId}` },
            ]
          : [{ type: "GroupInvitation" as const, id: `LIST-${groupId}` }],
    }),

    createInvitation: builder.mutation<
      GroupInvitation,
      { groupId: string; data: InvitationCreateRequest }
    >({
      query: ({ groupId, data }) => ({
        url: API_ENDPOINTS.GROUPS.INVITATIONS(groupId),
        method: "POST",
        body: data,
      }),
      invalidatesTags: (_result, _error, { groupId }) => [
        { type: "GroupInvitation" as const, id: `LIST-${groupId}` },
      ],
    }),

    cancelInvitation: builder.mutation<
      MessageResponse,
      { groupId: string; invitationId: string }
    >({
      query: ({ groupId, invitationId }) => ({
        url: API_ENDPOINTS.GROUPS.INVITATION_DETAIL(groupId, invitationId),
        method: "DELETE",
      }),
      invalidatesTags: (_result, _error, { groupId, invitationId }) => [
        { type: "GroupInvitation" as const, id: invitationId },
        { type: "GroupInvitation" as const, id: `LIST-${groupId}` },
      ],
    }),

    acceptInvitation: builder.mutation<InvitationAcceptResult, string>({
      query: (token) => ({
        url: API_ENDPOINTS.GROUPS.ACCEPT_INVITATION(token),
        method: "POST",
      }),
      invalidatesTags: [
        { type: "Group" as const, id: "LIST" },
        { type: "GroupInvitation" as const, id: "MINE" },
      ],
    }),

    declineInvitation: builder.mutation<MessageResponse, string>({
      query: (token) => ({
        url: API_ENDPOINTS.GROUPS.DECLINE_INVITATION(token),
        method: "POST",
      }),
      invalidatesTags: [{ type: "GroupInvitation" as const, id: "MINE" }],
    }),
  }),
});

export const {
  useGetGroupsQuery,
  useGetGroupQuery,
  useCreateGroupMutation,
  useUpdateGroupMutation,
  useDeleteGroupMutation,
  useGetGroupMembersQuery,
  useAddGroupMemberMutation,
  useUpdateGroupMemberMutation,
  useRemoveGroupMemberMutation,
  useGetInvitationByTokenQuery,
  useGetMyPendingInvitationsQuery,
  useGetGroupInvitationsQuery,
  useCreateInvitationMutation,
  useCancelInvitationMutation,
  useAcceptInvitationMutation,
  useDeclineInvitationMutation,
} = groupApi;
