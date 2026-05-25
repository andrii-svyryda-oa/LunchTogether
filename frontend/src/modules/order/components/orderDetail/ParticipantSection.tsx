import { Button } from "@/components/ui/button";
import type { OrderItem } from "@/types";
import { cn } from "@/utils";
import { Plus } from "lucide-react";
import { OrderItemRow } from "./OrderItemRow";

interface ParticipantSectionProps {
  userId: string;
  name: string;
  items: OrderItem[];
  isMe: boolean;
  subtotal: number;
  deliveryShare: number;
  canEditConfirmed: boolean;
  currentUserId?: string;
  canEditInitiated: boolean;
  canEditOwn: boolean;
  canManage: boolean;
  alreadyHaveItem: (item: OrderItem) => boolean;
  onAddForMember: (userId: string) => void;
  onEditItem: (item: OrderItem) => void;
  onDeleteItem: (itemId: string) => void;
  onCopyItemToSelf: (item: OrderItem) => void;
}

export function ParticipantSection({
  userId,
  name,
  items,
  isMe,
  subtotal,
  deliveryShare,
  canEditConfirmed,
  currentUserId,
  canEditInitiated,
  canEditOwn,
  canManage,
  alreadyHaveItem,
  onAddForMember,
  onEditItem,
  onDeleteItem,
  onCopyItemToSelf,
}: ParticipantSectionProps) {
  const memberTotal = subtotal + deliveryShare;

  return (
    <div
      className={
        isMe
          ? "rounded-2xl border border-primary/30 bg-primary/5 p-4 -mx-1 -mt-1 mb-3"
          : undefined
      }
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div
            className={cn(
              "flex h-7 w-7 items-center justify-center rounded-full text-[11px] font-bold shrink-0 bg-primary text-primary-foreground",
              isMe && "ring-2 ring-primary/30",
            )}
          >
            {name.charAt(0).toUpperCase()}
          </div>
          <h3 className="font-medium text-sm">{name}</h3>
          {isMe && (
            <span className="text-[10px] uppercase tracking-wide bg-primary text-primary-foreground px-1.5 py-0.5 rounded-md font-semibold">
              You
            </span>
          )}
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
            onClick={() => onAddForMember(userId)}
            className="text-muted-foreground hover:text-primary"
          >
            <Plus className="h-4 w-4 mr-1" />
            Add
          </Button>
        )}
      </div>
      <div className="space-y-2 ml-9">
        {items.map((item) => {
          const isItemMine = item.user_id === currentUserId;
          const canCopyToSelf =
            canEditInitiated && !isItemMine && !alreadyHaveItem(item);
          const canEdit =
            canEditOwn && (canEditConfirmed || isItemMine || canManage);
          return (
            <OrderItemRow
              key={item.id}
              item={item}
              canEdit={canEdit}
              canCopyToSelf={canCopyToSelf}
              onEdit={onEditItem}
              onDelete={onDeleteItem}
              onCopyToSelf={onCopyItemToSelf}
            />
          );
        })}
      </div>
    </div>
  );
}
