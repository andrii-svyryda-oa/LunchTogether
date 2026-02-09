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
    │   ├── api/
    │   │   ├── baseApi.ts          # RTK Query base API
    │   │   ├── authApi.ts          # Auth API endpoints
    │   │   └── userApi.ts          # User API endpoints
    │   └── slices/
    │       ├── authSlice.ts        # Auth state slice
    │       └── userSlice.ts        # User state slice
    ├── types/
    │   ├── index.ts                # Re-export all types
    │   ├── models.ts               # Shared type definitions
    │   ├── api.ts                  # API request/response types
    │   └── common.ts               # Common utility types
    ├── constants/
    │   ├── index.ts                # Re-export all constants
    │   ├── routes.ts               # Route constants
    │   ├── api.ts                  # API endpoints constants
    │   ├── validation.ts           # Validation messages and rules
    │   └── app.ts                  # App-wide constants
    ├── hooks/
    │   ├── index.ts                # Re-export all hooks
    │   ├── useAuth.ts              # Auth-related hooks
    │   ├── useAppSelector.ts       # Typed Redux selector hook
    │   ├── useAppDispatch.ts       # Typed Redux dispatch hook
    │   └── useDebounce.ts          # Common utility hooks
    ├── utils/
    │   ├── index.ts
    │   ├── helpers.ts              # Utility functions
    │   └── validation.ts           # Validation helpers
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
    │   │   ├── hooks/              # Module-specific hooks only
    │   │   │   └── useLoginForm.ts # Form-specific hook
    │   │   └── types/              # Module-specific types only
    │   │       └── forms.ts        # Form-specific types
    │   └── user/
    │       ├── components/
    │       │   └── UserProfile.tsx
    │       ├── pages/
    │       │   ├── UserListPage.tsx
    │       │   └── UserDetailPage.tsx
    │       ├── hooks/              # Module-specific hooks only
    │       │   └── useUserProfile.ts
    │       └── types/              # Module-specific types only
    │           └── profile.ts
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
  VITE_API_BASE_URL=http://localhost:8000/api
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
  - Import and add all slices
  - Export store, RootState, AppDispatch types

- `src/store/api/baseApi.ts`:
  - Create base API with createApi
  - Configure baseQuery with credentials (cookies)
  - Set up base URL from environment
  - Add global error handling
  - Configure tag types for cache invalidation

- `src/hooks/useAppDispatch.ts`:
  - Export typed useAppDispatch hook

- `src/hooks/useAppSelector.ts`:
  - Export typed useAppSelector hook

### 5. Type Definitions
**Task**: Create shared TypeScript types

**Files to create**:
- `src/types/models.ts`:
  - User model type
  - Other domain model types

- `src/types/api.ts`:
  - API response wrapper types
  - Pagination types
  - Error response types
  - Request/response interfaces

- `src/types/common.ts`:
  - Common utility types (Optional, Nullable, etc.)
  - Form types
  - Component prop types

- `src/types/index.ts`:
  - Re-export all types
  - Global type declarations

### 6. Constants Setup
**Task**: Define application constants

**Files to create**:
- `src/constants/routes.ts`:
  - Route path constants (HOME, LOGIN, REGISTER, PROFILE, etc.)

- `src/constants/api.ts`:
  - API endpoint paths
  - HTTP status codes
  - Common headers

- `src/constants/validation.ts`:
  - Validation error messages
  - Password requirements
  - Field length limits
  - Regex patterns

- `src/constants/app.ts`:
  - App name
  - Default values
  - Feature flags

- `src/constants/index.ts`:
  - Re-export all constants

### 7. Utility Functions
**Task**: Create common utility functions

**Files to create**:
- `src/utils/helpers.ts`:
  - cn() function (clsx + tailwind-merge)
  - Date formatting helpers
  - String manipulation utilities
  - Array/object helpers

- `src/utils/validation.ts`:
  - Email validation
  - Password strength validation
  - Generic validation helpers

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

### 11. Auth API & Slice - Global Level
**Task**: Set up auth API and state management

**Files to create**:
- `src/store/api/authApi.ts`:
  - Inject endpoints into baseApi using `injectEndpoints`
  - POST `/auth/register` mutation
  - POST `/auth/login` mutation
  - POST `/auth/logout` mutation
  - GET `/auth/me` query
  - Configure tag invalidation
  - Export hooks (useLoginMutation, useRegisterMutation, etc.)

**Type definitions** (add to existing global types):
- `src/types/models.ts` - Add User interface:
  ```typescript
  export interface User {
    id: string;
    email: string;
    full_name: string;
    is_active: boolean;
    created_at: string;
  }
  ```

- `src/types/api.ts` - Add auth request/response types:
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
  
  export interface AuthResponse {
    user: User;
    message?: string;
  }
  ```

### 12. Auth Slice - Global Level
**Task**: Create Redux slice for auth state

**Files to create**:
- `src/store/slices/authSlice.ts`:
  - State: user (User | null), isAuthenticated (boolean), isLoading (boolean)
  - Reducers: setUser, clearUser, setLoading
  - Add matchers for authApi endpoints (login, logout, getCurrentUser)
  - Export actions
  - Export selectors (selectUser, selectIsAuthenticated, selectIsLoading)

### 13. Auth Hooks - Global Level
**Task**: Create auth-related hooks

**Files to create**:
- `src/hooks/useAuth.ts`:
  - Combine auth selectors and mutations
  - Export convenient auth operations
  ```typescript
  export const useAuth = () => {
    const user = useAppSelector(selectUser);
    const isAuthenticated = useAppSelector(selectIsAuthenticated);
    const [login, { isLoading: isLoggingIn }] = useLoginMutation();
    const [logout] = useLogoutMutation();
    
    return {
      user,
      isAuthenticated,
      login,
      logout,
      isLoggingIn,
    };
  };
  ```

### 14. Auth Module - Module-Specific Hooks
**Task**: Create form-specific hooks

**Files to create**:
- `src/modules/auth/hooks/useLoginForm.ts`:
  - Form validation using react-hook-form + zod
  - Login-specific submit handler
  - Error handling
  - Success redirect logic

- `src/modules/auth/hooks/useRegisterForm.ts` (optional, if logic differs):
  - Register-specific form logic
  - Different validation rules if needed

### 15. Auth Module - Components
**Task**: Create auth UI components

**Files to create**:
- `src/modules/auth/components/LoginForm.tsx`:
  - Use useLoginForm hook
  - Email and password inputs (shadcn/ui)
  - Form validation display
  - Submit with loading state
  - Error display
  - Link to register page

- `src/modules/auth/components/RegisterForm.tsx`:
  - Use useRegisterForm hook (or useLoginForm if shared)
  - Email, password, full name inputs
  - Form validation display
  - Submit with loading state
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

### 17. User API & Slice - Global Level
**Task**: Set up user API and state management

**Files to create**:
- `src/store/api/userApi.ts`:
  - Inject endpoints into baseApi using `injectEndpoints`
  - GET `/users` query with pagination params
  - GET `/users/{id}` query
  - PATCH `/users/{id}` mutation
  - Configure cache tags
  - Export hooks (useGetUsersQuery, useGetUserQuery, etc.)

**Type definitions** (add to existing global types):
- `src/types/api.ts` - Add user-related types:
  ```typescript
  export interface UserListParams {
    page?: number;
    limit?: number;
    search?: string;
  }
  
  export interface UserListResponse {
    users: User[];
    total: number;
    page: number;
    limit: number;
  }
  
  export interface UserUpdateRequest {
    full_name?: string;
    email?: string;
  }
  ```

- `src/store/slices/userSlice.ts` (optional, only if you need client-side user state):
  - State for selected user, filters, etc.
  - Reducers for UI state management
  - Export selectors

### 18. User Module - Components & Pages
**Task**: Create user UI components

**Files to create**:
- `src/modules/user/hooks/useUserProfile.ts` (optional, module-specific):
  - Profile editing logic
  - Form state management
  - Update mutation handling

- `src/modules/user/components/UserProfile.tsx`:
  - Display user information
  - Edit mode toggle
  - Save changes
  - Use shadcn/ui Card component

- `src/modules/user/pages/UserListPage.tsx`:
  - Use useGetUsersQuery hook
  - Display users in a list/table
  - Pagination controls
  - Search functionality
  - Loading and error states

- `src/modules/user/pages/UserDetailPage.tsx`:
  - Use useGetUserQuery hook with userId from route params
  - Render UserProfile component
  - Loading and error states
  - Back to list navigation

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
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=LunchTogether
```

## Validation Checklist

- [ ] APIs are in `src/store/api/` (global level)
- [ ] Slices are in `src/store/slices/` (global level)
- [ ] Constants are in `src/constants/` (global level)
- [ ] General hooks are in `src/hooks/` (global level)
- [ ] Global types are in `src/types/` (global level)
- [ ] Modules only contain: components, pages, and module-specific hooks/types
- [ ] RTK Query uses `injectEndpoints` pattern
- [ ] All API calls include credentials (cookies)
- [ ] Redux state is properly typed with RootState and AppDispatch
- [ ] useAppSelector and useAppDispatch hooks are typed
- [ ] Protected routes redirect unauthenticated users
- [ ] Forms have proper validation (zod schemas)
- [ ] Loading and error states are handled
- [ ] shadcn/ui components are properly integrated
- [ ] Tailwind CSS is working correctly
- [ ] TypeScript has no errors
- [ ] Path aliases are working (@/ for src/)

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
- **Global Level**: APIs, slices, constants, general types, and reusable hooks live at the top level
- **Module Level**: Only contains UI (components, pages) and module-specific hooks/types
- Modules are organized by feature/domain (auth, user, etc.)
- Shared UI components go in `components/common/`
- shadcn/ui components go in `components/ui/`
- Each module imports from global folders: `import { useAuth } from '@/hooks'`

### State Management Strategy
- Use RTK Query for server state (data fetching, caching) - **APIs at global level**
- Use Redux slices for client state (auth status, UI state) - **Slices at global level**
- Minimize global state, prefer component state when possible
- Use RTK Query's automatic cache invalidation with tags
- All APIs extend baseApi using `injectEndpoints`

### Module Guidelines
**What goes in a module**:
- Components (UI specific to that feature)
- Pages (route components)
- Module-specific hooks (e.g., `useLoginForm` for form logic)
- Module-specific types (e.g., form types that aren't used elsewhere)

**What does NOT go in a module**:
- APIs (go in `src/store/api/`)
- Slices (go in `src/store/slices/`)
- Constants (go in `src/constants/`)
- General types (go in `src/types/`)
- Reusable hooks (go in `src/hooks/`)

### Import Pattern Examples
```typescript
// In a module component
import { useAuth } from '@/hooks';                    // From global hooks
import { useLoginMutation } from '@/store/api';       // From global API
import { selectUser } from '@/store/slices/authSlice'; // From global slice
import { ROUTES } from '@/constants';                 // From global constants
import { User } from '@/types';                       // From global types
import { useLoginForm } from '../hooks/useLoginForm'; // Module-specific hook
```

### Styling Approach
- Use shadcn/ui components as building blocks
- Customize with Tailwind utility classes
- Use CSS variables for theme consistency
- Mobile-first responsive design
