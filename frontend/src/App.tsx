import { RouterProvider } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { useGetCurrentUserQuery } from "@/store/api/authApi";
import { router } from "@/routes";

export function App() {
  // Attempt to fetch current user on mount (checks auth cookie)
  const { isLoading } = useGetCurrentUserQuery();

  // Show a full-screen loader while checking auth status
  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <>
      <RouterProvider router={router} />
      <Toaster />
    </>
  );
}
