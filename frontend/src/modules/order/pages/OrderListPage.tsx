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
import {
  useCreateOrderMutation,
  useGetOrdersQuery,
} from "@/store/api/orderApi";
import { useGetRestaurantsQuery } from "@/store/api/restaurantApi";
import { cn } from "@/utils";
import { ArrowRight, Plus } from "lucide-react";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";

const STATUS_COLORS: Record<string, string> = {
  initiated: "bg-blue-100 text-blue-700",
  confirmed: "bg-yellow-100 text-yellow-700",
  ordered: "bg-purple-100 text-purple-700",
  finished: "bg-green-100 text-green-700",
  cancelled: "bg-red-100 text-red-700",
};

export function OrderListPage() {
  const { groupId } = useParams<{ groupId: string }>();
  const { data: orders, isLoading } = useGetOrdersQuery(groupId!);
  const { data: restaurants } = useGetRestaurantsQuery(groupId!);
  const [createOrder] = useCreateOrderMutation();

  const [open, setOpen] = useState(false);
  const [selectedRestaurant, setSelectedRestaurant] = useState("");
  const [customName, setCustomName] = useState("");

  const handleCreate = async () => {
    try {
      await createOrder({
        groupId: groupId!,
        data: {
          restaurant_id: selectedRestaurant || undefined,
          restaurant_name: !selectedRestaurant
            ? customName || undefined
            : undefined,
        },
      }).unwrap();
      setOpen(false);
      setSelectedRestaurant("");
      setCustomName("");
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

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Orders</h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Order
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Start New Order</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div>
                <Label>Restaurant (optional)</Label>
                <select
                  value={selectedRestaurant}
                  onChange={(e) => setSelectedRestaurant(e.target.value)}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="">Select or enter custom name</option>
                  {restaurants?.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.name}
                    </option>
                  ))}
                </select>
              </div>
              {!selectedRestaurant && (
                <div>
                  <Label>Custom Restaurant Name</Label>
                  <Input
                    value={customName}
                    onChange={(e) => setCustomName(e.target.value)}
                    placeholder="New place on Main St."
                  />
                </div>
              )}
              <Button onClick={handleCreate} className="w-full">
                Start Order
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {orders && orders.length === 0 ? (
        <p className="text-center text-muted-foreground py-12">
          No orders yet. Start one!
        </p>
      ) : (
        <div className="space-y-3">
          {orders?.map((order) => (
            <Link key={order.id} to={`/groups/${groupId}/orders/${order.id}`}>
              <Card className="p-4 hover:border-primary transition-colors cursor-pointer mb-2">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">
                      {order.restaurant_name ?? "Custom Order"}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(order.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span
                      className={cn(
                        "text-xs px-2 py-1 rounded font-medium",
                        STATUS_COLORS[order.status] ??
                          "bg-gray-100 text-gray-700",
                      )}
                    >
                      {order.status}
                    </span>
                    <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
