# Frontend Basic Structure Implementation Plan

## Overview
This plan outlines the implementation of the basic frontend structure using React with TypeScript, following a modular architecture pattern.

## Technology Stack
- TypeScript
- React 18+
- Redux Toolkit (state management and RTK Query)
- shadcn/ui for UI components
- Tailwind CSS for styling
- React Router for routing
- Vite as build tool

## Project Structure

```
frontend/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── index.html
├── .env.example
├── public/
│   └── assets/
└── src/
    ├── main.tsx                    # Application entry point
    ├── App.tsx                     # Root component
    ├── vite-env.d.ts
    ├── config/
    │   └── env.ts                  # Environment configuration
    ├── store/
    │   ├── index.ts                # Redux store configuration
    │   └── api/
    │       └── baseApi.ts          # RTK Query base API
    ├── types/
    │   ├── index.ts
    │   └── models.ts               # Shared type definitions
    ├── constants/
    │   ├── index.ts
    │   ├── routes.ts               # Route constants
    │   └── api.ts                  # API endpoints constants
    ├── hooks/
    │   ├── index.ts
    │   └── useAuth.ts              # Common hooks
    ├── utils/
    │   ├── index.ts
    │   └── helpers.ts              # Utility functions
    ├── components/
    │   ├── ui/                     # shadcn/ui components
    │   │   ├── button.tsx
    │   │   ├── input.tsx
    │   │   ├── card.tsx
    │   │   └── ...
    │   └── common/                 # Shared components
    │       ├── Layout/
    │       │   ├── Layout.tsx
    │       │   ├── Header.tsx
    │       │   ├── Sidebar.tsx
    │       │   └── Footer.tsx
    │       ├── ProtectedRoute/
    │       │   └── ProtectedRoute.tsx
    │       └── ErrorBoundary/
    │           └── ErrorBoundary.tsx
    ├── modules/
    │   ├── auth/
    │   │   ├── components/
    │   │   │   ├── LoginForm.tsx
    │   │   │   └── RegisterForm.tsx
    │   │   ├── pages/
    │   │   │   ├── LoginPage.tsx
    │   │   │   └── RegisterPage.tsx
    │   │   ├── api/
    │   │   │   └── authApi.ts      # RTK Query endpoints
    │   │   ├── slices/
    │   │   │   └── authSlice.ts    # Redux slice
    │   │   ├── hooks/
    │   │   │   └── useAuthForm.ts
    │   │   ├── types/
    │   │   │   └── auth.types.ts
    │   │   └── constants/
    │   │       └── auth.constants.ts
    │   └── user/
    │       ├── components/
    │       │   └── UserProfile.tsx
    │       ├── pages/
    │       │   ├── UserListPage.tsx
    │       │   └── UserDetailPage.tsx
    │       ├── api/
    │       │   └── userApi.ts
    │       ├── slices/
    │       │   └── userSlice.ts
    │       ├── hooks/
    │       │   └── useUserData.ts
    │       ├── types/
    │       │   └── user.types.ts
    │       └── constants/
    │           └── user.constants.ts
    └── routes/
        └── index.tsx               # Route configuration
```

## Implementation Steps

### 1. Project Initialization
**Task**: Set up React project with Vite and TypeScript

**Commands to run**:
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

**Additional dependencies to install**:
```bash
# Core dependencies
npm install react-router-dom @reduxjs/toolkit react-redux

# UI and styling
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# shadcn/ui setup
npx shadcn-ui@latest init

# Utilities
npm install clsx tailwind-merge
npm install @hookform/resolvers zod react-hook-form
```

### 2. Tailwind CSS Configuration
**Task**: Configure Tailwind CSS with shadcn/ui

**Files to configure**:
- `tailwind.config.js`:
  - Add content paths
  - Configure theme extensions
  - Add shadcn/ui presets

- `src/index.css`:
  - Add Tailwind directives
  - Add CSS variables for shadcn/ui theme

### 3. Environment Configuration
**Task**: Set up environment variable management

**Files to create**:
- `.env.example`:
  ```env
  VITE_API_BASE_URL=http://localhost:8000/api/v1
  VITE_APP_NAME=LunchTogether
  ```

- `src/config/env.ts`:
  - Parse and export environment variables
  - Type-safe environment configuration

### 4. Redux Store Setup
**Task**: Configure Redux Toolkit store with RTK Query

**Files to create**:
- `src/store/index.ts`:
  - Create store with configureStore
  - Add middleware for RTK Query
  - Export hooks (useAppDispatch, useAppSelector)

- `src/store/api/baseApi.ts`:
  - Create base API with createApi
  - Configure baseQuery with credentials (cookies)
  - Set up base URL from environment
  - Add global error handling
  - Configure tag types for cache invalidation

### 5. Type Definitions
**Task**: Create shared TypeScript types

**Files to create**:
- `src/types/models.ts`:
  - User type
  - API response types
  - Pagination types
  - Error types

- `src/types/index.ts`:
  - Re-export all types
  - Global type declarations

### 6. Constants Setup
**Task**: Define application constants

**Files to create**:
- `src/constants/routes.ts`:
  - Route path constants (HOME, LOGIN, REGISTER, PROFILE, etc.)

- `src/constants/api.ts`:
  - API endpoint constants
  - HTTP status codes
  - Common headers

- `src/constants/index.ts`:
  - Re-export all constants

### 7. Utility Functions
**Task**: Create common utility functions

**Files to create**:
- `src/utils/helpers.ts`:
  - cn() function (clsx + tailwind-merge)
  - Date formatting helpers
  - String manipulation utilities

- `src/utils/index.ts`:
  - Re-export utilities

### 8. shadcn/ui Components
**Task**: Install and configure base UI components

**Components to add** (using shadcn/ui CLI):
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add card
npx shadcn-ui@latest add form
npx shadcn-ui@latest add label
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add alert
npx shadcn-ui@latest add dialog
```

**Result**: Components will be added to `src/components/ui/`

### 9. Common Components - Layout
**Task**: Create layout components

**Files to create**:
- `src/components/common/Layout/Layout.tsx`:
  - Main layout wrapper
  - Conditional header/sidebar rendering
  - Children rendering

- `src/components/common/Layout/Header.tsx`:
  - App header with navigation
  - User menu (logout, profile)
  - Mobile responsive

- `src/components/common/Layout/Sidebar.tsx`:
  - Navigation sidebar
  - Collapsible on mobile

- `src/components/common/Layout/Footer.tsx`:
  - App footer (optional)

### 10. Common Components - Protection
**Task**: Create route protection components

**Files to create**:
- `src/components/common/ProtectedRoute/ProtectedRoute.tsx`:
  - Check authentication status
  - Redirect to login if not authenticated
  - Use auth slice for state

- `src/components/common/ErrorBoundary/ErrorBoundary.tsx`:
  - Catch React errors
  - Display fallback UI
  - Log errors to console/Sentry

### 11. Auth Module - Types & Constants
**Task**: Set up auth module structure

**Files to create**:
- `src/modules/auth/types/auth.types.ts`:
  ```typescript
  export interface LoginRequest {
    email: string;
    password: string;
  }
  
  export interface RegisterRequest {
    email: string;
    password: string;
    full_name: string;
  }
  
  export interface AuthUser {
    id: string;
    email: string;
    full_name: string;
  }
  ```

- `src/modules/auth/constants/auth.constants.ts`:
  - Form validation messages
  - Password requirements
  - Auth error messages

### 12. Auth Module - API
**Task**: Create RTK Query endpoints for auth

**Files to create**:
- `src/modules/auth/api/authApi.ts`:
  - Inject endpoints into baseApi using `injectEndpoints`
  - POST `/auth/register` mutation
  - POST `/auth/login` mutation
  - POST `/auth/logout` mutation
  - GET `/auth/me` query
  - Configure tag invalidation

### 13. Auth Module - Slice
**Task**: Create Redux slice for auth state

**Files to create**:
- `src/modules/auth/slices/authSlice.ts`:
  - State: user, isAuthenticated, isLoading
  - Reducers: setUser, clearUser
  - Add matchers for authApi endpoints (login, logout)
  - Export selectors (selectUser, selectIsAuthenticated)

### 14. Auth Module - Hooks
**Task**: Create custom hooks for auth

**Files to create**:
- `src/modules/auth/hooks/useAuthForm.ts`:
  - Form validation using react-hook-form + zod
  - Submit handlers
  - Error handling

- `src/hooks/useAuth.ts` (global):
  - Export auth selectors and mutations
  - Convenience hook for auth operations

### 15. Auth Module - Components
**Task**: Create auth UI components

**Files to create**:
- `src/modules/auth/components/LoginForm.tsx`:
  - Email and password inputs
  - Form validation
  - Submit handler
  - Error display
  - Link to register page

- `src/modules/auth/components/RegisterForm.tsx`:
  - Email, password, full name inputs
  - Form validation (password strength, email format)
  - Submit handler
  - Error display
  - Link to login page

### 16. Auth Module - Pages
**Task**: Create auth pages

**Files to create**:
- `src/modules/auth/pages/LoginPage.tsx`:
  - Render LoginForm
  - Handle redirect after successful login
  - Centered layout with Card component

- `src/modules/auth/pages/RegisterPage.tsx`:
  - Render RegisterForm
  - Handle redirect after successful registration
  - Centered layout with Card component

### 17. User Module - Types & API
**Task**: Set up user module structure

**Files to create**:
- `src/modules/user/types/user.types.ts`:
  - User type (import from shared types)
  - UserListResponse type
  - UserUpdateRequest type

- `src/modules/user/api/userApi.ts`:
  - GET `/users` query with pagination
  - GET `/users/{id}` query
  - PATCH `/users/{id}` mutation
  - Use `injectEndpoints` pattern

### 18. User Module - Components & Pages
**Task**: Create user UI components

**Files to create**:
- `src/modules/user/components/UserProfile.tsx`:
  - Display user information
  - Edit profile button
  - Use Card component

- `src/modules/user/pages/UserListPage.tsx`:
  - Fetch and display users list
  - Pagination controls
  - Loading and error states

- `src/modules/user/pages/UserDetailPage.tsx`:
  - Fetch and display single user
  - Use UserProfile component
  - Loading and error states

### 19. Routing Configuration
**Task**: Set up React Router

**Files to create**:
- `src/routes/index.tsx`:
  - Create router with createBrowserRouter
  - Define routes with lazy loading
  - Nest protected routes
  - Handle 404 pages

**Routes structure**:
```typescript
- / (home)
- /login
- /register
- /users (protected)
  - /users/:id (protected)
- /profile (protected)
- /* (404)
```

### 20. Root Application
**Task**: Wire up all components

**Files to configure**:
- `src/main.tsx`:
  - Import store
  - Wrap App with Redux Provider
  - Wrap with RouterProvider
  - Import global styles

- `src/App.tsx`:
  - Initialize auth (check /auth/me on mount)
  - Show loading state during initialization
  - Render router outlet
  - Add Toaster for notifications

### 21. TypeScript Configuration
**Task**: Configure TypeScript for optimal DX

**Files to configure**:
- `tsconfig.json`:
  - Enable strict mode
  - Add path aliases (@/ for src/)
  - Configure module resolution

- `vite.config.ts`:
  - Add path alias resolution
  - Configure proxy for API calls (optional)

### 22. Testing Setup (Optional for basic structure)
**Task**: Add testing infrastructure

**Dependencies**:
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

**Files to create**:
- `vitest.config.ts`: Vitest configuration
- `src/test/setup.ts`: Test setup file
- `src/modules/auth/__tests__/LoginForm.test.tsx`: Example test

## Environment Variables Required

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=LunchTogether
```

## Validation Checklist

- [ ] All modules follow the defined structure (components, pages, api, slices, hooks, types, constants)
- [ ] RTK Query uses `injectEndpoints` pattern
- [ ] All API calls include credentials (cookies)
- [ ] Redux state is properly typed
- [ ] Protected routes redirect unauthenticated users
- [ ] Forms have proper validation
- [ ] Loading and error states are handled
- [ ] shadcn/ui components are properly integrated
- [ ] Tailwind CSS is working correctly
- [ ] TypeScript has no errors
- [ ] Path aliases are working

## Next Steps After Implementation

1. Test authentication flow (register, login, logout)
2. Verify protected routes work correctly
3. Test API integration with backend
4. Add more modules as needed (lunches, invites, etc.)
5. Implement responsive design for mobile
6. Add comprehensive component tests
7. Add Storybook for component documentation (optional)

## Additional Considerations

### Code Organization Patterns
- Each module is self-contained with its own types, API, state, and UI
- Shared code goes in top-level folders (components/common, hooks, utils)
- Constants and types are co-located with their modules
- APIs use RTK Query's `injectEndpoints` to extend the base API

### State Management Strategy
- Use RTK Query for server state (data fetching, caching)
- Use Redux slices for client state (auth status, UI state)
- Minimize global state, prefer component state when possible
- Use RTK Query's automatic cache invalidation with tags

### Styling Approach
- Use shadcn/ui components as building blocks
- Customize with Tailwind utility classes
- Use CSS variables for theme consistency
- Mobile-first responsive design
