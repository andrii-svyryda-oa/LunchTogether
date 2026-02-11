import { API_ENDPOINTS } from "@/constants";
import type {
  Dish,
  DishCreateRequest,
  DishUpdateRequest,
  MessageResponse,
  Restaurant,
  RestaurantCreateRequest,
  RestaurantDetail,
  RestaurantUpdateRequest,
} from "@/types";
import { baseApi } from "./baseApi";

export const restaurantApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getRestaurants: builder.query<Restaurant[], string>({
      query: (groupId) => API_ENDPOINTS.RESTAURANTS.LIST(groupId),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({
                type: "Restaurant" as const,
                id,
              })),
              { type: "Restaurant" as const, id: "LIST" },
            ]
          : [{ type: "Restaurant" as const, id: "LIST" }],
    }),

    getRestaurant: builder.query<
      RestaurantDetail,
      { groupId: string; restaurantId: string }
    >({
      query: ({ groupId, restaurantId }) =>
        API_ENDPOINTS.RESTAURANTS.DETAIL(groupId, restaurantId),
      providesTags: (_result, _error, { restaurantId }) => [
        { type: "Restaurant" as const, id: restaurantId },
        { type: "Dish" as const, id: "LIST" },
      ],
    }),

    createRestaurant: builder.mutation<
      Restaurant,
      { groupId: string; data: RestaurantCreateRequest }
    >({
      query: ({ groupId, data }) => ({
        url: API_ENDPOINTS.RESTAURANTS.LIST(groupId),
        method: "POST",
        body: data,
      }),
      invalidatesTags: [{ type: "Restaurant" as const, id: "LIST" }],
    }),

    updateRestaurant: builder.mutation<
      Restaurant,
      { groupId: string; restaurantId: string; data: RestaurantUpdateRequest }
    >({
      query: ({ groupId, restaurantId, data }) => ({
        url: API_ENDPOINTS.RESTAURANTS.DETAIL(groupId, restaurantId),
        method: "PATCH",
        body: data,
      }),
      invalidatesTags: (_result, _error, { restaurantId }) => [
        { type: "Restaurant" as const, id: restaurantId },
      ],
    }),

    deleteRestaurant: builder.mutation<
      MessageResponse,
      { groupId: string; restaurantId: string }
    >({
      query: ({ groupId, restaurantId }) => ({
        url: API_ENDPOINTS.RESTAURANTS.DETAIL(groupId, restaurantId),
        method: "DELETE",
      }),
      invalidatesTags: [{ type: "Restaurant" as const, id: "LIST" }],
    }),

    // Dishes
    createDish: builder.mutation<
      Dish,
      { groupId: string; restaurantId: string; data: DishCreateRequest }
    >({
      query: ({ groupId, restaurantId, data }) => ({
        url: API_ENDPOINTS.RESTAURANTS.DISHES(groupId, restaurantId),
        method: "POST",
        body: data,
      }),
      invalidatesTags: [{ type: "Dish" as const, id: "LIST" }],
    }),

    updateDish: builder.mutation<
      Dish,
      {
        groupId: string;
        restaurantId: string;
        dishId: string;
        data: DishUpdateRequest;
      }
    >({
      query: ({ groupId, restaurantId, dishId, data }) => ({
        url: API_ENDPOINTS.RESTAURANTS.DISH_DETAIL(
          groupId,
          restaurantId,
          dishId,
        ),
        method: "PATCH",
        body: data,
      }),
      invalidatesTags: [{ type: "Dish" as const, id: "LIST" }],
    }),

    deleteDish: builder.mutation<
      MessageResponse,
      { groupId: string; restaurantId: string; dishId: string }
    >({
      query: ({ groupId, restaurantId, dishId }) => ({
        url: API_ENDPOINTS.RESTAURANTS.DISH_DETAIL(
          groupId,
          restaurantId,
          dishId,
        ),
        method: "DELETE",
      }),
      invalidatesTags: [{ type: "Dish" as const, id: "LIST" }],
    }),
  }),
});

export const {
  useGetRestaurantsQuery,
  useGetRestaurantQuery,
  useCreateRestaurantMutation,
  useUpdateRestaurantMutation,
  useDeleteRestaurantMutation,
  useCreateDishMutation,
  useUpdateDishMutation,
  useDeleteDishMutation,
} = restaurantApi;
