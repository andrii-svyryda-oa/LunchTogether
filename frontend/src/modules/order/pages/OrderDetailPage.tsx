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
import {
  useAddOrderItemMutation,
  useDeleteOrderItemMutation,
  useGetOrderQuery,
  useSetDeliveryFeeMutation,
  useUpdateOrderStatusMutation,
} from "@/store/api/orderApi";
import { cn } from "@/utils";
import { DollarSign, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { useParams } from "react-router-dom";

const STATUS_COLORS: Record<string, string> = {
  initiated: "bg-blue-100 text-blue-700",
  confirmed: "bg-yellow-100 text-yellow-700",
  ordered: "bg-purple-100 text-purple-700",
  finished: "bg-green-100 text-green-700",
  cancelled: "bg-red-100 text-red-700",
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
  const [updateStatus] = useUpdateOrderStatusMutation();
  const [addItem] = useAddOrderItemMutation();
  const [deleteItem] = useDeleteOrderItemMutation();
  const [setDeliveryFee] = useSetDeliveryFeeMutation();

  // Add item state
  const [addOpen, setAddOpen] = useState(false);
  const [itemName, setItemName] = useState("");
  const [itemDetail, setItemDetail] = useState("");
  const [itemPrice, setItemPrice] = useState("");

  // Delivery fee state
  const [feeOpen, setFeeOpen] = useState(false);
  const [feeTotal, setFeeTotal] = useState("");

  const handleAddItem = async () => {
    try {
      await addItem({
        groupId: groupId!,
        orderId: orderId!,
        data: {
          name: itemName,
          detail: itemDetail || undefined,
          price: parseFloat(itemPrice),
        },
      }).unwrap();
      setAddOpen(false);
      setItemName("");
      setItemDetail("");
      setItemPrice("");
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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error || !order) {
    return <Alert variant="destructive">Failed to load order.</Alert>;
  }

  const isInitiator = order.initiator_id === user?.id;
  const canEdit = order.status === "initiated";
  const canManage = isInitiator || user?.is_admin;
  const nextAction = NEXT_STATUS[order.status];

  // Group items by user
  const itemsByUser = order.items.reduce((acc, item) => {
    const key = item.user_full_name ?? item.user_id;
    if (!acc[key]) acc[key] = [];
    acc[key].push(item);
    return acc;
  }, {} as Record<string, typeof order.items>);

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            {order.restaurant_name ?? "Custom Order"}
          </h1>
          <p className="text-muted-foreground">
            By {order.initiator_name} ·{" "}
            {new Date(order.created_at).toLocaleDateString()}
          </p>
        </div>
        <span
          className={cn(
            "text-sm px-3 py-1 rounded font-medium",
            STATUS_COLORS[order.status],
          )}
        >
          {order.status}
        </span>
      </div>

      {/* Summary cards */}
      <div className="grid gap-4 md:grid-cols-3 mb-6">
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Participants</p>
          <p className="text-2xl font-bold">{order.participant_count}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Items Total</p>
          <p className="text-2xl font-bold">
            ${Number(order.total_amount).toFixed(2)}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Delivery Fee</p>
          <p className="text-2xl font-bold">
            {order.delivery_fee_total
              ? `$${Number(order.delivery_fee_total).toFixed(2)}`
              : "—"}
          </p>
        </Card>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-2 mb-6">
        {canEdit && (
          <Dialog open={addOpen} onOpenChange={setAddOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Add Dish
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Your Dish</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 pt-4">
                <div>
                  <Label>Dish Name</Label>
                  <Input
                    value={itemName}
                    onChange={(e) => setItemName(e.target.value)}
                    placeholder="Burger"
                  />
                </div>
                <div>
                  <Label>Detail (optional)</Label>
                  <Input
                    value={itemDetail}
                    onChange={(e) => setItemDetail(e.target.value)}
                    placeholder="No onions"
                  />
                </div>
                <div>
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
        )}

        {order.status === "confirmed" && canManage && (
          <Dialog open={feeOpen} onOpenChange={setFeeOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <DollarSign className="mr-2 h-4 w-4" />
                Set Delivery Fee
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Set Delivery/Packing Fee</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 pt-4">
                <div>
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

      {/* Items grouped by user */}
      <h2 className="text-xl font-semibold mb-4">Order Items</h2>
      {Object.entries(itemsByUser).length === 0 ? (
        <p className="text-center text-muted-foreground py-8">
          No items yet. Be the first to add your dish!
        </p>
      ) : (
        <div className="space-y-4">
          {Object.entries(itemsByUser).map(([userName, items]) => (
            <div key={userName}>
              <h3 className="font-medium text-sm text-muted-foreground mb-2">
                {userName}
              </h3>
              <div className="space-y-2">
                {items.map((item) => (
                  <Card key={item.id} className="p-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{item.name}</p>
                        {item.detail && (
                          <p className="text-sm text-muted-foreground">
                            {item.detail}
                          </p>
                        )}
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="font-semibold">
                          ${Number(item.price).toFixed(2)}
                        </span>
                        {canEdit &&
                          (item.user_id === user?.id || user?.is_admin) && (
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDeleteItem(item.id)}
                            >
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          )}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
