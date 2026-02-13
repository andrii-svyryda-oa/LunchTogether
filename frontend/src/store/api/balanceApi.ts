import { API_ENDPOINTS } from "@/constants";
import type {
  Balance,
  BalanceAdjustmentRequest,
  BalanceHistory,
} from "@/types";
import { baseApi } from "./baseApi";

export const balanceApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getBalances: builder.query<Balance[], string>({
      query: (groupId) => API_ENDPOINTS.BALANCES.LIST(groupId),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({
                type: "Balance" as const,
                id,
              })),
              { type: "Balance" as const, id: "LIST" },
            ]
          : [{ type: "Balance" as const, id: "LIST" }],
    }),

    getMyBalance: builder.query<Balance, string>({
      query: (groupId) => API_ENDPOINTS.BALANCES.ME(groupId),
      providesTags: [{ type: "Balance" as const, id: "ME" }],
    }),

    adjustBalance: builder.mutation<
      Balance,
      { groupId: string; data: BalanceAdjustmentRequest }
    >({
      query: ({ groupId, data }) => ({
        url: API_ENDPOINTS.BALANCES.ADJUST(groupId),
        method: "POST",
        body: data,
      }),
      invalidatesTags: (_result, _error, { data }) => [
        { type: "Balance" as const, id: "LIST" },
        { type: "Balance" as const, id: `HISTORY_${data.user_id}` },
      ],
    }),

    getBalanceHistory: builder.query<
      BalanceHistory[],
      { groupId: string; userId: string }
    >({
      query: ({ groupId, userId }) =>
        API_ENDPOINTS.BALANCES.HISTORY(groupId, userId),
      providesTags: (_result, _error, { userId }) => [
        { type: "Balance" as const, id: `HISTORY_${userId}` },
      ],
    }),
  }),
});

export const {
  useGetBalancesQuery,
  useGetMyBalanceQuery,
  useAdjustBalanceMutation,
  useGetBalanceHistoryQuery,
} = balanceApi;
