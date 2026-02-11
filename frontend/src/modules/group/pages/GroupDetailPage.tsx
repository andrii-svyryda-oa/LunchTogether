import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useAuth } from "@/hooks";
import { useGetGroupAnalyticsQuery } from "@/store/api/analyticsApi";
import { useGetMyBalanceQuery } from "@/store/api/balanceApi";
import { useGetGroupQuery } from "@/store/api/groupApi";
import { useGetActiveOrderQuery } from "@/store/api/orderApi";
import { cn } from "@/utils";
import { ShoppingCart, Users, UtensilsCrossed, Wallet } from "lucide-react";
import { Link, useParams } from "react-router-dom";

export function GroupDetailPage() {
  const { groupId } = useParams<{ groupId: string }>();
  const { user } = useAuth();
  const { data: group, isLoading, error } = useGetGroupQuery(groupId!);
  const { data: activeOrder } = useGetActiveOrderQuery(groupId!);
  const { data: analytics } = useGetGroupAnalyticsQuery(groupId!);
  const { data: myBalance } = useGetMyBalanceQuery(groupId!);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error || !group) {
    return <Alert variant="destructive">Failed to load group.</Alert>;
  }

  const isOwner = group.owner_id === user?.id;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary font-bold text-xl">
            {group.name.charAt(0).toUpperCase()}
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{group.name}</h1>
            {group.description && (
              <p className="text-muted-foreground">{group.description}</p>
            )}
          </div>
        </div>
      </div>

      {/* Quick nav links */}
      <div className="flex flex-wrap gap-2 mb-6">
        <Button variant="outline" size="sm" asChild>
          <Link to={`/groups/${groupId}/members`}>
            <Users className="mr-2 h-4 w-4" />
            Members ({group.members?.length ?? 0})
          </Link>
        </Button>
        <Button variant="outline" size="sm" asChild>
          <Link to={`/groups/${groupId}/restaurants`}>
            <UtensilsCrossed className="mr-2 h-4 w-4" />
            Restaurants
          </Link>
        </Button>
        <Button variant="outline" size="sm" asChild>
          <Link to={`/groups/${groupId}/orders`}>
            <ShoppingCart className="mr-2 h-4 w-4" />
            Orders
          </Link>
        </Button>
        <Button variant="outline" size="sm" asChild>
          <Link to={`/groups/${groupId}/balances`}>
            <Wallet className="mr-2 h-4 w-4" />
            Balances
          </Link>
        </Button>
      </div>

      {/* Active order banner */}
      {activeOrder && (
        <Link to={`/groups/${groupId}/orders/${activeOrder.id}`}>
          <Card className="p-4 mb-6 border-orange-500/50 bg-orange-50 dark:bg-orange-950/20 hover:border-orange-500 transition-colors">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold text-orange-700 dark:text-orange-400">
                  Active Order — {activeOrder.restaurant_name ?? "Custom"}
                </p>
                <p className="text-sm text-muted-foreground">
                  Status: {activeOrder.status} · {activeOrder.participant_count}{" "}
                  participants · ${Number(activeOrder.total_amount).toFixed(2)}{" "}
                  total
                </p>
              </div>
              <Button variant="outline" size="sm">
                View Order
              </Button>
            </div>
          </Card>
        </Link>
      )}

      {/* Dashboard cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
        {analytics && (
          <>
            <Card className="p-4">
              <p className="text-sm text-muted-foreground">Total Orders</p>
              <p className="text-2xl font-bold">{analytics.total_orders}</p>
            </Card>
            <Card className="p-4">
              <p className="text-sm text-muted-foreground">Total Spent</p>
              <p className="text-2xl font-bold">
                ${Number(analytics.total_spent).toFixed(2)}
              </p>
            </Card>
            <Card className="p-4">
              <p className="text-sm text-muted-foreground">Members</p>
              <p className="text-2xl font-bold">{analytics.total_members}</p>
            </Card>
            <Card className="p-4">
              <p className="text-sm text-muted-foreground">Avg. Order</p>
              <p className="text-2xl font-bold">
                ${Number(analytics.average_order_value).toFixed(2)}
              </p>
            </Card>
          </>
        )}
      </div>

      {/* My balance */}
      {myBalance && (
        <Card className="p-4 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">My Balance</p>
              <p
                className={cn(
                  "text-2xl font-bold",
                  Number(myBalance.amount) >= 0
                    ? "text-green-600"
                    : "text-red-600",
                )}
              >
                ${Number(myBalance.amount).toFixed(2)}
              </p>
            </div>
            <Link to={`/groups/${groupId}/balances`}>
              <Button variant="outline" size="sm">
                View History
              </Button>
            </Link>
          </div>
        </Card>
      )}

      {analytics?.most_popular_restaurant && (
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">
            Most Popular Restaurant
          </p>
          <p className="text-lg font-semibold">
            {analytics.most_popular_restaurant}
          </p>
        </Card>
      )}
    </div>
  );
}
