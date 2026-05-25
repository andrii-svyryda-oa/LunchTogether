import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { OrderItem } from "@/types";
import { Copy, Pencil, Trash2 } from "lucide-react";

interface OrderItemRowProps {
  item: OrderItem;
  canEdit: boolean;
  canCopyToSelf: boolean;
  onEdit: (item: OrderItem) => void;
  onDelete: (itemId: string) => void;
  onCopyToSelf: (item: OrderItem) => void;
}

export function OrderItemRow({
  item,
  canEdit,
  canCopyToSelf,
  onEdit,
  onDelete,
  onCopyToSelf,
}: OrderItemRowProps) {
  const qty = item.quantity ?? 1;
  const price = Number(item.price);
  const lineTotal = price * qty;

  return (
    <Card className="p-3.5 hover:shadow-md">
      <div className="flex items-center justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <p className="font-medium">{item.name}</p>
            {qty > 1 && (
              <span className="text-xs bg-muted text-muted-foreground px-1.5 py-0.5 rounded-md font-medium">
                x{qty}
              </span>
            )}
          </div>
          {item.detail && (
            <p className="text-sm text-muted-foreground">{item.detail}</p>
          )}
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <span className="font-semibold text-primary">
            {qty > 1
              ? `${price.toFixed(2)} × ${qty} = ${lineTotal.toFixed(2)} ₴`
              : `${price.toFixed(2)} ₴`}
          </span>
          {canCopyToSelf && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => onCopyToSelf(item)}
              title="Add this dish for myself"
              aria-label="Add this dish for myself"
              className="text-muted-foreground hover:text-primary"
            >
              <Copy className="h-4 w-4" />
            </Button>
          )}
          {canEdit && (
            <>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onEdit(item)}
                className="text-muted-foreground hover:text-primary"
              >
                <Pencil className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onDelete(item.id)}
                className="text-muted-foreground hover:text-destructive"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </>
          )}
        </div>
      </div>
    </Card>
  );
}
