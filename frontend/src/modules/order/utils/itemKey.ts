import type { OrderItem } from "@/types";

export interface ItemKeyable {
  name: string;
  detail: string | null;
  price: number;
  dish_id: string | null;
}

/**
 * Stable key for an order item, used for deduplication and aggregation.
 * Matches by dish_id when present, else by name+detail+price.
 */
export function itemKey(item: OrderItem | ItemKeyable): string {
  return item.dish_id
    ? `dish:${item.dish_id}`
    : `custom:${item.name}|${item.detail ?? ""}|${Number(item.price)}`;
}
