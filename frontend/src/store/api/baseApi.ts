import { env } from "@/config/env";
import { API_ENDPOINTS, API_TAG_TYPES } from "@/constants";
import { ROUTES } from "@/constants";
import type {
  BaseQueryFn,
  FetchArgs,
  FetchBaseQueryError,
} from "@reduxjs/toolkit/query";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

const rawBaseQuery = fetchBaseQuery({
  baseUrl: env.apiBaseUrl,
  credentials: "include",
  prepareHeaders: (headers) => {
    headers.set("Content-Type", "application/json");
    return headers;
  },
});

/** Auth endpoints that should NOT trigger a redirect on 401. */
const AUTH_ENDPOINTS = new Set([
  API_ENDPOINTS.AUTH.LOGIN,
  API_ENDPOINTS.AUTH.REGISTER,
  API_ENDPOINTS.AUTH.LOGOUT,
  API_ENDPOINTS.AUTH.ME,
]);

const baseQueryWithReauth: BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError
> = async (args, api, extraOptions) => {
  const result = await rawBaseQuery(args, api, extraOptions);

  if (result.error?.status === 401) {
    const data = result.error.data as { detail?: string } | undefined;

    if (data?.detail === "Not authenticated") {
      // Determine the request URL to skip auth-related endpoints
      const url = typeof args === "string" ? args : args.url;

      if (!AUTH_ENDPOINTS.has(url)) {
        api.dispatch({ type: "auth/clearUser" });
        window.location.href = ROUTES.LOGIN;
      }
    }
  }

  return result;
};

export const baseApi = createApi({
  reducerPath: "api",
  baseQuery: baseQueryWithReauth,
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
