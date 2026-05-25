import {
  useAddOrderItemMutation,
  useDeleteOrderItemMutation,
  useUpdateOrderItemMutation,
} from "@/store/api/orderApi";
import type { OrderItem } from "@/types";
import { useState } from "react";

interface AddItemPayload {
  name: string;
  detail?: string;
  price: number;
  quantity: number;
  user_id?: string;
  dish_id?: string;
}

interface UpdateItemPayload {
  name: string;
  detail?: string;
  price: number;
  quantity: number;
}

export function useOrderItemActions(groupId: string, orderId: string) {
  const [addItemMutation] = useAddOrderItemMutation();
  const [updateItemMutation] = useUpdateOrderItemMutation();
  const [deleteItemMutation] = useDeleteOrderItemMutation();

  // Add dialog state
  const [addOpen, setAddOpen] = useState(false);
  const [addForUserId, setAddForUserId] = useState<string | null>(null);

  // Edit dialog state
  const [editItem, setEditItem] = useState<OrderItem | null>(null);

  const openAddForSelf = () => {
    setAddForUserId(null);
    setAddOpen(true);
  };

  const openAddForMember = (userId: string) => {
    setAddForUserId(userId);
    setAddOpen(true);
  };

  const closeAdd = () => {
    setAddOpen(false);
    setAddForUserId(null);
  };

  const openEdit = (item: OrderItem) => setEditItem(item);
  const closeEdit = () => setEditItem(null);

  const addItem = async (data: AddItemPayload) => {
    await addItemMutation({ groupId, orderId, data }).unwrap();
  };

  const updateItem = async (itemId: string, data: UpdateItemPayload) => {
    await updateItemMutation({ groupId, orderId, itemId, data }).unwrap();
  };

  const deleteItem = async (itemId: string) => {
    await deleteItemMutation({ groupId, orderId, itemId }).unwrap();
  };

  const copyItemToSelf = async (item: OrderItem) => {
    await addItem({
      name: item.name,
      detail: item.detail ?? undefined,
      price: Number(item.price),
      quantity: 1,
      dish_id: item.dish_id ?? undefined,
    });
  };

  return {
    addOpen,
    addForUserId,
    openAddForSelf,
    openAddForMember,
    closeAdd,

    editItem,
    openEdit,
    closeEdit,

    addItem,
    updateItem,
    deleteItem,
    copyItemToSelf,
  };
}
