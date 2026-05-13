export const PERMISSION_TYPE = {
  MEMBERS: "members",
  ORDERS: "orders",
  BALANCES: "balances",
  ANALYTICS: "analytics",
  RESTAURANTS: "restaurants",
} as const;

export const MEMBERS_SCOPE = {
  EDITOR: "editor",
  VIEWER: "viewer",
  NONE: "none",
} as const;

export const ORDERS_SCOPE = {
  EDITOR: "editor",
  INITIATOR: "initiator",
  PARTICIPANT: "participant",
} as const;

export const BALANCES_SCOPE = {
  EDITOR: "editor",
  VIEWER: "viewer",
  NONE: "none",
} as const;

export const ANALYTICS_SCOPE = {
  VIEWER: "viewer",
  NONE: "none",
} as const;

export const RESTAURANTS_SCOPE = {
  EDITOR: "editor",
  VIEWER: "viewer",
} as const;
