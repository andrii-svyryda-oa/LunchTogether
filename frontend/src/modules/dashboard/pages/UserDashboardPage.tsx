import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useAuth } from "@/hooks";
import { useGetUserAnalyticsQuery } from "@/store/api/analyticsApi";
import { useGetGroupsQuery } from "@/store/api/groupApi";
import { cn } from "@/utils";
import {
  DollarSign,
  Settings,
  ShoppingCart,
  Users,
  UtensilsCrossed,
} from "lucide-react";
import { Link } from "react-router-dom";

export function UserDashboardPage() {
  const { user } = useAuth();
  const { data: analytics, isLoading } = useGetUserAnalyticsQuery();
  const { data: groups } = useGetGroupsQuery();

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
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Welcome back, {user?.full_name?.split(" ")[0]}!
          </h1>
          <p className="text-muted-foreground">
            Here's your activity overview across all groups.
          </p>
        </div>
        <Button variant="outline" asChild>
          <Link to="/settings">
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </Link>
        </Button>
      </div>

      {/* Analytics cards */}
      {analytics && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 mb-8">
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-2">
              <Users className="h-5 w-5 text-primary" />
              <p className="text-sm text-muted-foreground">Groups</p>
            </div>
            <p className="text-3xl font-bold">{analytics.total_groups}</p>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-3 mb-2">
              <ShoppingCart className="h-5 w-5 text-primary" />
              <p className="text-sm text-muted-foreground">
                Orders Participated
              </p>
            </div>
            <p className="text-3xl font-bold">
              {analytics.total_orders_participated}
            </p>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-3 mb-2">
              <DollarSign className="h-5 w-5 text-primary" />
              <p className="text-sm text-muted-foreground">Total Spent</p>
            </div>
            <p className="text-3xl font-bold">
              ${Number(analytics.total_spent).toFixed(2)}
            </p>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-3 mb-2">
              <DollarSign className="h-5 w-5 text-primary" />
              <p className="text-sm text-muted-foreground">Avg. Order Value</p>
            </div>
            <p className="text-3xl font-bold">
              ${Number(analytics.average_order_value).toFixed(2)}
            </p>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-3 mb-2">
              <UtensilsCrossed className="h-5 w-5 text-primary" />
              <p className="text-sm text-muted-foreground">
                Favorite Restaurant
              </p>
            </div>
            <p className="text-xl font-bold">
              {analytics.favorite_restaurant ?? "N/A"}
            </p>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-3 mb-2">
              <DollarSign className="h-5 w-5 text-primary" />
              <p className="text-sm text-muted-foreground">Total Balance</p>
            </div>
            <p
              className={cn(
                "text-3xl font-bold",
                Number(analytics.total_balance_across_groups) >= 0
                  ? "text-green-600"
                  : "text-red-600",
              )}
            >
              ${Number(analytics.total_balance_across_groups).toFixed(2)}
            </p>
          </Card>
        </div>
      )}

      {/* Quick group access */}
      <h2 className="text-xl font-semibold mb-4">Your Groups</h2>
      {groups && groups.length === 0 ? (
        <p className="text-muted-foreground">
          You don't belong to any groups yet.{" "}
          <Link to="/groups" className="text-primary underline">
            Create one
          </Link>
        </p>
      ) : (
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {groups?.map((group) => (
            <Link key={group.id} to={`/groups/${group.id}`}>
              <Card className="p-4 hover:border-primary transition-colors cursor-pointer">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary font-bold">
                    {group.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h3 className="font-semibold">{group.name}</h3>
                    {group.description && (
                      <p className="text-sm text-muted-foreground line-clamp-1">
                        {group.description}
                      </p>
                    )}
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
