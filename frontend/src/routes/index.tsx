import { ErrorBoundary } from "@/components/common/ErrorBoundary/ErrorBoundary";
import { Layout } from "@/components/common/Layout/Layout";
import { ProtectedRoute } from "@/components/common/ProtectedRoute/ProtectedRoute";
import { ROUTES } from "@/constants";
import { createBrowserRouter } from "react-router-dom";

import { LoginPage } from "@/modules/auth/pages/LoginPage";
import { RegisterPage } from "@/modules/auth/pages/RegisterPage";
import { BalancesPage } from "@/modules/balance/pages/BalancesPage";
import { SettingsPage } from "@/modules/dashboard/pages/SettingsPage";
import { UserDashboardPage } from "@/modules/dashboard/pages/UserDashboardPage";
import { GroupDetailPage } from "@/modules/group/pages/GroupDetailPage";
import { GroupListPage } from "@/modules/group/pages/GroupListPage";
import { GroupMembersPage } from "@/modules/group/pages/GroupMembersPage";
import { OrderDetailPage } from "@/modules/order/pages/OrderDetailPage";
import { OrderListPage } from "@/modules/order/pages/OrderListPage";
import { RestaurantDetailPage } from "@/modules/restaurant/pages/RestaurantDetailPage";
import { RestaurantListPage } from "@/modules/restaurant/pages/RestaurantListPage";
import { ProfilePage } from "@/modules/user/pages/ProfilePage";
import { UserDetailPage } from "@/modules/user/pages/UserDetailPage";
import { UserListPage } from "@/modules/user/pages/UserListPage";

function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-muted mb-6">
        <span className="text-4xl font-bold text-muted-foreground">?</span>
      </div>
      <h1 className="text-5xl font-bold text-primary mb-3">404</h1>
      <p className="text-lg text-muted-foreground mb-6">
        Oops! This page doesn&apos;t exist.
      </p>
      <a
        href="/"
        className="inline-flex items-center justify-center rounded-full bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground shadow-md shadow-primary/20 hover:bg-primary/90 transition-colors"
      >
        Go Home
      </a>
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
      // Dashboard
      {
        path: ROUTES.HOME,
        element: (
          <ProtectedRoute>
            <UserDashboardPage />
          </ProtectedRoute>
        ),
      },
      {
        path: ROUTES.SETTINGS,
        element: (
          <ProtectedRoute>
            <SettingsPage />
          </ProtectedRoute>
        ),
      },

      // Auth
      {
        path: ROUTES.LOGIN,
        element: <LoginPage />,
      },
      {
        path: ROUTES.REGISTER,
        element: <RegisterPage />,
      },

      // Users (admin)
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

      // Groups
      {
        path: ROUTES.GROUPS,
        element: (
          <ProtectedRoute>
            <GroupListPage />
          </ProtectedRoute>
        ),
      },
      {
        path: ROUTES.GROUP_DETAIL,
        element: (
          <ProtectedRoute>
            <GroupDetailPage />
          </ProtectedRoute>
        ),
      },
      {
        path: ROUTES.GROUP_MEMBERS,
        element: (
          <ProtectedRoute>
            <GroupMembersPage />
          </ProtectedRoute>
        ),
      },

      // Restaurants
      {
        path: ROUTES.GROUP_RESTAURANTS,
        element: (
          <ProtectedRoute>
            <RestaurantListPage />
          </ProtectedRoute>
        ),
      },
      {
        path: ROUTES.GROUP_RESTAURANT_DETAIL,
        element: (
          <ProtectedRoute>
            <RestaurantDetailPage />
          </ProtectedRoute>
        ),
      },

      // Orders
      {
        path: ROUTES.GROUP_ORDERS,
        element: (
          <ProtectedRoute>
            <OrderListPage />
          </ProtectedRoute>
        ),
      },
      {
        path: ROUTES.GROUP_ORDER_DETAIL,
        element: (
          <ProtectedRoute>
            <OrderDetailPage />
          </ProtectedRoute>
        ),
      },

      // Balances
      {
        path: ROUTES.GROUP_BALANCES,
        element: (
          <ProtectedRoute>
            <BalancesPage />
          </ProtectedRoute>
        ),
      },

      // 404
      {
        path: ROUTES.NOT_FOUND,
        element: <NotFoundPage />,
      },
    ],
  },
]);
