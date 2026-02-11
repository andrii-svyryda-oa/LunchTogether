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
import { ChevronDown, ChevronUp, History, Plus, Wallet } from "lucide-react";
import { useState } from "react";
import { useParams } from "react-router-dom";

const AVATAR_GRADIENTS = [
  "from-orange-500 to-amber-500",
  "from-blue-500 to-indigo-500",
  "from-emerald-500 to-teal-500",
  "from-purple-500 to-violet-500",
  "from-pink-500 to-rose-500",
  "from-cyan-500 to-sky-500",
];

function getAvatarGradient(name: string): string {
  const index = (name ?? "?").charCodeAt(0) % AVATAR_GRADIENTS.length;
  return AVATAR_GRADIENTS[index];
}

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
      <div className="flex items-center justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="animate-slide-up">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Balances</h1>
          <p className="text-muted-foreground mt-1">
            Track who owes what in this group.
          </p>
        </div>
        <Dialog open={adjustOpen} onOpenChange={setAdjustOpen}>
          <DialogTrigger asChild>
            <Button className="shadow-md shadow-primary/20">
              <Plus className="mr-2 h-4 w-4" />
              Adjust Balance
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Adjust Balance</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label>Member</Label>
                <select
                  value={adjustUserId}
                  onChange={(e) => setAdjustUserId(e.target.value)}
                  className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  <option value="">Select member</option>
                  {balances?.map((b) => (
                    <option key={b.user_id} value={b.user_id}>
                      {b.user_full_name ?? b.user_id}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label>Amount (positive to add, negative to subtract)</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={adjustAmount}
                  onChange={(e) => setAdjustAmount(e.target.value)}
                  placeholder="10.00"
                />
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
                      <div
                        className={cn(
                          "flex h-10 w-10 items-center justify-center rounded-full bg-linear-to-br text-white text-sm font-bold shrink-0",
                          getAvatarGradient(balance.user_full_name ?? "?"),
                        )}
                      >
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
                            : "text-red-600",
                        )}
                      >
                        ${Number(balance.amount).toFixed(2)}
                      </span>
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
                                    : "bg-amber-50 text-amber-600",
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
                                    : "text-red-600",
                                )}
                              >
                                {Number(entry.amount) >= 0 ? "+" : ""}$
                                {Number(entry.amount).toFixed(2)}
                              </span>
                              <span className="text-muted-foreground text-xs">
                                = ${Number(entry.balance_after).toFixed(2)}
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
