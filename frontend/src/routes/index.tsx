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
