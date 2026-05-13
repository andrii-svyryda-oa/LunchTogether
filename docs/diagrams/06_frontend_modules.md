# Рис. 4.1.1. Структура модулів клієнтської частини

Діаграма ілюструє модульну організацію директорії `frontend/src/`. Глобальні
ресурси (store, types, constants, hooks, utils, спільні компоненти) лежать на
верхньому рівні; функціональні розділи додатку винесено у `modules/` із
власними піддиректоріями `pages/`, `components/`, `hooks/`, `types/`. Імпорти
між модулями відбуваються лише через глобальний рівень (через alias `@/`).

**Використовується у розділах:** 4.1.

```mermaid
flowchart TD
    Entry[main.tsx + App.tsx<br/>RouterProvider + Toaster]
    Routes[routes/index.tsx<br/>createBrowserRouter, ProtectedRoute]
    LayoutCmp[components/common/Layout<br/>Header + Sidebar + Footer]

    subgraph Global [Глобальні ресурси src/]
        StoreApi[store/api/<br/>baseApi + injectEndpoints<br/>authApi, userApi, groupApi,<br/>restaurantApi, orderApi,<br/>balanceApi, analyticsApi]
        StoreSlice[store/slices/<br/>authSlice, userSlice]
        StoreRoot[store/index.ts<br/>configureStore]
        Types[types/<br/>models, api, common]
        Constants[constants/<br/>routes, api, app, validation]
        Hooks[hooks/<br/>useAuth, useAppSelector,<br/>useAppDispatch, useDebounce]
        Utils[utils/<br/>cn, validation, helpers]
        UI[components/ui/<br/>shadcn primitives<br/>Button, Card, Dialog, Form,<br/>Input, Label, Popover, Alert,<br/>Combobox, Sonner]
        Common[components/common/<br/>Layout, ProtectedRoute,<br/>ErrorBoundary]
        Config[config/env.ts]
    end

    subgraph Modules [modules/]
        AuthM[auth/<br/>LoginPage, RegisterPage,<br/>LoginForm, RegisterForm,<br/>useLoginForm, useRegisterForm]
        DashM[dashboard/<br/>UserDashboardPage,<br/>SettingsPage]
        GroupM[group/<br/>GroupListPage,<br/>GroupDetailPage,<br/>GroupMembersPage]
        UserM[user/<br/>ProfilePage, UserListPage,<br/>UserDetailPage, UserProfile]
        RestM[restaurant/<br/>RestaurantListPage,<br/>RestaurantDetailPage]
        OrderM[order/<br/>OrderListPage,<br/>OrderDetailPage]
        BalanceM[balance/<br/>BalancesPage]
    end

    Entry --> Routes
    Entry --> StoreRoot
    Routes --> LayoutCmp
    Routes --> Modules
    LayoutCmp --> Common
    Modules --> StoreApi
    Modules --> StoreSlice
    Modules --> UI
    Modules --> Hooks
    Modules --> Constants
    Modules --> Utils
    Modules --> Types
    StoreApi --> Constants
    StoreApi --> Types
    StoreApi --> Config
```
