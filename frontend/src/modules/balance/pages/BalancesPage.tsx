import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks";
import {
  useAdjustBalanceMutation,
  useGetBalanceHistoryQuery,
  useGetBalancesQuery,
} from "@/store/api/balanceApi";
import { cn } from "@/utils";
import { History, Plus } from "lucide-react";
import { useState } from "react";
import { useParams } from "react-router-dom";

export function BalancesPage() {
  const { groupId } = useParams<{ groupId: string }>();
  const { user } = useAuth();
  const { data: balances, isLoading } = useGetBalancesQuery(groupId!);
  const [adjustBalance] = useAdjustBalanceMutation();

  // Adjust state
  const [adjustOpen, setAdjustOpen] = useState(false);
  const [adjustUserId, setAdjustUserId] = useState("");
  const [adjustAmount, setAdjustAmount] = useState("");
  const [adjustNote, setAdjustNote] = useState("");

  // History state
  const [historyUserId, setHistoryUserId] = useState<string | null>(null);
  const { data: history } = useGetBalanceHistoryQuery(
    { groupId: groupId!, userId: historyUserId! },
    { skip: !historyUserId },
  );

  const handleAdjust = async () => {
    try {
      await adjustBalance({
        groupId: groupId!,
        data: {
          user_id: adjustUserId,
          amount: parseFloat(adjustAmount),
          note: adjustNote || undefined,
        },
      }).unwrap();
      setAdjustOpen(false);
      setAdjustUserId("");
      setAdjustAmount("");
      setAdjustNote("");
    } catch {
      // handled
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Balances</h1>
        <Dialog open={adjustOpen} onOpenChange={setAdjustOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Adjust Balance
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Adjust Balance</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div>
                <Label>Member</Label>
                <select
                  value={adjustUserId}
                  onChange={(e) => setAdjustUserId(e.target.value)}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="">Select member</option>
                  {balances?.map((b) => (
                    <option key={b.user_id} value={b.user_id}>
                      {b.user_full_name ?? b.user_id}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <Label>Amount (positive to add, negative to subtract)</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={adjustAmount}
                  onChange={(e) => setAdjustAmount(e.target.value)}
                  placeholder="10.00"
                />
              </div>
              <div>
                <Label>Note (optional)</Label>
                <Input
                  value={adjustNote}
                  onChange={(e) => setAdjustNote(e.target.value)}
                  placeholder="Payment received"
                />
              </div>
              <Button
                onClick={handleAdjust}
                disabled={!adjustUserId || !adjustAmount}
                className="w-full"
              >
                Apply Adjustment
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Balance list */}
      <div className="space-y-3 mb-8">
        {balances?.map((balance) => (
          <Card key={balance.id} className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">{balance.user_full_name}</p>
              </div>
              <div className="flex items-center gap-3">
                <span
                  className={cn(
                    "text-lg font-bold",
                    Number(balance.amount) >= 0
                      ? "text-green-600"
                      : "text-red-600",
                  )}
                >
                  ${Number(balance.amount).toFixed(2)}
                </span>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() =>
                    setHistoryUserId(
                      historyUserId === balance.user_id
                        ? null
                        : balance.user_id,
                    )
                  }
                >
                  <History className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Inline history */}
            {historyUserId === balance.user_id && history && (
              <div className="mt-4 border-t pt-4 space-y-2">
                <p className="text-sm font-medium text-muted-foreground">
                  History
                </p>
                {history.length === 0 ? (
                  <p className="text-sm text-muted-foreground">
                    No history yet.
                  </p>
                ) : (
                  history.map((entry) => (
                    <div
                      key={entry.id}
                      className="flex items-center justify-between text-sm"
                    >
                      <div>
                        <span className="font-medium">
                          {entry.change_type === "order" ? "Order" : "Manual"}
                        </span>
                        {entry.note && (
                          <span className="text-muted-foreground ml-2">
                            {entry.note}
                          </span>
                        )}
                        {entry.created_by_name && (
                          <span className="text-muted-foreground ml-2">
                            by {entry.created_by_name}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-3">
                        <span
                          className={cn(
                            "font-medium",
                            Number(entry.amount) >= 0
                              ? "text-green-600"
                              : "text-red-600",
                          )}
                        >
                          {Number(entry.amount) >= 0 ? "+" : ""}$
                          {Number(entry.amount).toFixed(2)}
                        </span>
                        <span className="text-muted-foreground">
                          = ${Number(entry.balance_after).toFixed(2)}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
