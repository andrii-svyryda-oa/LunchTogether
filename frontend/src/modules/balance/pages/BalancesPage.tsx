import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks";
import {
  useAdjustBalanceMutation,
  useGetBalanceHistoryQuery,
  useGetBalancesQuery,
} from "@/store/api/balanceApi";
import type { Balance } from "@/types";
import { cn } from "@/utils";
import { ChevronUp, History, Plus, Wallet } from "lucide-react";
import { useState } from "react";
import { useParams } from "react-router-dom";

export function BalancesPage() {
  const { groupId } = useParams<{ groupId: string }>();
  const { user } = useAuth();
  const { data: balances, isLoading } = useGetBalancesQuery(groupId!);
  const [adjustBalance] = useAdjustBalanceMutation();

  // Adjust state — tracks which user's dialog is open
  const [adjustTarget, setAdjustTarget] = useState<Balance | null>(null);
  const [adjustAmount, setAdjustAmount] = useState("");
  const [adjustNote, setAdjustNote] = useState("");

  // History state
  const [historyUserId, setHistoryUserId] = useState<string | null>(null);
  const { data: history } = useGetBalanceHistoryQuery(
    { groupId: groupId!, userId: historyUserId! },
    { skip: !historyUserId }
  );

  const openAdjustDialog = (balance: Balance) => {
    setAdjustTarget(balance);
    setAdjustAmount("");
    setAdjustNote("");
  };

  const closeAdjustDialog = () => {
    setAdjustTarget(null);
    setAdjustAmount("");
    setAdjustNote("");
  };

  const handleAdjust = async () => {
    if (!adjustTarget) return;
    try {
      await adjustBalance({
        groupId: groupId!,
        data: {
          user_id: adjustTarget.user_id,
          amount: parseFloat(adjustAmount),
          note: adjustNote || undefined,
        },
      }).unwrap();
      closeAdjustDialog();
    } catch {
      // handled
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Balances</h1>
        <p className="text-muted-foreground mt-1">
          Track who owes what in this group.
        </p>
      </div>

      {/* Per-person adjust dialog */}
      <Dialog open={!!adjustTarget} onOpenChange={(open) => !open && closeAdjustDialog()}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              Adjust Balance — {adjustTarget?.user_full_name ?? "Member"}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 pt-4">
            <div className="space-y-2">
              <Label>Amount (positive to add, negative to subtract)</Label>
              <Input
                type="number"
                step="0.01"
                value={adjustAmount}
                onChange={(e) => setAdjustAmount(e.target.value)}
                placeholder="10.00"
              />
              {adjustTarget && Number(adjustTarget.amount) < 0 && (
                <button
                  type="button"
                  className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold text-muted-foreground cursor-pointer hover:bg-accent transition-colors"
                  onClick={() =>
                    setAdjustAmount(String(Math.abs(Number(adjustTarget.amount))))
                  }
                >
                  +{Math.abs(Number(adjustTarget.amount)).toFixed(2)}
                </button>
              )}
            </div>
            <div className="space-y-2">
              <Label>Note (optional)</Label>
              <Input
                value={adjustNote}
                onChange={(e) => setAdjustNote(e.target.value)}
                placeholder="Payment received"
              />
            </div>
            <Button
              onClick={handleAdjust}
              disabled={!adjustAmount}
              className="w-full"
            >
              Apply Adjustment
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Balance list */}
      {balances && balances.length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-16 border-dashed">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-muted mb-4">
            <Wallet className="h-7 w-7 text-muted-foreground" />
          </div>
          <p className="text-muted-foreground font-medium">No balances yet</p>
        </Card>
      ) : (
        <div className="space-y-3 mb-8">
          {balances?.map((balance) => {
            const isExpanded = historyUserId === balance.user_id;
            return (
              <Card
                key={balance.id}
                className={cn("hover:shadow-md", isExpanded && "shadow-md")}
              >
                <div className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-bold shrink-0">
                        {(balance.user_full_name ?? "?")
                          .charAt(0)
                          .toUpperCase()}
                      </div>
                      <div>
                        <p className="font-medium">{balance.user_full_name}</p>
                        {balance.user_id === user?.id && (
                          <span className="text-[11px] font-medium bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">
                            You
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span
                        className={cn(
                          "text-lg font-bold",
                          Number(balance.amount) >= 0
                            ? "text-emerald-600"
                            : "text-red-600"
                        )}
                      >
                        {Number(balance.amount).toFixed(2)} ₴
                      </span>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => openAdjustDialog(balance)}
                        className="text-muted-foreground"
                        title="Adjust balance"
                      >
                        <Plus className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() =>
                          setHistoryUserId(isExpanded ? null : balance.user_id)
                        }
                        className="text-muted-foreground"
                      >
                        {isExpanded ? (
                          <ChevronUp className="h-4 w-4" />
                        ) : (
                          <History className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Inline history */}
                {isExpanded && history && (
                  <div className="border-t px-4 py-4 bg-muted/30">
                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                      History
                    </p>
                    {history.length === 0 ? (
                      <p className="text-sm text-muted-foreground">
                        No history yet.
                      </p>
                    ) : (
                      <div className="space-y-2.5">
                        {history.map((entry) => (
                          <div
                            key={entry.id}
                            className="flex items-center justify-between text-sm"
                          >
                            <div className="flex items-center gap-2">
                              <span
                                className={cn(
                                  "text-[11px] font-medium px-2 py-0.5 rounded-full",
                                  entry.change_type === "order"
                                    ? "bg-blue-50 text-blue-600"
                                    : "bg-amber-50 text-amber-600"
                                )}
                              >
                                {entry.change_type === "order"
                                  ? "Order"
                                  : "Manual"}
                              </span>
                              {entry.note && (
                                <span className="text-muted-foreground">
                                  {entry.note}
                                </span>
                              )}
                              {entry.created_by_name && (
                                <span className="text-muted-foreground">
                                  by {entry.created_by_name}
                                </span>
                              )}
                            </div>
                            <div className="flex items-center gap-3 shrink-0">
                              <span
                                className={cn(
                                  "font-medium",
                                  Number(entry.amount) >= 0
                                    ? "text-emerald-600"
                                    : "text-red-600"
                                )}
                              >
                                {Number(entry.amount) >= 0 ? "+" : ""}
                                {Number(entry.amount).toFixed(2)} ₴
                              </span>
                              <span className="text-muted-foreground text-xs">
                                = {Number(entry.balance_after).toFixed(2)} ₴
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
