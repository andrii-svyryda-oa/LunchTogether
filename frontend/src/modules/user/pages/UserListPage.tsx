import { Link } from "react-router-dom";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Search,
  User,
} from "lucide-react";
import { useGetUsersQuery } from "@/store/api/userApi";
import { useAppDispatch, useAppSelector, useDebounce } from "@/hooks";
import {
  selectSearchQuery,
  selectCurrentPage,
  setSearchQuery,
  setCurrentPage,
} from "@/store/slices/userSlice";
import { APP } from "@/constants";
import { formatDate } from "@/utils";

export function UserListPage() {
  const dispatch = useAppDispatch();
  const searchQuery = useAppSelector(selectSearchQuery);
  const currentPage = useAppSelector(selectCurrentPage);
  const debouncedSearch = useDebounce(searchQuery);

  const { data, isLoading, error } = useGetUsersQuery({
    page: currentPage,
    limit: APP.DEFAULT_PAGE_SIZE,
    search: debouncedSearch || undefined,
  });

  const totalPages = data ? Math.ceil(data.total / APP.DEFAULT_PAGE_SIZE) : 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Users</h1>
        <p className="text-muted-foreground">
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
        <div className="flex justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      )}

      {data && (
        <>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {data.users.map((user) => (
              <Link key={user.id} to={`/users/${user.id}`}>
                <Card className="transition-shadow hover:shadow-md">
                  <CardHeader className="flex flex-row items-center gap-3 pb-2">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                      <User className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <CardTitle className="text-base">
                        {user.full_name}
                      </CardTitle>
                      <CardDescription className="text-xs">
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

          {data.users.length === 0 && (
            <div className="py-12 text-center text-muted-foreground">
              No users found.
            </div>
          )}

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => dispatch(setCurrentPage(currentPage - 1))}
                disabled={currentPage <= 1}
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>
              <span className="text-sm text-muted-foreground">
                Page {currentPage} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => dispatch(setCurrentPage(currentPage + 1))}
                disabled={currentPage >= totalPages}
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
