# Admin RBAC Design

## 1. Goal

Upgrade the current admin backend from login-only access control to fixed-role RBAC so the management system can demonstrate real permission isolation during product demos and the next implementation slice.

This slice must:

- enforce role-based access on backend APIs
- hide and block unauthorized frontend routes
- persist the current admin role in frontend state after login or refresh
- keep the design simple enough to land quickly in the current codebase

## 2. Scope

### In Scope

- fixed roles:
  - `super_admin`
  - `content_admin`
  - `ops_admin`
- backend route-level role guards
- frontend menu filtering
- frontend route-guard permission checks
- login flow update to fetch `/api/auth/me`
- refresh-time recovery of current user role
- automated backend and frontend tests for role boundaries

### Out Of Scope

- admin-user CRUD
- role editing UI
- fine-grained permission codes
- button-level permission control
- organization, department, or approval workflows

## 3. Selected Approach

Use fixed-role RBAC with enforcement on both backend and frontend.

The backend remains the source of truth for security. Every protected router uses an explicit dependency that allows only the required roles. The frontend improves usability by filtering sidebar items, guarding routes before navigation, and redirecting the user to a role-appropriate landing page.

This keeps the implementation aligned with the existing modular router structure and avoids introducing unnecessary schema or permission-engine complexity.

## 4. Role Model

### 4.1 Roles

- `super_admin`
- `content_admin`
- `ops_admin`

### 4.2 Permission Boundaries

#### `super_admin`

- can access all admin modules
- keeps system-level configuration access
- keeps high-risk write operations

#### `content_admin`

- can access:
  - knowledge documents
  - FAQ management
  - scenic-area management
  - scenic-spot management
  - route-template management
  - digital-human configuration
  - session correction workflow
- cannot access:
  - dashboard analytics
  - feedback report
  - operation logs
  - system settings

#### `ops_admin`

- can access:
  - workspace/dashboard home
  - analytics dashboard
  - feedback report
  - operation logs
  - session management
- cannot access:
  - knowledge documents
  - FAQ management
  - scenic-area management
  - scenic-spot management
  - route-template management
  - digital-human configuration
  - system settings

## 5. Backend Design

### 5.1 Authentication Base

Keep the current JWT-based login flow and `get_current_user` dependency.

Keep `/api/auth/me` as the shared identity endpoint after login. The response remains small and must include:

- `username`
- `role`

### 5.2 Authorization Dependencies

Add explicit role-check dependencies in `backend/app/api/deps.py`:

- `require_super_admin`
- `require_content_roles`
- `require_ops_roles`

Behavior:

- missing or invalid token -> `401`
- authenticated but role not allowed -> `403`

### 5.3 Router Access Matrix

#### Super Admin Only

- `/api/settings/*`

#### Content Roles (`super_admin`, `content_admin`)

- `/api/knowledge-documents*`
- `/api/faqs*`
- `/api/scenic-areas*`
- `/api/scenic-spots*`
- `/api/route-templates*`
- `/api/route-recommendations/generate`
- `/api/digital-humans*`

#### Ops Roles (`super_admin`, `ops_admin`)

- `/api/dashboard*`
- `/api/sessions*`
- `/api/operation-logs*`

#### Any Authenticated Role

- `/api/auth/me`

## 6. Frontend Design

### 6.1 Auth Store

Extend the existing auth store so it keeps:

- `accessToken`
- `username`
- `role`
- `profileLoaded`

The store also needs:

- `setToken`
- `setProfile`
- `clearAuth`
- `fetchProfile`

`fetchProfile` calls `/api/auth/me` and updates the role state used by the router and sidebar.

### 6.2 Login Flow

After `/api/auth/login` succeeds:

1. save token
2. call `/api/auth/me`
3. save `username` and `role`
4. redirect to the role default page

### 6.3 Refresh Recovery

When the app refreshes and a token exists but no role is loaded:

- the route guard must call `fetchProfile`
- if profile recovery fails, clear auth and redirect to `/login`

### 6.4 Route Metadata

Protected routes get `meta.roles`.

Examples:

- content pages -> `['super_admin', 'content_admin']`
- ops pages -> `['super_admin', 'ops_admin']`
- settings pages -> `['super_admin']`

### 6.5 Sidebar Filtering

Sidebar items add the same role metadata and are filtered by the current role from the auth store.

Users should not see navigation entries they cannot access.

## 7. Redirect Rules

### 7.1 Default Landing Pages

- `super_admin` -> `/`
- `content_admin` -> `/knowledge/documents`
- `ops_admin` -> `/analytics/dashboard`

### 7.2 Guard Behavior

- unauthenticated access to protected route -> `/login`
- authenticated access to `/login` -> role default page
- authenticated but unauthorized route -> role default page

The frontend may show a lightweight message, but the redirect is the required behavior.

## 8. Error Handling

### 8.1 Backend

- unauthenticated -> `401`
- unauthorized -> `403`
- response body keeps a simple `detail` field
- do not expose extra internal information in permission errors

### 8.2 Frontend

- API `401` -> clear auth and redirect to `/login`
- API `403` -> keep auth, redirect to role default page
- route-level unauthorized access should be blocked before page render when possible

## 9. Testing Strategy

### 9.1 Backend

Add tests for:

- `/api/auth/me` returns the current username and role
- `content_admin` can access content-side routes
- `content_admin` gets `403` on ops-side routes
- `ops_admin` can access ops-side routes
- `ops_admin` gets `403` on content-side routes
- `super_admin` can access system settings routes

### 9.2 Frontend

Add tests for:

- login flow fetches `/auth/me` and stores role data
- sidebar filters entries by role
- route guard redirects unauthorized access to the correct default page

## 10. Risks And Constraints

- fixed-role RBAC is intentionally narrow; it solves current product-demo needs but does not support future fine-grained permission points
- route-level protection is sufficient for this slice because the codebase is already organized by feature routers and feature pages
- frontend route blocking improves experience, but backend authorization remains the only security boundary that matters
