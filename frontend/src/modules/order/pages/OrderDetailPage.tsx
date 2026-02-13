import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks";
import { useGetGroupMembersQuery } from "@/store/api/groupApi";
import {
  useAddOrderItemMutation,
  useDeleteOrderItemMutation,
  useGetOrderQuery,
  useSetDeliveryFeeMutation,
  useUpdateOrderItemMutation,
  useUpdateOrderStatusMutation,
} from "@/store/api/orderApi";
import type { OrderItem } from "@/types";
import { cn } from "@/utils";
import {
  DollarSign,
  Minus,
  Pencil,
  Plus,
  ShoppingCart,
  Trash2,
  Truck,
  Users,
} from "lucide-react";
import { useState } from "react";
import { useParams } from "react-router-dom";

const STATUS_STYLES: Record<string, { bg: string; text: string; dot: string }> =
  {
    initiated: { bg: "bg-blue-50", text: "text-blue-700", dot: "bg-blue-500" },
    confirmed: {
      bg: "bg-amber-50",
      text: "text-amber-700",
      dot: "bg-amber-500",
    },
    ordered: {
      bg: "bg-purple-50",
      text: "text-purple-700",
      dot: "bg-purple-500",
    },
    finished: {
      bg: "bg-emerald-50",
      text: "text-emerald-700",
      dot: "bg-emerald-500",
    },
    cancelled: { bg: "bg-red-50", text: "text-red-700", dot: "bg-red-500" },
  };

const NEXT_STATUS: Record<string, { label: string; status: string }> = {
  initiated: { label: "Confirm Order", status: "confirmed" },
  confirmed: { label: "Mark as Ordered", status: "ordered" },
  ordered: { label: "Mark as Finished", status: "finished" },
};

export function OrderDetailPage() {
  const { groupId, orderId } = useParams<{
    groupId: string;
    orderId: string;
  }>();
  const { user } = useAuth();
  const {
    data: order,
    isLoading,
    error,
  } = useGetOrderQuery({
    groupId: groupId!,
    orderId: orderId!,
  });
  const { data: groupMembers } = useGetGroupMembersQuery(groupId!, {
    skip: !groupId,
  });
  const [updateStatus] = useUpdateOrderStatusMutation();
  const [addItem] = useAddOrderItemMutation();
  const [updateItem] = useUpdateOrderItemMutation();
  const [deleteItem] = useDeleteOrderItemMutation();
  const [setDeliveryFee] = useSetDeliveryFeeMutation();

  // Add item state
  const [addOpen, setAddOpen] = useState(false);
  const [addForUserId, setAddForUserId] = useState<string | null>(null);
  const [itemName, setItemName] = useState("");
  const [itemDetail, setItemDetail] = useState("");
  const [itemPrice, setItemPrice] = useState("");
  const [itemQuantity, setItemQuantity] = useState("1");

  // Edit item state
  const [editOpen, setEditOpen] = useState(false);
  const [editItem, setEditItem] = useState<OrderItem | null>(null);
  const [editName, setEditName] = useState("");
  const [editDetail, setEditDetail] = useState("");
  const [editPrice, setEditPrice] = useState("");
  const [editQuantity, setEditQuantity] = useState("1");

  // Delivery fee state
  const [feeOpen, setFeeOpen] = useState(false);
  const [feeTotal, setFeeTotal] = useState("");

  // Add for member dialog state (confirmed state)
  const [memberPickerOpen, setMemberPickerOpen] = useState(false);

  const resetAddForm = () => {
    setItemName("");
    setItemDetail("");
    setItemPrice("");
    setItemQuantity("1");
    setAddForUserId(null);
  };

  const handleAddItem = async () => {
    try {
      await addItem({
        groupId: groupId!,
        orderId: orderId!,
        data: {
          name: itemName,
          detail: itemDetail || undefined,
          price: parseFloat(itemPrice),
          quantity: parseInt(itemQuantity) || 1,
          user_id: addForUserId || undefined,
        },
      }).unwrap();
      setAddOpen(false);
      resetAddForm();
    } catch {
      // handled
    }
  };

  const openEditDialog = (item: OrderItem) => {
    setEditItem(item);
    setEditName(item.name);
    setEditDetail(item.detail ?? "");
    setEditPrice(String(item.price));
    setEditQuantity(String(item.quantity ?? 1));
    setEditOpen(true);
  };

  const handleEditItem = async () => {
    if (!editItem) return;
    try {
      await updateItem({
        groupId: groupId!,
        orderId: orderId!,
        itemId: editItem.id,
        data: {
          name: editName,
          detail: editDetail || undefined,
          price: parseFloat(editPrice),
          quantity: parseInt(editQuantity) || 1,
        },
      }).unwrap();
      setEditOpen(false);
      setEditItem(null);
    } catch {
      // handled
    }
  };

  const handleDeleteItem = async (itemId: string) => {
    await deleteItem({ groupId: groupId!, orderId: orderId!, itemId });
  };

  const handleTransition = async (status: string) => {
    if (status === "cancelled" && !confirm("Cancel this order?")) return;
    if (
      status === "finished" &&
      !confirm("Mark this order as finished? This will update balances.")
    )
      return;
    await updateStatus({ groupId: groupId!, orderId: orderId!, status });
  };

  const handleSetFee = async () => {
    try {
      await setDeliveryFee({
        groupId: groupId!,
        orderId: orderId!,
        data: { delivery_fee_total: parseFloat(feeTotal) },
      }).unwrap();
      setFeeOpen(false);
      setFeeTotal("");
    } catch {
      // handled
    }
  };

  const openAddForMember = (userId: string) => {
    setAddForUserId(userId);
    resetAddForm();
    setAddForUserId(userId);
    setAddOpen(true);
  };

  const openAddForSelf = () => {
    resetAddForm();
    setAddOpen(true);
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

  const isInitiator = order.initiator_id === user?.id;
  const canEditInitiated = order.status === "initiated";
  const canEditConfirmed =
    order.status === "confirmed" &&
    (isInitiator || user?.role === "admin");
  const canEdit = canEditInitiated || canEditConfirmed;
  const canManage = isInitiator || user?.role === "admin";
  const nextAction = NEXT_STATUS[order.status];
  const style = STATUS_STYLES[order.status] ?? STATUS_STYLES.initiated;

  // Group items by user
  const itemsByUser = order.items.reduce(
    (acc, item) => {
      const key = item.user_id;
      if (!acc[key]) acc[key] = { name: item.user_full_name ?? item.user_id, items: [] };
      acc[key].items.push(item);
      return acc;
    },
    {} as Record<string, { name: string; items: typeof order.items }>,
  );

  // Get members not currently in the order (for "Add member dish" in confirmed state)
  const existingParticipantIds = new Set(Object.keys(itemsByUser));
  const availableMembers = groupMembers?.filter(
    (m) => !existingParticipantIds.has(m.user_id),
  );

  // Calculate per-user subtotals
  const getUserSubtotal = (items: typeof order.items) =>
    items.reduce((sum, item) => sum + Number(item.price) * (item.quantity ?? 1), 0);

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-3xl font-bold tracking-tight">
              {order.restaurant_name ?? "Custom Order"}
            </h1>
            <span
              className={cn(
                "inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full font-medium",
                style.bg,
                style.text,
              )}
            >
              <span className={cn("h-1.5 w-1.5 rounded-full", style.dot)} />
              {order.status}
            </span>
          </div>
          <p className="text-muted-foreground">
            By {order.initiator_name} &middot;{" "}
            {new Date(order.created_at).toLocaleDateString()}
          </p>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid gap-4 sm:grid-cols-3 mb-8">
        <Card className="p-5 hover:shadow-md group">
          <div className="flex items-center gap-3 mb-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600 group-hover:scale-105 transition-transform">
              <Users className="h-5 w-5" />
            </div>
            <p className="text-sm font-medium text-muted-foreground">
              Participants
            </p>
          </div>
          <p className="text-2xl font-bold">{order.participant_count}</p>
        </Card>

        <Card className="p-5 hover:shadow-md group">
          <div className="flex items-center gap-3 mb-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-green-50 text-green-600 group-hover:scale-105 transition-transform">
              <DollarSign className="h-5 w-5" />
            </div>
            <p className="text-sm font-medium text-muted-foreground">
              Items Total
            </p>
          </div>
          <p className="text-2xl font-bold">
            {Number(order.total_amount).toFixed(2)} ₴
          </p>
        </Card>

        <Dialog open={feeOpen} onOpenChange={setFeeOpen}>
          <Card className="p-5 hover:shadow-md group relative">
            <div className="flex items-center gap-3 mb-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-50 text-purple-600 group-hover:scale-105 transition-transform">
                <Truck className="h-5 w-5" />
              </div>
              <p className="text-sm font-medium text-muted-foreground">
                Delivery Fee
              </p>
              {canManage &&
                order.status !== "finished" &&
                order.status !== "cancelled" && (
                <DialogTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="absolute top-3 right-3 h-7 w-7 text-muted-foreground hover:text-primary"
                  >
                    <Pencil className="h-3.5 w-3.5" />
                  </Button>
                </DialogTrigger>
              )}
            </div>
            <p className="text-2xl font-bold">
              {order.delivery_fee_total
                ? `${Number(order.delivery_fee_total).toFixed(2)} ₴`
                : "\u2014"}
            </p>
          </Card>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Set Delivery/Packing Fee</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label>Total Fee (divided equally)</Label>
                <Input
                  type="number"
                  step="0.01"
                  min="0"
                  value={feeTotal}
                  onChange={(e) => setFeeTotal(e.target.value)}
                  placeholder="5.00"
                />
              </div>
              <Button
                onClick={handleSetFee}
                disabled={!feeTotal}
                className="w-full"
              >
                Set Fee
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-2 mb-8">
        {canEditInitiated && (
          <Button
            className="shadow-md shadow-primary/20"
            onClick={openAddForSelf}
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Dish
          </Button>
        )}

        {canEditConfirmed && (
          <Dialog open={memberPickerOpen} onOpenChange={setMemberPickerOpen}>
            <DialogTrigger asChild>
              <Button className="shadow-md shadow-primary/20">
                <Plus className="mr-2 h-4 w-4" />
                Add Dish for Member
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Select Member</DialogTitle>
              </DialogHeader>
              <div className="space-y-2 pt-4 max-h-80 overflow-y-auto">
                {/* Existing participants */}
                {Object.entries(itemsByUser).map(([userId, { name }]) => (
                  <Button
                    key={userId}
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => {
                      setMemberPickerOpen(false);
                      openAddForMember(userId);
                    }}
                  >
                    <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-primary-foreground text-[10px] font-bold mr-2 shrink-0">
                      {name.charAt(0).toUpperCase()}
                    </div>
                    {name}
                  </Button>
                ))}
                {/* Members not yet in order */}
                {availableMembers && availableMembers.length > 0 && (
                  <>
                    {Object.keys(itemsByUser).length > 0 && (
                      <div className="border-t my-2" />
                    )}
                    <p className="text-xs text-muted-foreground px-1 pb-1">Other group members</p>
                    {availableMembers.map((member) => (
                      <Button
                        key={member.user_id}
                        variant="outline"
                        className="w-full justify-start"
                        onClick={() => {
                          setMemberPickerOpen(false);
                          openAddForMember(member.user_id);
                        }}
                      >
                        <div className="flex h-6 w-6 items-center justify-center rounded-full bg-muted text-muted-foreground text-[10px] font-bold mr-2 shrink-0">
                          {(member.user_full_name ?? "?").charAt(0).toUpperCase()}
                        </div>
                        {member.user_full_name ?? member.user_email}
                      </Button>
                    ))}
                  </>
                )}
              </div>
            </DialogContent>
          </Dialog>
        )}

        {canManage && nextAction && (
          <Button onClick={() => handleTransition(nextAction.status)}>
            {nextAction.label}
          </Button>
        )}

        {canManage &&
          order.status !== "finished" &&
          order.status !== "cancelled" && (
            <Button
              variant="destructive"
              onClick={() => handleTransition("cancelled")}
            >
              Cancel Order
            </Button>
          )}
      </div>

      {/* Add Item Dialog */}
      <Dialog open={addOpen} onOpenChange={(open) => { setAddOpen(open); if (!open) resetAddForm(); }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {addForUserId
                ? `Add Dish${addForUserId !== user?.id ? " for Member" : ""}`
                : "Add Your Dish"}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 pt-4">
            <div className="space-y-2">
              <Label>Dish Name</Label>
              <Input
                value={itemName}
                onChange={(e) => setItemName(e.target.value)}
                placeholder="Burger"
              />
            </div>
            <div className="space-y-2">
              <Label>Detail (optional)</Label>
              <Input
                value={itemDetail}
                onChange={(e) => setItemDetail(e.target.value)}
                placeholder="No onions"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Price</Label>
                <Input
                  type="number"
                  step="0.01"
                  min="0"
                  value={itemPrice}
                  onChange={(e) => setItemPrice(e.target.value)}
                  placeholder="9.99"
                />
              </div>
              <div className="space-y-2">
                <Label>Quantity</Label>
                <div className="flex items-center gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    className="h-9 w-9 shrink-0"
                    onClick={() =>
                      setItemQuantity(String(Math.max(1, parseInt(itemQuantity) - 1)))
                    }
                    disabled={parseInt(itemQuantity) <= 1}
                  >
                    <Minus className="h-4 w-4" />
                  </Button>
                  <Input
                    type="number"
                    min="1"
                    value={itemQuantity}
                    onChange={(e) => setItemQuantity(e.target.value)}
                    className="text-center"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    className="h-9 w-9 shrink-0"
                    onClick={() =>
                      setItemQuantity(String(parseInt(itemQuantity) + 1))
                    }
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
            <Button
              onClick={handleAddItem}
              disabled={!itemName.trim() || !itemPrice}
              className="w-full"
            >
              Add
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Edit Item Dialog */}
      <Dialog open={editOpen} onOpenChange={(open) => { setEditOpen(open); if (!open) setEditItem(null); }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Dish</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 pt-4">
            <div className="space-y-2">
              <Label>Dish Name</Label>
              <Input
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                placeholder="Burger"
              />
            </div>
            <div className="space-y-2">
              <Label>Detail (optional)</Label>
              <Input
                value={editDetail}
                onChange={(e) => setEditDetail(e.target.value)}
                placeholder="No onions"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Price</Label>
                <Input
                  type="number"
                  step="0.01"
                  min="0"
                  value={editPrice}
                  onChange={(e) => setEditPrice(e.target.value)}
                  placeholder="9.99"
                />
              </div>
              <div className="space-y-2">
                <Label>Quantity</Label>
                <div className="flex items-center gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    className="h-9 w-9 shrink-0"
                    onClick={() =>
                      setEditQuantity(String(Math.max(1, parseInt(editQuantity) - 1)))
                    }
                    disabled={parseInt(editQuantity) <= 1}
                  >
                    <Minus className="h-4 w-4" />
                  </Button>
                  <Input
                    type="number"
                    min="1"
                    value={editQuantity}
                    onChange={(e) => setEditQuantity(e.target.value)}
                    className="text-center"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    className="h-9 w-9 shrink-0"
                    onClick={() =>
                      setEditQuantity(String(parseInt(editQuantity) + 1))
                    }
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
            <Button
              onClick={handleEditItem}
              disabled={!editName.trim() || !editPrice}
              className="w-full"
            >
              Save Changes
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Items grouped by user */}
      <h2 className="text-xl font-semibold mb-4">Order Items</h2>
      {Object.entries(itemsByUser).length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-16 border-dashed">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-muted mb-4">
            <ShoppingCart className="h-7 w-7 text-muted-foreground" />
          </div>
          <p className="text-muted-foreground font-medium mb-1">No items yet</p>
          <p className="text-sm text-muted-foreground">
            Be the first to add your dish!
          </p>
        </Card>
      ) : (
        <div className="space-y-6">
          {Object.entries(itemsByUser).map(([userId, { name, items }]) => {
            const subtotal = getUserSubtotal(items);
            const deliveryShare = order.delivery_fee_per_person
              ? Number(order.delivery_fee_per_person)
              : 0;
            const memberTotal = subtotal + deliveryShare;

            return (
              <div key={userId}>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary text-primary-foreground text-[11px] font-bold shrink-0">
                      {name.charAt(0).toUpperCase()}
                    </div>
                    <h3 className="font-medium text-sm">{name}</h3>
                    <span className="text-xs text-muted-foreground ml-1">
                      {subtotal.toFixed(2)} ₴
                      {deliveryShare > 0 && (
                        <span> + {deliveryShare.toFixed(2)} ₴ delivery</span>
                      )}
                      {deliveryShare > 0 && (
                        <span className="font-semibold text-foreground ml-1">
                          = {memberTotal.toFixed(2)} ₴
                        </span>
                      )}
                    </span>
                  </div>
                  {canEditConfirmed && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => openAddForMember(userId)}
                      className="text-muted-foreground hover:text-primary"
                    >
                      <Plus className="h-4 w-4 mr-1" />
                      Add
                    </Button>
                  )}
                </div>
                <div className="space-y-2 ml-9">
                  {items.map((item) => (
                    <Card key={item.id} className="p-3.5 hover:shadow-md">
                      <div className="flex items-center justify-between">
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <p className="font-medium">{item.name}</p>
                            {(item.quantity ?? 1) > 1 && (
                              <span className="text-xs bg-muted text-muted-foreground px-1.5 py-0.5 rounded-md font-medium">
                                x{item.quantity}
                              </span>
                            )}
                          </div>
                          {item.detail && (
                            <p className="text-sm text-muted-foreground">
                              {item.detail}
                            </p>
                          )}
                        </div>
                        <div className="flex items-center gap-3 shrink-0">
                          <span className="font-semibold text-primary">
                            {(item.quantity ?? 1) > 1
                              ? `${Number(item.price).toFixed(2)} × ${item.quantity} = ${(Number(item.price) * (item.quantity ?? 1)).toFixed(2)} ₴`
                              : `${Number(item.price).toFixed(2)} ₴`}
                          </span>
                          {canEdit &&
                            (canEditConfirmed ||
                              item.user_id === user?.id ||
                              user?.role === "admin") && (
                              <>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => openEditDialog(item)}
                                  className="text-muted-foreground hover:text-primary"
                                >
                                  <Pencil className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => handleDeleteItem(item.id)}
                                  className="text-muted-foreground hover:text-destructive"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </>
                            )}
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
