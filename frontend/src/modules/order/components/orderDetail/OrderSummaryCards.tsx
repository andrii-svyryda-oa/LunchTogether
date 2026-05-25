import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { OrderDetail } from "@/types";
import { DollarSign, Pencil, Truck, Users } from "lucide-react";

interface OrderSummaryCardsProps {
  order: OrderDetail;
  canEditFee: boolean;
  onEditFee: () => void;
}

export function OrderSummaryCards({
  order,
  canEditFee,
  onEditFee,
}: OrderSummaryCardsProps) {
  return (
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

      <Card className="p-5 hover:shadow-md group relative">
        <div className="flex items-center gap-3 mb-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-50 text-purple-600 group-hover:scale-105 transition-transform">
            <Truck className="h-5 w-5" />
          </div>
          <p className="text-sm font-medium text-muted-foreground">
            Delivery Fee
          </p>
          {canEditFee && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onEditFee}
              className="absolute top-3 right-3 h-7 w-7 text-muted-foreground hover:text-primary"
            >
              <Pencil className="h-3.5 w-3.5" />
            </Button>
          )}
        </div>
        <p className="text-2xl font-bold">
          {order.delivery_fee_total
            ? `${Number(order.delivery_fee_total).toFixed(2)} ₴`
            : "—"}
        </p>
      </Card>
    </div>
  );
}
