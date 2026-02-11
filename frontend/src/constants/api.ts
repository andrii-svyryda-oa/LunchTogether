export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: "/auth/login",
    REGISTER: "/auth/register",
    LOGOUT: "/auth/logout",
    ME: "/auth/me",
  },
  USERS: {
    LIST: "/users",
    DETAIL: (id: string) => `/users/${id}`,
    ADMIN_UPDATE: (id: string) => `/users/${id}/admin`,
    ANALYTICS: "/users/me/analytics",
  },
  GROUPS: {
    LIST: "/groups",
    DETAIL: (id: string) => `/groups/${id}`,
    MEMBERS: (groupId: string) => `/groups/${groupId}/members`,
    MEMBER_DETAIL: (groupId: string, userId: string) =>
      `/groups/${groupId}/members/${userId}`,
    INVITATIONS: (groupId: string) => `/groups/${groupId}/invitations`,
    ACCEPT_INVITATION: (token: string) => `/groups/invitations/${token}/accept`,
    DECLINE_INVITATION: (token: string) =>
      `/groups/invitations/${token}/decline`,
    LOGO: (groupId: string) => `/groups/${groupId}/logo`,
    ANALYTICS: (groupId: string) => `/groups/${groupId}/analytics`,
  },
  RESTAURANTS: {
    LIST: (groupId: string) => `/groups/${groupId}/restaurants`,
    DETAIL: (groupId: string, restaurantId: string) =>
      `/groups/${groupId}/restaurants/${restaurantId}`,
    DISHES: (groupId: string, restaurantId: string) =>
      `/groups/${groupId}/restaurants/${restaurantId}/dishes`,
    DISH_DETAIL: (groupId: string, restaurantId: string, dishId: string) =>
      `/groups/${groupId}/restaurants/${restaurantId}/dishes/${dishId}`,
  },
  ORDERS: {
    LIST: (groupId: string) => `/groups/${groupId}/orders`,
    ACTIVE: (groupId: string) => `/groups/${groupId}/orders/active`,
    DETAIL: (groupId: string, orderId: string) =>
      `/groups/${groupId}/orders/${orderId}`,
    STATUS: (groupId: string, orderId: string) =>
      `/groups/${groupId}/orders/${orderId}/status`,
    DELIVERY_FEE: (groupId: string, orderId: string) =>
      `/groups/${groupId}/orders/${orderId}/delivery-fee`,
    ITEMS: (groupId: string, orderId: string) =>
      `/groups/${groupId}/orders/${orderId}/items`,
    ITEM_DETAIL: (groupId: string, orderId: string, itemId: string) =>
      `/groups/${groupId}/orders/${orderId}/items/${itemId}`,
    FAVORITES: (groupId: string, restaurantId: string) =>
      `/groups/${groupId}/orders/favorites/${restaurantId}`,
    TOGGLE_FAVORITE: (groupId: string, dishId: string) =>
      `/groups/${groupId}/orders/favorites/${dishId}`,
  },
  BALANCES: {
    LIST: (groupId: string) => `/groups/${groupId}/balances`,
    ME: (groupId: string) => `/groups/${groupId}/balances/me`,
    ADJUST: (groupId: string) => `/groups/${groupId}/balances/adjust`,
    HISTORY: (groupId: string, userId: string) =>
      `/groups/${groupId}/balances/${userId}/history`,
  },
} as const;

export const API_TAG_TYPES = {
  AUTH: "Auth",
  USER: "User",
  GROUP: "Group",
  GROUP_MEMBER: "GroupMember",
  RESTAURANT: "Restaurant",
  DISH: "Dish",
  ORDER: "Order",
  ORDER_ITEM: "OrderItem",
  BALANCE: "Balance",
  ANALYTICS: "Analytics",
} as const;
