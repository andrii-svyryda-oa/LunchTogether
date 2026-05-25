import { Card } from "@/components/ui/card";
import type { OrderDetail, OrderItem } from "@/types";
import { ShoppingCart } from "lucide-react";
import { ParticipantSection } from "./ParticipantSection";

interface ParticipantGroup {
  userId: string;
  name: string;
  items: OrderItem[];
}

interface OrderItemsListProps {
  order: OrderDetail;
  groups: ParticipantGroup[];
  currentUserId?: string;
  canEditInitiated: boolean;
  canEditConfirmed: boolean;
  canEditOwn: boolean;
  canManage: boolean;
  alreadyHaveItem: (item: OrderItem) => boolean;
  onAddForMember: (userId: string) => void;
  onEditItem: (item: OrderItem) => void;
  onDeleteItem: (itemId: string) => void;
  onCopyItemToSelf: (item: OrderItem) => void;
}

export function OrderItemsList({
  order,
  groups,
  currentUserId,
  canEditInitiated,
  canEditConfirmed,
  canEditOwn,
  canManage,
  alreadyHaveItem,
  onAddForMember,
  onEditItem,
  onDeleteItem,
  onCopyItemToSelf,
}: OrderItemsListProps) {
  const deliveryShare = order.delivery_fee_per_person
    ? Number(order.delivery_fee_per_person)
    : 0;

  return (
    <>
      <h2 className="text-xl font-semibold mb-4">Order Items</h2>
      {groups.length === 0 ? (
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
          {groups.map((g) => {
            const subtotal = g.items.reduce(
              (sum, i) => sum + Number(i.price) * (i.quantity ?? 1),
              0,
            );
            return (
              <ParticipantSection
                key={g.userId}
                userId={g.userId}
                name={g.name}
                items={g.items}
                isMe={g.userId === currentUserId}
                subtotal={subtotal}
                deliveryShare={deliveryShare}
                canEditConfirmed={canEditConfirmed}
                currentUserId={currentUserId}
                canEditInitiated={canEditInitiated}
                canEditOwn={canEditOwn}
                canManage={canManage}
                alreadyHaveItem={alreadyHaveItem}
                onAddForMember={onAddForMember}
                onEditItem={onEditItem}
                onDeleteItem={onDeleteItem}
                onCopyItemToSelf={onCopyItemToSelf}
              />
            );
          })}
        </div>
      )}
    </>
  );
}
