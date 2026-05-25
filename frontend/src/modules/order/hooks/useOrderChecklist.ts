import type { OrderItem } from "@/types";
import { useMemo, useState } from "react";
import { itemKey } from "../utils/itemKey";

export interface AggregatedRow {
  key: string;
  name: string;
  detail: string | null;
  quantity: number;
}

/**
 * UI-only aggregated checklist for the "Place the Order" dialog.
 * Merges items across users by dish_id (or name+detail+price) and
 * tracks which rows have been ticked off. State resets on refresh.
 */
export function useOrderChecklist(items: OrderItem[]) {
  const [open, setOpen] = useState(false);
  const [checkedKeys, setCheckedKeys] = useState<Set<string>>(new Set());

  const aggregated = useMemo<AggregatedRow[]>(() => {
    const map = new Map<string, AggregatedRow>();
    for (const item of items) {
      const key = itemKey(item);
      const qty = item.quantity ?? 1;
      const existing = map.get(key);
      if (existing) {
        existing.quantity += qty;
      } else {
        map.set(key, {
          key,
          name: item.name,
          detail: item.detail,
          quantity: qty,
        });
      }
    }
    return Array.from(map.values()).sort((a, b) =>
      a.name.localeCompare(b.name),
    );
  }, [items]);

  const toggle = (key: string) => {
    setCheckedKeys((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const reset = () => setCheckedKeys(new Set());

  return {
    open,
    setOpen,
    aggregated,
    checkedKeys,
    toggle,
    reset,
  };
}
