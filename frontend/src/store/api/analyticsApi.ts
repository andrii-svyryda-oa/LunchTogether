import { API_ENDPOINTS } from "@/constants";
import type { GroupAnalytics, UserAnalytics } from "@/types";
import { baseApi } from "./baseApi";

export const analyticsApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getGroupAnalytics: builder.query<GroupAnalytics, string>({
      query: (groupId) => API_ENDPOINTS.GROUPS.ANALYTICS(groupId),
      providesTags: [{ type: "Analytics" as const, id: "LIST" }],
    }),

    getUserAnalytics: builder.query<UserAnalytics, void>({
      query: () => API_ENDPOINTS.USERS.ANALYTICS,
      providesTags: [{ type: "Analytics" as const, id: "USER" }],
    }),
  }),
});

export const { useGetGroupAnalyticsQuery, useGetUserAnalyticsQuery } =
  analyticsApi;
