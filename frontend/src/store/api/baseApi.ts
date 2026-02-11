import { env } from "@/config/env";
import { API_TAG_TYPES } from "@/constants";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const baseApi = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({
    baseUrl: env.apiBaseUrl,
    credentials: "include",
    prepareHeaders: (headers) => {
      headers.set("Content-Type", "application/json");
      return headers;
    },
  }),
  tagTypes: [
    API_TAG_TYPES.AUTH,
    API_TAG_TYPES.USER,
    API_TAG_TYPES.GROUP,
    API_TAG_TYPES.GROUP_MEMBER,
    API_TAG_TYPES.RESTAURANT,
    API_TAG_TYPES.DISH,
    API_TAG_TYPES.ORDER,
    API_TAG_TYPES.ORDER_ITEM,
    API_TAG_TYPES.BALANCE,
    API_TAG_TYPES.ANALYTICS,
  ],
  endpoints: () => ({}),
});
