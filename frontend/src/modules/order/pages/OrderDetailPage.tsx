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
import {
  DollarSign,
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

const AVATAR_GRADIENTS = [
  "from-orange-500 to-amber-500",
  "from-blue-500 to-indigo-500",
  "from-emerald-500 to-teal-500",
  "from-purple-500 to-violet-500",
  "from-pink-500 to-rose-500",
  "from-cyan-500 to-sky-500",
];

function getAvatarGradient(name: string): string {
  const index = (name ?? "?").charCodeAt(0) % AVATAR_GRADIENTS.length;
  return AVATAR_GRADIENTS[index];
}

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
      <div className="flex items-center justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error || !order) {
    return <Alert variant="destructive">Failed to load order.</Alert>;
  }

  const isInitiator = order.initiator_id === user?.id;
  const canEdit = order.status === "initiated";
  const canManage = isInitiator || user?.role === "admin";
  const nextAction = NEXT_STATUS[order.status];
  const style = STATUS_STYLES[order.status] ?? STATUS_STYLES.initiated;

  // Group items by user
  const itemsByUser = order.items.reduce((acc, item) => {
    const key = item.user_full_name ?? item.user_id;
    if (!acc[key]) acc[key] = [];
    acc[key].push(item);
    return acc;
  }, {} as Record<string, typeof order.items>);

  return (
    <div className="animate-slide-up">
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

        <Card className="p-5 hover:shadow-md group">
          <div className="flex items-center gap-3 mb-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-50 text-purple-600 group-hover:scale-105 transition-transform">
              <Truck className="h-5 w-5" />
            </div>
            <p className="text-sm font-medium text-muted-foreground">
              Delivery Fee
            </p>
          </div>
          <p className="text-2xl font-bold">
            {order.delivery_fee_total
              ? `${Number(order.delivery_fee_total).toFixed(2)} ₴`
              : "\u2014"}
          </p>
        </Card>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-2 mb-8">
        {canEdit && (
          <Dialog open={addOpen} onOpenChange={setAddOpen}>
            <DialogTrigger asChild>
              <Button className="shadow-md shadow-primary/20">
                <Plus className="mr-2 h-4 w-4" />
                Add Dish
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Your Dish</DialogTitle>
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
          {Object.entries(itemsByUser).map(([userName, items]) => (
            <div key={userName}>
              <div className="flex items-center gap-2 mb-3">
                <div
                  className={cn(
                    "flex h-7 w-7 items-center justify-center rounded-full bg-linear-to-br text-white text-[11px] font-bold shrink-0",
                    getAvatarGradient(userName),
                  )}
                >
                  {userName.charAt(0).toUpperCase()}
                </div>
                <h3 className="font-medium text-sm">{userName}</h3>
              </div>
              <div className="space-y-2 ml-9">
                {items.map((item) => (
                  <Card key={item.id} className="p-3.5 hover:shadow-md">
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
                        <span className="font-semibold text-primary">
                          {Number(item.price).toFixed(2)} ₴
                        </span>
                        {canEdit &&
                          (item.user_id === user?.id ||
                            user?.role === "admin") && (
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDeleteItem(item.id)}
                              className="text-muted-foreground hover:text-destructive"
                            >
                              <Trash2 className="h-4 w-4" />
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
