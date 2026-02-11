import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useAuth } from "@/hooks";
import { useGetUserAnalyticsQuery } from "@/store/api/analyticsApi";
import { useGetGroupsQuery } from "@/store/api/groupApi";
import { cn } from "@/utils";
import {
  ArrowRight,
  DollarSign,
  Settings,
  ShoppingCart,
  TrendingUp,
  Users,
  UtensilsCrossed,
} from "lucide-react";
import { Link } from "react-router-dom";

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

export function UserDashboardPage() {
  const { user } = useAuth();
  const { data: analytics, isLoading } = useGetUserAnalyticsQuery();
  const { data: groups } = useGetGroupsQuery();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="animate-slide-up">
      {/* Welcome header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Welcome back,{" "}
            <span className="bg-linear-to-r from-orange-500 to-amber-500 bg-clip-text text-transparent">
              {user?.full_name?.split(" ")[0]}
            </span>
            !
          </h1>
          <p className="text-muted-foreground mt-1">
            Here&apos;s your activity overview across all groups.
          </p>
        </div>
        <Button variant="outline" asChild className="hidden sm:flex">
          <Link to="/settings">
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </Link>
        </Button>
      </div>

      {/* Analytics cards */}
      {analytics && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 mb-10">
          <Card className="p-5 hover:shadow-md group">
            <div className="flex items-center gap-3 mb-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600 group-hover:scale-105 transition-transform">
                <Users className="h-5 w-5" />
              </div>
              <p className="text-sm font-medium text-muted-foreground">Groups</p>
            </div>
            <p className="text-3xl font-bold">{analytics.total_groups}</p>
          </Card>

          <Card className="p-5 hover:shadow-md group">
            <div className="flex items-center gap-3 mb-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-50 text-purple-600 group-hover:scale-105 transition-transform">
                <ShoppingCart className="h-5 w-5" />
              </div>
              <p className="text-sm font-medium text-muted-foreground">
                Orders Participated
              </p>
            </div>
            <p className="text-3xl font-bold">
              {analytics.total_orders_participated}
            </p>
          </Card>

          <Card className="p-5 hover:shadow-md group">
            <div className="flex items-center gap-3 mb-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-green-50 text-green-600 group-hover:scale-105 transition-transform">
                <DollarSign className="h-5 w-5" />
              </div>
              <p className="text-sm font-medium text-muted-foreground">Total Spent</p>
            </div>
            <p className="text-3xl font-bold">
              ${Number(analytics.total_spent).toFixed(2)}
            </p>
          </Card>

          <Card className="p-5 hover:shadow-md group">
            <div className="flex items-center gap-3 mb-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-600 group-hover:scale-105 transition-transform">
                <TrendingUp className="h-5 w-5" />
              </div>
              <p className="text-sm font-medium text-muted-foreground">Avg. Order Value</p>
            </div>
            <p className="text-3xl font-bold">
              ${Number(analytics.average_order_value).toFixed(2)}
            </p>
          </Card>

          <Card className="p-5 hover:shadow-md group">
            <div className="flex items-center gap-3 mb-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-rose-50 text-rose-600 group-hover:scale-105 transition-transform">
                <UtensilsCrossed className="h-5 w-5" />
              </div>
              <p className="text-sm font-medium text-muted-foreground">
                Favorite Restaurant
              </p>
            </div>
            <p className="text-xl font-bold truncate">
              {analytics.favorite_restaurant ?? "N/A"}
            </p>
          </Card>

          <Card className="p-5 hover:shadow-md group">
            <div className="flex items-center gap-3 mb-3">
              <div
                className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-xl group-hover:scale-105 transition-transform",
                  Number(analytics.total_balance_across_groups) >= 0
                    ? "bg-emerald-50 text-emerald-600"
                    : "bg-red-50 text-red-600",
                )}
              >
                <DollarSign className="h-5 w-5" />
              </div>
              <p className="text-sm font-medium text-muted-foreground">Total Balance</p>
            </div>
            <p
              className={cn(
                "text-3xl font-bold",
                Number(analytics.total_balance_across_groups) >= 0
                  ? "text-emerald-600"
                  : "text-red-600",
              )}
            >
              ${Number(analytics.total_balance_across_groups).toFixed(2)}
            </p>
          </Card>
        </div>
      )}

      {/* Quick group access */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Your Groups</h2>
        <Button variant="ghost" size="sm" asChild className="text-muted-foreground">
          <Link to="/groups">
            View all
            <ArrowRight className="ml-1 h-4 w-4" />
          </Link>
        </Button>
      </div>

      {groups && groups.length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-16 border-dashed">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-muted mb-4">
            <Users className="h-7 w-7 text-muted-foreground" />
          </div>
          <p className="text-muted-foreground font-medium mb-1">
            No groups yet
          </p>
          <p className="text-sm text-muted-foreground">
            <Link to="/groups" className="text-primary hover:underline font-medium">
              Create one
            </Link>{" "}
            to start ordering lunch together
          </p>
        </Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {groups?.map((group) => (
            <Link key={group.id} to={`/groups/${group.id}`}>
              <Card className="p-4 hover:shadow-md hover:border-primary/30 cursor-pointer group">
                <div className="flex items-center gap-3">
                  <div
                    className={cn(
                      "flex h-11 w-11 items-center justify-center rounded-xl bg-linear-to-br text-white font-bold text-sm shrink-0 group-hover:scale-105 transition-transform shadow-sm",
                      getGroupGradient(group.name),
                    )}
                  >
                    {group.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-semibold truncate">{group.name}</h3>
                    {group.description && (
                      <p className="text-sm text-muted-foreground line-clamp-1">
                        {group.description}
                      </p>
                    )}
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground ml-auto shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
