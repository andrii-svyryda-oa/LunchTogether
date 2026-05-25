import { Alert } from "@/components/ui/alert";
import { useAuth, useGroupPermissions } from "@/hooks";
import { useGetGroupMembersQuery } from "@/store/api/groupApi";
import {
  useGetOrderQuery,
  useUpdateOrderStatusMutation,
} from "@/store/api/orderApi";
import { useGetRestaurantQuery } from "@/store/api/restaurantApi";
import type { Dish, OrderItem } from "@/types";
import { useState } from "react";
import { useParams } from "react-router-dom";

import { AddItemDialog } from "../components/orderDetail/AddItemDialog";
import { DeliveryFeeDialog } from "../components/orderDetail/DeliveryFeeDialog";
import { EditItemDialog } from "../components/orderDetail/EditItemDialog";
import { OrderChecklistDialog } from "../components/orderDetail/OrderChecklistDialog";
import { OrderHeader } from "../components/orderDetail/OrderHeader";
import { OrderItemsList } from "../components/orderDetail/OrderItemsList";
import { OrderSummaryCards } from "../components/orderDetail/OrderSummaryCards";
import { RestaurantInfoCard } from "../components/orderDetail/RestaurantInfoCard";
import { SecondaryActionBar } from "../components/orderDetail/SecondaryActionBar";
import { useOrderChecklist } from "../hooks/useOrderChecklist";
import { useOrderItemActions } from "../hooks/useOrderItemActions";
import { itemKey } from "../utils/itemKey";

export function OrderDetailPage() {
  const { groupId, orderId } = useParams<{
    groupId: string;
    orderId: string;
  }>();
  const { user } = useAuth();
  const { canManageOrderLifecycle } = useGroupPermissions(groupId);

  const { data: order, isLoading, error } = useGetOrderQuery({
    groupId: groupId!,
    orderId: orderId!,
  });
  const { data: groupMembers } = useGetGroupMembersQuery(groupId!, {
    skip: !groupId,
  });
  const { data: restaurant } = useGetRestaurantQuery(
    { groupId: groupId!, restaurantId: order?.restaurant_id ?? "" },
    { skip: !groupId || !order?.restaurant_id },
  );

  const [updateStatus] = useUpdateOrderStatusMutation();
  const itemActions = useOrderItemActions(groupId!, orderId!);
  const checklist = useOrderChecklist(order?.items ?? []);

  const [feeOpen, setFeeOpen] = useState(false);

  const handleTransition = async (status: string) => {
    if (status === "cancelled" && !confirm("Cancel this order?")) return;
    if (
      status === "finished" &&
      !confirm("Mark this order as finished? This will update balances.")
    )
      return;
    await updateStatus({ groupId: groupId!, orderId: orderId!, status });
  };

  const handleConfirmOrdered = async () => {
    await updateStatus({
      groupId: groupId!,
      orderId: orderId!,
      status: "ordered",
    });
    checklist.setOpen(false);
  };

  const handleDeleteItem = async (itemId: string) => {
    await itemActions.deleteItem(itemId);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error || !order) {
    return <Alert variant="destructive">Failed to load order.</Alert>;
  }

  const canManage = canManageOrderLifecycle(order.initiator_id);
  const canEditInitiated = order.status === "initiated";
  const canEditConfirmed = order.status === "confirmed" && canManage;
  const canEditOwn = canEditInitiated || canEditConfirmed;

  // Group items by user, then sort with the current user first.
  const itemsByUser = order.items.reduce(
    (acc, item) => {
      const key = item.user_id;
      if (!acc[key])
        acc[key] = { name: item.user_full_name ?? item.user_id, items: [] };
      acc[key].items.push(item);
      return acc;
    },
    {} as Record<string, { name: string; items: OrderItem[] }>,
  );

  const sortedGroups = Object.entries(itemsByUser)
    .sort(([a], [b]) => {
      if (a === user?.id) return -1;
      if (b === user?.id) return 1;
      return 0;
    })
    .map(([userId, { name, items }]) => ({ userId, name, items }));

  const participants = sortedGroups.map(({ userId, name }) => ({
    userId,
    name,
  }));
  const existingParticipantIds = new Set(participants.map((p) => p.userId));
  const otherMembers =
    groupMembers?.filter((m) => !existingParticipantIds.has(m.user_id)) ?? [];

  // Dedupe helpers — match against the user the next add would target.
  const targetUserId = itemActions.addForUserId ?? user?.id ?? null;
  const targetUserKeys = new Set(
    order.items
      .filter((i) => i.user_id === targetUserId)
      .map((i) => itemKey(i)),
  );
  const myKeys = new Set(
    order.items.filter((i) => i.user_id === user?.id).map((i) => itemKey(i)),
  );

  const isDuplicateDish = (dish: Dish) =>
    targetUserKeys.has(
      itemKey({
        name: dish.name,
        detail: dish.detail,
        price: Number(dish.price),
        dish_id: dish.id,
      }),
    );

  const alreadyHaveItem = (item: OrderItem) => myKeys.has(itemKey(item));

  const showRestaurantInfo =
    order.status === "initiated" && restaurant !== undefined;

  const canEditFee =
    canManage && order.status !== "finished" && order.status !== "cancelled";

  return (
    <div>
      <OrderHeader
        order={order}
        canManage={canManage}
        onTransition={handleTransition}
        onOpenOrderDialog={() => checklist.setOpen(true)}
      />

      {showRestaurantInfo && restaurant && (
        <RestaurantInfoCard restaurant={restaurant} />
      )}

      <OrderSummaryCards
        order={order}
        canEditFee={canEditFee}
        onEditFee={() => setFeeOpen(true)}
      />

      <SecondaryActionBar
        canEditInitiated={canEditInitiated}
        canEditConfirmed={canEditConfirmed}
        participants={participants}
        otherMembers={otherMembers}
        onAddForSelf={itemActions.openAddForSelf}
        onAddForMember={itemActions.openAddForMember}
      />

      <AddItemDialog
        open={itemActions.addOpen}
        onOpenChange={(open) =>
          open ? null : itemActions.closeAdd()
        }
        forUserId={itemActions.addForUserId}
        currentUserId={user?.id}
        dishes={restaurant?.dishes}
        isDuplicateDish={isDuplicateDish}
        onSubmit={itemActions.addItem}
      />

      <EditItemDialog
        item={itemActions.editItem}
        onOpenChange={(open) => (open ? null : itemActions.closeEdit())}
        onSubmit={itemActions.updateItem}
      />

      <DeliveryFeeDialog
        open={feeOpen}
        onOpenChange={setFeeOpen}
        groupId={groupId!}
        orderId={orderId!}
      />

      <OrderChecklistDialog
        open={checklist.open}
        onOpenChange={checklist.setOpen}
        aggregated={checklist.aggregated}
        checkedKeys={checklist.checkedKeys}
        onToggle={checklist.toggle}
        onReset={checklist.reset}
        showOrderButton={canManage && order.status === "confirmed"}
        onOrder={handleConfirmOrdered}
      />

      <OrderItemsList
        order={order}
        groups={sortedGroups}
        currentUserId={user?.id}
        canEditInitiated={canEditInitiated}
        canEditConfirmed={canEditConfirmed}
        canEditOwn={canEditOwn}
        canManage={canManage}
        alreadyHaveItem={alreadyHaveItem}
        onAddForMember={itemActions.openAddForMember}
        onEditItem={itemActions.openEdit}
        onDeleteItem={handleDeleteItem}
        onCopyItemToSelf={itemActions.copyItemToSelf}
      />
    </div>
  );
}
