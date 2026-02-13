import { API_ENDPOINTS } from "@/constants";
import type {
  FavoriteDish,
  MessageResponse,
  Order,
  OrderCreateRequest,
  OrderDetail,
  OrderItem,
  OrderItemCreateRequest,
  OrderItemUpdateRequest,
  OrderSetDeliveryFeeRequest,
} from "@/types";
import { baseApi } from "./baseApi";

export const orderApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getOrders: builder.query<Order[], string>({
      query: (groupId) => API_ENDPOINTS.ORDERS.LIST(groupId),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({
                type: "Order" as const,
                id,
              })),
              { type: "Order" as const, id: "LIST" },
            ]
          : [{ type: "Order" as const, id: "LIST" }],
    }),

    getActiveOrder: builder.query<OrderDetail | null, string>({
      query: (groupId) => API_ENDPOINTS.ORDERS.ACTIVE(groupId),
      providesTags: [
        { type: "Order" as const, id: "ACTIVE" },
        { type: "OrderItem" as const, id: "LIST" },
      ],
    }),

    getOrder: builder.query<OrderDetail, { groupId: string; orderId: string }>({
      query: ({ groupId, orderId }) =>
        API_ENDPOINTS.ORDERS.DETAIL(groupId, orderId),
      providesTags: (_result, _error, { orderId }) => [
        { type: "Order" as const, id: orderId },
        { type: "OrderItem" as const, id: "LIST" },
      ],
    }),

    createOrder: builder.mutation<
      Order,
      { groupId: string; data: OrderCreateRequest }
    >({
      query: ({ groupId, data }) => ({
        url: API_ENDPOINTS.ORDERS.LIST(groupId),
        method: "POST",
        body: data,
      }),
      invalidatesTags: [
        { type: "Order" as const, id: "LIST" },
        { type: "Order" as const, id: "ACTIVE" },
        { type: "Restaurant" as const, id: "LIST" },
      ],
    }),

    updateOrderStatus: builder.mutation<
      Order,
      { groupId: string; orderId: string; status: string }
    >({
      query: ({ groupId, orderId, status }) => ({
        url: API_ENDPOINTS.ORDERS.STATUS(groupId, orderId),
        method: "POST",
        body: { status },
      }),
      invalidatesTags: (_result, _error, { orderId }) => [
        { type: "Order" as const, id: orderId },
        { type: "Order" as const, id: "LIST" },
        { type: "Order" as const, id: "ACTIVE" },
        { type: "Balance" as const, id: "LIST" },
        { type: "Analytics" as const, id: "LIST" },
      ],
    }),

    setDeliveryFee: builder.mutation<
      Order,
      {
        groupId: string;
        orderId: string;
        data: OrderSetDeliveryFeeRequest;
      }
    >({
      query: ({ groupId, orderId, data }) => ({
        url: API_ENDPOINTS.ORDERS.DELIVERY_FEE(groupId, orderId),
        method: "POST",
        body: data,
      }),
      invalidatesTags: (_result, _error, { orderId }) => [
        { type: "Order" as const, id: orderId },
      ],
    }),

    // Order Items
    getOrderItems: builder.query<
      OrderItem[],
      { groupId: string; orderId: string }
    >({
      query: ({ groupId, orderId }) =>
        API_ENDPOINTS.ORDERS.ITEMS(groupId, orderId),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({
                type: "OrderItem" as const,
                id,
              })),
              { type: "OrderItem" as const, id: "LIST" },
            ]
          : [{ type: "OrderItem" as const, id: "LIST" }],
    }),

    addOrderItem: builder.mutation<
      OrderItem,
      { groupId: string; orderId: string; data: OrderItemCreateRequest }
    >({
      query: ({ groupId, orderId, data }) => ({
        url: API_ENDPOINTS.ORDERS.ITEMS(groupId, orderId),
        method: "POST",
        body: data,
      }),
      invalidatesTags: (_result, _error, { orderId }) => [
        { type: "OrderItem" as const, id: "LIST" },
        { type: "Order" as const, id: orderId },
        { type: "Order" as const, id: "ACTIVE" },
      ],
    }),

    updateOrderItem: builder.mutation<
      OrderItem,
      {
        groupId: string;
        orderId: string;
        itemId: string;
        data: OrderItemUpdateRequest;
      }
    >({
      query: ({ groupId, orderId, itemId, data }) => ({
        url: API_ENDPOINTS.ORDERS.ITEM_DETAIL(groupId, orderId, itemId),
        method: "PATCH",
        body: data,
      }),
      invalidatesTags: (_result, _error, { orderId }) => [
        { type: "OrderItem" as const, id: "LIST" },
        { type: "Order" as const, id: orderId },
        { type: "Order" as const, id: "ACTIVE" },
      ],
    }),

    deleteOrderItem: builder.mutation<
      MessageResponse,
      { groupId: string; orderId: string; itemId: string }
    >({
      query: ({ groupId, orderId, itemId }) => ({
        url: API_ENDPOINTS.ORDERS.ITEM_DETAIL(groupId, orderId, itemId),
        method: "DELETE",
      }),
      invalidatesTags: (_result, _error, { orderId }) => [
        { type: "OrderItem" as const, id: "LIST" },
        { type: "Order" as const, id: orderId },
        { type: "Order" as const, id: "ACTIVE" },
      ],
    }),

    // Favorites
    getFavorites: builder.query<
      FavoriteDish[],
      { groupId: string; restaurantId: string }
    >({
      query: ({ groupId, restaurantId }) =>
        API_ENDPOINTS.ORDERS.FAVORITES(groupId, restaurantId),
    }),

    toggleFavorite: builder.mutation<
      MessageResponse,
      { groupId: string; dishId: string }
    >({
      query: ({ groupId, dishId }) => ({
        url: API_ENDPOINTS.ORDERS.TOGGLE_FAVORITE(groupId, dishId),
        method: "POST",
      }),
    }),
  }),
});

export const {
  useGetOrdersQuery,
  useGetActiveOrderQuery,
  useGetOrderQuery,
  useCreateOrderMutation,
  useUpdateOrderStatusMutation,
  useSetDeliveryFeeMutation,
  useGetOrderItemsQuery,
  useAddOrderItemMutation,
  useUpdateOrderItemMutation,
  useDeleteOrderItemMutation,
  useGetFavoritesQuery,
  useToggleFavoriteMutation,
} = orderApi;
