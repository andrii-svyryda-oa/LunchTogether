import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { APP } from "@/constants";
import { useAppDispatch, useAppSelector, useDebounce } from "@/hooks";
import { useGetUsersQuery } from "@/store/api/userApi";
import {
  selectCurrentPage,
  selectSearchQuery,
  setCurrentPage,
  setSearchQuery,
} from "@/store/slices/userSlice";
import { cn } from "@/utils";
import { formatDate } from "@/utils";
import {
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Search,
  User,
} from "lucide-react";
import { Link } from "react-router-dom";

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

export function UserListPage() {
  const dispatch = useAppDispatch();
  const searchQuery = useAppSelector(selectSearchQuery);
  const currentPage = useAppSelector(selectCurrentPage);
  const debouncedSearch = useDebounce(searchQuery);

  const { data, isLoading, error } = useGetUsersQuery({
    page: currentPage,
    page_size: APP.DEFAULT_PAGE_SIZE,
    search: debouncedSearch || undefined,
  });

  const totalPages = data?.total_pages ?? 0;

  return (
    <div className="space-y-6 animate-slide-up">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Users</h1>
        <p className="text-muted-foreground mt-1">
          Browse and manage registered users.
        </p>
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search users..."
          value={searchQuery}
          onChange={(e) => dispatch(setSearchQuery(e.target.value))}
          className="pl-10"
        />
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Failed to load users. Please try again.
          </AlertDescription>
        </Alert>
      )}

      {isLoading && (
        <div className="flex justify-center py-20">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      )}

      {data && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data.items.map((user) => (
              <Link key={user.id} to={`/users/${user.id}`}>
                <Card className="hover:shadow-md hover:border-primary/30 cursor-pointer group">
                  <CardHeader className="flex flex-row items-center gap-3 pb-2">
                    <div
                      className={cn(
                        "flex h-11 w-11 items-center justify-center rounded-full bg-linear-to-br text-white font-bold text-sm shrink-0 group-hover:scale-105 transition-transform",
                        getAvatarGradient(user.full_name),
                      )}
                    >
                      {user.full_name.charAt(0).toUpperCase()}
                    </div>
                    <div className="min-w-0">
                      <CardTitle className="text-base truncate">
                        {user.full_name}
                      </CardTitle>
                      <CardDescription className="text-xs truncate">
                        {user.email}
                      </CardDescription>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-xs text-muted-foreground">
                      Joined {formatDate(user.created_at)}
                    </p>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>

          {data.items.length === 0 && (
            <Card className="flex flex-col items-center justify-center py-16 border-dashed">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-muted mb-4">
                <User className="h-7 w-7 text-muted-foreground" />
              </div>
              <p className="text-muted-foreground font-medium">
                No users found.
              </p>
            </Card>
          )}

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => dispatch(setCurrentPage(currentPage - 1))}
                disabled={currentPage <= 1}
                className="rounded-full"
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>
              <span className="text-sm text-muted-foreground px-3">
                Page {currentPage} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => dispatch(setCurrentPage(currentPage + 1))}
                disabled={currentPage >= totalPages}
                className="rounded-full"
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
