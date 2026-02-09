import { createBrowserRouter } from "react-router-dom";
import { Layout } from "@/components/common/Layout/Layout";
import { ProtectedRoute } from "@/components/common/ProtectedRoute/ProtectedRoute";
import { ErrorBoundary } from "@/components/common/ErrorBoundary/ErrorBoundary";
import { ROUTES } from "@/constants";

import { LoginPage } from "@/modules/auth/pages/LoginPage";
import { RegisterPage } from "@/modules/auth/pages/RegisterPage";
import { UserListPage } from "@/modules/user/pages/UserListPage";
import { UserDetailPage } from "@/modules/user/pages/UserDetailPage";
import { ProfilePage } from "@/modules/user/pages/ProfilePage";

function HomePage() {
  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tight">
        Welcome to LunchTogether
      </h1>
      <p className="mt-2 text-muted-foreground">
        Organize regular lunches with your colleagues, friends, and family.
      </p>
    </div>
  );
}

function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <h1 className="text-6xl font-bold text-muted-foreground">404</h1>
      <p className="mt-4 text-lg text-muted-foreground">Page not found</p>
    </div>
  );
}

export const router = createBrowserRouter([
  {
    element: (
      <ErrorBoundary>
        <Layout />
      </ErrorBoundary>
    ),
    children: [
      {
        path: ROUTES.HOME,
        element: (
          <ProtectedRoute>
            <HomePage />
          </ProtectedRoute>
        ),
      },
      {
        path: ROUTES.LOGIN,
        element: <LoginPage />,
      },
      {
        path: ROUTES.REGISTER,
        element: <RegisterPage />,
      },
      {
        path: ROUTES.USERS,
        element: (
          <ProtectedRoute>
            <UserListPage />
          </ProtectedRoute>
        ),
      },
      {
        path: ROUTES.USER_DETAIL,
        element: (
          <ProtectedRoute>
            <UserDetailPage />
          </ProtectedRoute>
        ),
      },
      {
        path: ROUTES.PROFILE,
        element: (
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        ),
      },
      {
        path: ROUTES.NOT_FOUND,
        element: <NotFoundPage />,
      },
    ],
  },
]);
