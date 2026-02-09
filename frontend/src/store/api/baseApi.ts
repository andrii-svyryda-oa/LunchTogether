import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { env } from "@/config/env";
import { API_TAG_TYPES } from "@/constants";

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
  tagTypes: [API_TAG_TYPES.AUTH, API_TAG_TYPES.USER],
  endpoints: () => ({}),
});
