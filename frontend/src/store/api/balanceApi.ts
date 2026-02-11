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
      invalidatesTags: [{ type: "Balance" as const, id: "LIST" }],
    }),

    getBalanceHistory: builder.query<
      BalanceHistory[],
      { groupId: string; userId: string }
    >({
      query: ({ groupId, userId }) =>
        API_ENDPOINTS.BALANCES.HISTORY(groupId, userId),
    }),
  }),
});

export const {
  useGetBalancesQuery,
  useGetMyBalanceQuery,
  useAdjustBalanceMutation,
  useGetBalanceHistoryQuery,
} = balanceApi;
