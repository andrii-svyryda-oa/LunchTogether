import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useAuth } from "@/hooks";
import { useGetGroupAnalyticsQuery } from "@/store/api/analyticsApi";
import { useGetMyBalanceQuery } from "@/store/api/balanceApi";
import { useGetGroupQuery } from "@/store/api/groupApi";
import { useGetActiveOrderQuery } from "@/store/api/orderApi";
import { cn } from "@/utils";
import {
  ArrowRight,
  DollarSign,
  ShoppingCart,
  TrendingUp,
  Users,
  UtensilsCrossed,
  Wallet,
} from "lucide-react";
import { Link, useParams } from "react-router-dom";

const GROUP_GRADIENTS = [
  "from-orange-500 to-amber-500",
  "from-blue-500 to-indigo-500",
  "from-emerald-500 to-teal-500",
  "from-purple-500 to-violet-500",
  "from-pink-500 to-rose-500",
  "from-cyan-500 to-sky-500",
];

function getGroupGradient(name: string): string {
  const index = name.charCodeAt(0) % GROUP_GRADIENTS.length;
  return GROUP_GRADIENTS[index];
}

export function GroupDetailPage() {
  const { groupId } = useParams<{ groupId: string }>();
  const { user } = useAuth();
  const { data: group, isLoading, error } = useGetGroupQuery(groupId!);
  const { data: activeOrder } = useGetActiveOrderQuery(groupId!);
  const { data: analytics } = useGetGroupAnalyticsQuery(groupId!);
  const { data: myBalance } = useGetMyBalanceQuery(groupId!);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error || !group) {
    return <Alert variant="destructive">Failed to load group.</Alert>;
  }

  const isOwner = group.owner_id === user?.id;

  return (
    <div className="animate-slide-up">
      {/* Group header */}
      <div className="flex items-center gap-4 mb-8">
        <div
          className={cn(
            "flex h-14 w-14 items-center justify-center rounded-2xl bg-linear-to-br text-white font-bold text-2xl shadow-lg shrink-0",
            getGroupGradient(group.name),
          )}
        >
          {group.name.charAt(0).toUpperCase()}
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{group.name}</h1>
          {group.description && (
            <p className="text-muted-foreground">{group.description}</p>
          )}
        </div>
      </div>

      {/* Quick nav links */}
      <div className="flex flex-wrap gap-2 mb-8">
        <Button variant="outline" size="sm" asChild className="rounded-full">
          <Link to={`/groups/${groupId}/members`}>
            <Users className="mr-2 h-4 w-4" />
            Members ({group.members?.length ?? 0})
          </Link>
        </Button>
        <Button variant="outline" size="sm" asChild className="rounded-full">
          <Link to={`/groups/${groupId}/restaurants`}>
            <UtensilsCrossed className="mr-2 h-4 w-4" />
            Restaurants
          </Link>
        </Button>
        <Button variant="outline" size="sm" asChild className="rounded-full">
          <Link to={`/groups/${groupId}/orders`}>
            <ShoppingCart className="mr-2 h-4 w-4" />
            Orders
          </Link>
        </Button>
        <Button variant="outline" size="sm" asChild className="rounded-full">
          <Link to={`/groups/${groupId}/balances`}>
            <Wallet className="mr-2 h-4 w-4" />
            Balances
          </Link>
        </Button>
      </div>

      {/* Active order banner */}
      {activeOrder && (
        <Link to={`/groups/${groupId}/orders/${activeOrder.id}`}>
          <Card className="p-5 mb-8 border-orange-300 bg-linear-to-r from-orange-50 to-amber-50 dark:from-orange-950/30 dark:to-amber-950/20 hover:shadow-md transition-all group">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-orange-100 dark:bg-orange-900/40">
                  <ShoppingCart className="h-5 w-5 text-orange-600 dark:text-orange-400" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-semibold text-orange-700 dark:text-orange-400">
                      Active Order
                    </p>
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-orange-500"></span>
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {activeOrder.restaurant_name ?? "Custom"} &middot;{" "}
                    {activeOrder.participant_count} participants &middot;{" "}
                    {Number(activeOrder.total_amount).toFixed(2)} ₴ total
                  </p>
                </div>
              </div>
              <ArrowRight className="h-5 w-5 text-orange-500 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
            </div>
          </Card>
        </Link>
      )}

      {/* Dashboard cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {analytics && (
          <>
            <Card className="p-5 hover:shadow-md group">
              <div className="flex items-center gap-3 mb-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600 group-hover:scale-105 transition-transform">
                  <ShoppingCart className="h-5 w-5" />
                </div>
                <p className="text-sm font-medium text-muted-foreground">
                  Total Orders
                </p>
              </div>
              <p className="text-2xl font-bold">{analytics.total_orders}</p>
            </Card>

            <Card className="p-5 hover:shadow-md group">
              <div className="flex items-center gap-3 mb-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-green-50 text-green-600 group-hover:scale-105 transition-transform">
                  <DollarSign className="h-5 w-5" />
                </div>
                <p className="text-sm font-medium text-muted-foreground">
                  Total Spent
                </p>
              </div>
              <p className="text-2xl font-bold">
                {Number(analytics.total_spent).toFixed(2)} ₴
              </p>
            </Card>

            <Card className="p-5 hover:shadow-md group">
              <div className="flex items-center gap-3 mb-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-50 text-purple-600 group-hover:scale-105 transition-transform">
                  <Users className="h-5 w-5" />
                </div>
                <p className="text-sm font-medium text-muted-foreground">
                  Members
                </p>
              </div>
              <p className="text-2xl font-bold">{analytics.total_members}</p>
            </Card>

            <Card className="p-5 hover:shadow-md group">
              <div className="flex items-center gap-3 mb-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-600 group-hover:scale-105 transition-transform">
                  <TrendingUp className="h-5 w-5" />
                </div>
                <p className="text-sm font-medium text-muted-foreground">
                  Avg. Order
                </p>
              </div>
              <p className="text-2xl font-bold">
                {Number(analytics.average_order_value).toFixed(2)} ₴
              </p>
            </Card>
          </>
        )}
      </div>

      {/* My balance */}
      {myBalance && (
        <Card className="p-5 mb-8 hover:shadow-md">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div
                className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-xl",
                  Number(myBalance.amount) >= 0
                    ? "bg-emerald-50 text-emerald-600"
                    : "bg-red-50 text-red-600",
                )}
              >
                <Wallet className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  My Balance
                </p>
                <p
                  className={cn(
                    "text-2xl font-bold",
                    Number(myBalance.amount) >= 0
                      ? "text-emerald-600"
                      : "text-red-600",
                  )}
                >
                  {Number(myBalance.amount).toFixed(2)} ₴
                </p>
              </div>
            </div>
            <Link to={`/groups/${groupId}/balances`}>
              <Button variant="outline" size="sm" className="rounded-full">
                View History
              </Button>
            </Link>
          </div>
        </Card>
      )}

      {analytics?.most_popular_restaurant && (
        <Card className="p-5 hover:shadow-md group">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-rose-50 text-rose-600 group-hover:scale-105 transition-transform">
              <UtensilsCrossed className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Most Popular Restaurant
              </p>
              <p className="text-lg font-semibold">
                {analytics.most_popular_restaurant}
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
