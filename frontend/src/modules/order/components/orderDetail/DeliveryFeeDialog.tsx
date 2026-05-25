import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useSetDeliveryFeeMutation } from "@/store/api/orderApi";
import { useEffect, useState } from "react";

interface DeliveryFeeDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  groupId: string;
  orderId: string;
}

export function DeliveryFeeDialog({
  open,
  onOpenChange,
  groupId,
  orderId,
}: DeliveryFeeDialogProps) {
  const [feeTotal, setFeeTotal] = useState("");
  const [setDeliveryFee] = useSetDeliveryFeeMutation();

  useEffect(() => {
    if (!open) setFeeTotal("");
  }, [open]);

  const handleSubmit = async () => {
    try {
      await setDeliveryFee({
        groupId,
        orderId,
        data: { delivery_fee_total: parseFloat(feeTotal) },
      }).unwrap();
      onOpenChange(false);
    } catch {
      // handled
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Set Delivery/Packing Fee</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 pt-4">
          <div className="space-y-2">
            <Label>Total Fee (divided equally)</Label>
            <Input
              type="number"
              step="0.01"
              min="0"
              value={feeTotal}
              onChange={(e) => setFeeTotal(e.target.value)}
              placeholder="5.00"
            />
          </div>
          <Button
            onClick={handleSubmit}
            disabled={!feeTotal}
            className="w-full"
          >
            Set Fee
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
