import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { OrderItem } from "@/types";
import { useEffect, useState } from "react";
import { QuantityStepper } from "./QuantityStepper";

interface EditItemDialogProps {
  /** Non-null when the dialog should be open. */
  item: OrderItem | null;
  onOpenChange: (open: boolean) => void;
  onSubmit: (
    itemId: string,
    data: { name: string; detail?: string; price: number; quantity: number },
  ) => Promise<void>;
}

export function EditItemDialog({
  item,
  onOpenChange,
  onSubmit,
}: EditItemDialogProps) {
  const [name, setName] = useState("");
  const [detail, setDetail] = useState("");
  const [price, setPrice] = useState("");
  const [quantity, setQuantity] = useState("1");

  useEffect(() => {
    if (item) {
      setName(item.name);
      setDetail(item.detail ?? "");
      setPrice(String(item.price));
      setQuantity(String(item.quantity ?? 1));
    }
  }, [item]);

  const handleSubmit = async () => {
    if (!item) return;
    try {
      await onSubmit(item.id, {
        name,
        detail: detail || undefined,
        price: parseFloat(price),
        quantity: parseInt(quantity) || 1,
      });
      onOpenChange(false);
    } catch {
      // handled
    }
  };

  return (
    <Dialog open={item !== null} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Dish</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 pt-4">
          <div className="space-y-2">
            <Label>Dish Name</Label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Burger"
            />
          </div>
          <div className="space-y-2">
            <Label>Detail (optional)</Label>
            <Input
              value={detail}
              onChange={(e) => setDetail(e.target.value)}
              placeholder="No onions"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Price</Label>
              <Input
                type="number"
                step="0.01"
                min="0"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                placeholder="9.99"
              />
            </div>
            <div className="space-y-2">
              <Label>Quantity</Label>
              <QuantityStepper value={quantity} onChange={setQuantity} />
            </div>
          </div>
          <Button
            onClick={handleSubmit}
            disabled={!name.trim() || !price}
            className="w-full"
          >
            Save Changes
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
