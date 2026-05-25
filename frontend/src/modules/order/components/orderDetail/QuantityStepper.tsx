import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Minus, Plus } from "lucide-react";

interface QuantityStepperProps {
  value: string;
  onChange: (next: string) => void;
}

export function QuantityStepper({ value, onChange }: QuantityStepperProps) {
  const num = parseInt(value) || 1;

  return (
    <div className="flex items-center gap-2">
      <Button
        type="button"
        variant="outline"
        size="icon"
        className="h-9 w-9 shrink-0"
        onClick={() => onChange(String(Math.max(1, num - 1)))}
        disabled={num <= 1}
      >
        <Minus className="h-4 w-4" />
      </Button>
      <Input
        type="number"
        min="1"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="text-center"
      />
      <Button
        type="button"
        variant="outline"
        size="icon"
        className="h-9 w-9 shrink-0"
        onClick={() => onChange(String(num + 1))}
      >
        <Plus className="h-4 w-4" />
      </Button>
    </div>
  );
}
