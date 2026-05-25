import { Button } from "@/components/ui/button";
import type { OrderDetail } from "@/types";
import { cn } from "@/utils";
import { ClipboardCheck } from "lucide-react";
import { STATUS_STYLES } from "./statusStyles";

interface OrderHeaderProps {
  order: OrderDetail;
  canManage: boolean;
  onTransition: (status: string) => void;
  onOpenOrderDialog: () => void;
}

export function OrderHeader({
  order,
  canManage,
  onTransition,
  onOpenOrderDialog,
}: OrderHeaderProps) {
  const style = STATUS_STYLES[order.status] ?? STATUS_STYLES.initiated;
  const showCancel =
    canManage && order.status !== "finished" && order.status !== "cancelled";

  return (
    <div className="flex flex-wrap items-start justify-between gap-4 mb-8">
      <div>
        <div className="flex items-center gap-3 mb-1 flex-wrap">
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

      <div className="flex flex-wrap items-center gap-2">
        {canManage && order.status === "initiated" && (
          <Button onClick={() => onTransition("confirmed")}>
            Confirm Order
          </Button>
        )}

        {canManage &&
          order.status === "confirmed" &&
          order.items.length > 0 && (
            <Button onClick={onOpenOrderDialog}>
              <ClipboardCheck className="mr-2 h-4 w-4" />
              Order
            </Button>
          )}

        {canManage && order.status === "ordered" && (
          <Button onClick={() => onTransition("finished")}>
            Mark as Finished
          </Button>
        )}

        {showCancel && (
          <Button
            variant="destructive"
            onClick={() => onTransition("cancelled")}
          >
            Cancel Order
          </Button>
        )}
      </div>
    </div>
  );
}
