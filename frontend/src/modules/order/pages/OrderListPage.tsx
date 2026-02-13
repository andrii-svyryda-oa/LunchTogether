import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Combobox } from "@/components/ui/combobox";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  useCreateOrderMutation,
  useGetOrdersQuery,
} from "@/store/api/orderApi";
import { useGetRestaurantsQuery } from "@/store/api/restaurantApi";
import { cn } from "@/utils";
import { ArrowRight, Plus, ShoppingCart } from "lucide-react";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";

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

  const restaurantOptions = (restaurants ?? []).map((r) => ({
    value: r.id,
    label: r.name,
  }));

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Orders</h1>
          <p className="text-muted-foreground mt-1">
            View and manage all group orders.
          </p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="shadow-md shadow-primary/20">
              <Plus className="mr-2 h-4 w-4" />
              New Order
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Start New Order</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label>Restaurant</Label>
                <Combobox
                  options={restaurantOptions}
                  value={selectedRestaurant}
                  onChange={(val) => {
                    setSelectedRestaurant(val);
                    if (val) setCustomName("");
                  }}
                  placeholder="Select or type to create..."
                  searchPlaceholder="Search restaurants..."
                  emptyText="No restaurants found."
                  allowCreate
                  createLabel="Create"
                  onCreateNew={(name) => {
                    setSelectedRestaurant("");
                    setCustomName(name);
                  }}
                />
                {customName && !selectedRestaurant && (
                  <p className="text-sm text-muted-foreground">
                    New restaurant:{" "}
                    <span className="font-medium text-foreground">
                      {customName}
                    </span>
                  </p>
                )}
              </div>
              <Button onClick={handleCreate} className="w-full">
                Start Order
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {orders && orders.length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-16 border-dashed">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-muted mb-4">
            <ShoppingCart className="h-7 w-7 text-muted-foreground" />
          </div>
          <p className="text-muted-foreground font-medium mb-1">
            No orders yet
          </p>
          <p className="text-sm text-muted-foreground">
            Start one to get the team&apos;s lunch going!
          </p>
        </Card>
      ) : (
        <div className="space-y-3">
          {orders?.map((order) => {
            const style =
              STATUS_STYLES[order.status] ?? STATUS_STYLES.initiated;
            return (
              <Link key={order.id} to={`/groups/${groupId}/orders/${order.id}`}>
                <Card className="p-4 hover:shadow-md hover:border-primary/30 cursor-pointer group mb-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-muted shrink-0">
                        <ShoppingCart className="h-5 w-5 text-muted-foreground" />
                      </div>
                      <div>
                        <p className="font-medium">
                          {order.restaurant_name ?? "Custom Order"}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(order.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span
                        className={cn(
                          "inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full font-medium",
                          style.bg,
                          style.text
                        )}
                      >
                        <span
                          className={cn("h-1.5 w-1.5 rounded-full", style.dot)}
                        />
                        {order.status}
                      </span>
                      <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                  </div>
                </Card>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
