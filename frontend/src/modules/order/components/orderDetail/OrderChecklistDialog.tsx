import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { cn } from "@/utils";
import type { AggregatedRow } from "../../hooks/useOrderChecklist";

interface OrderChecklistDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  aggregated: AggregatedRow[];
  checkedKeys: Set<string>;
  onToggle: (key: string) => void;
  onReset: () => void;
  /** When true, shows the bottom "Order" submit button. */
  showOrderButton: boolean;
  onOrder: () => void;
}

export function OrderChecklistDialog({
  open,
  onOpenChange,
  aggregated,
  checkedKeys,
  onToggle,
  onReset,
  showOrderButton,
  onOrder,
}: OrderChecklistDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Place the Order</DialogTitle>
        </DialogHeader>
        <p className="text-sm text-muted-foreground pt-2">
          Tick items off as you place them with the restaurant. Checking
          everything is optional &mdash; when you&apos;re ready, hit{" "}
          <span className="font-medium text-foreground">Order</span>.
        </p>
        <div className="space-y-2 pt-3 max-h-[50vh] overflow-y-auto">
          {aggregated.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              No items to aggregate.
            </p>
          ) : (
            aggregated.map((row) => {
              const isChecked = checkedKeys.has(row.key);
              return (
                <label
                  key={row.key}
                  className={cn(
                    "flex items-center gap-3 rounded-lg border p-3 cursor-pointer transition-colors",
                    isChecked
                      ? "bg-muted/50 border-muted"
                      : "hover:bg-muted/30",
                  )}
                >
                  <input
                    type="checkbox"
                    checked={isChecked}
                    onChange={() => onToggle(row.key)}
                    className="h-4 w-4 shrink-0 accent-primary cursor-pointer"
                  />
                  <div className="min-w-0 flex-1">
                    <p
                      className={cn(
                        "font-medium",
                        isChecked && "line-through text-muted-foreground",
                      )}
                    >
                      {row.name}
                    </p>
                    {row.detail && (
                      <p
                        className={cn(
                          "text-sm text-muted-foreground",
                          isChecked && "line-through",
                        )}
                      >
                        {row.detail}
                      </p>
                    )}
                  </div>
                  <span
                    className={cn(
                      "text-sm font-semibold shrink-0",
                      isChecked ? "text-muted-foreground" : "text-primary",
                    )}
                  >
                    ×{row.quantity}
                  </span>
                </label>
              );
            })
          )}
        </div>
        {aggregated.length > 0 && (
          <div className="flex items-center justify-between pt-2 text-xs text-muted-foreground">
            <span>
              {checkedKeys.size} / {aggregated.length} checked
            </span>
            {checkedKeys.size > 0 && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={onReset}
                className="h-7 text-xs"
              >
                Reset
              </Button>
            )}
          </div>
        )}
        {showOrderButton && (
          <Button
            onClick={onOrder}
            className="w-full mt-2"
            disabled={aggregated.length === 0}
          >
            Order
          </Button>
        )}
      </DialogContent>
    </Dialog>
  );
}
