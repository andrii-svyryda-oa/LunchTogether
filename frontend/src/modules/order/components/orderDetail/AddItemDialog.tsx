import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { Dish } from "@/types";
import { useEffect, useState } from "react";
import { QuantityStepper } from "./QuantityStepper";

interface AddItemDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** When set, dialog is "Add Dish for Member"; null/undefined → "Add Your Dish". */
  forUserId: string | null;
  currentUserId?: string;
  dishes?: Dish[];
  isDuplicateDish: (dish: Dish) => boolean;
  onSubmit: (data: {
    name: string;
    detail?: string;
    price: number;
    quantity: number;
    user_id?: string;
    dish_id?: string;
  }) => Promise<void>;
}

export function AddItemDialog({
  open,
  onOpenChange,
  forUserId,
  currentUserId,
  dishes,
  isDuplicateDish,
  onSubmit,
}: AddItemDialogProps) {
  const [name, setName] = useState("");
  const [detail, setDetail] = useState("");
  const [price, setPrice] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [selectedDishId, setSelectedDishId] = useState<string | null>(null);

  useEffect(() => {
    if (!open) {
      setName("");
      setDetail("");
      setPrice("");
      setQuantity("1");
      setSelectedDishId(null);
    }
  }, [open]);

  const handleSubmit = async () => {
    try {
      await onSubmit({
        name,
        detail: detail || undefined,
        price: parseFloat(price),
        quantity: parseInt(quantity) || 1,
        user_id: forUserId || undefined,
        dish_id: selectedDishId || undefined,
      });
      onOpenChange(false);
    } catch {
      // handled
    }
  };

  const title = forUserId
    ? `Add Dish${forUserId !== currentUserId ? " for Member" : ""}`
    : "Add Your Dish";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 pt-4">
          {dishes && dishes.length > 0 && (
            <div className="space-y-2">
              <Label>Choose from menu</Label>
              <div className="max-h-48 overflow-y-auto space-y-1 rounded-md border p-1">
                {dishes.map((dish) => {
                  const duplicate = isDuplicateDish(dish);
                  return (
                    <Button
                      key={dish.id}
                      type="button"
                      variant={
                        selectedDishId === dish.id ? "default" : "outline"
                      }
                      className="w-full justify-between h-auto py-2 px-3"
                      disabled={duplicate}
                      title={
                        duplicate
                          ? "Already in this person's order"
                          : undefined
                      }
                      onClick={() => {
                        setSelectedDishId(dish.id);
                        setName(dish.name);
                        setDetail(dish.detail ?? "");
                        setPrice(String(dish.price));
                      }}
                    >
                      <span className="font-medium text-sm">{dish.name}</span>
                      <span className="text-sm text-muted-foreground ml-2 shrink-0">
                        {duplicate
                          ? "Already added"
                          : `${Number(dish.price).toFixed(2)} ₴`}
                      </span>
                    </Button>
                  );
                })}
              </div>
            </div>
          )}
          <div className="space-y-2">
            <Label>Dish Name</Label>
            <Input
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                setSelectedDishId(null);
              }}
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
                onChange={(e) => {
                  setPrice(e.target.value);
                  setSelectedDishId(null);
                }}
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
            Add
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
