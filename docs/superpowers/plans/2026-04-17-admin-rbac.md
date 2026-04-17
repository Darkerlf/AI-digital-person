# Admin RBAC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add fixed-role RBAC to the admin backend and frontend so `super_admin`, `content_admin`, and `ops_admin` get the correct API access, route access, and sidebar visibility.

**Architecture:** Keep the backend as the authorization source of truth by extending the existing FastAPI auth dependencies with explicit role guards and wiring those guards into feature routers. Extend the Vue auth store to persist the current user profile, then use route metadata plus sidebar filtering to apply the same role model in the frontend for UX and navigation safety.

**Tech Stack:** Python 3.13, FastAPI, SQLAlchemy 2, Pydantic 2, pytest, Vue 3, TypeScript, Pinia, Vue Router, Axios, Vitest, Vite.

---

## File Structure

### Backend

- Modify: `backend/app/api/deps.py`
- Modify: `backend/app/api/routers/dashboard.py`
- Modify: `backend/app/api/routers/digital_humans.py`
- Modify: `backend/app/api/routers/faqs.py`
- Modify: `backend/app/api/routers/imports.py`
- Modify: `backend/app/api/routers/knowledge_documents.py`
- Modify: `backend/app/api/routers/operation_logs.py`
- Modify: `backend/app/api/routers/route_recommendations.py`
- Modify: `backend/app/api/routers/route_templates.py`
- Modify: `backend/app/api/routers/scenic_areas.py`
- Modify: `backend/app/api/routers/scenic_spots.py`
- Modify: `backend/app/api/routers/sessions.py`
- Modify: `backend/app/api/routers/settings.py`
- Modify: `backend/tests/conftest.py`
- Modify: `backend/tests/test_auth.py`
- Create: `backend/tests/test_rbac.py`

### Frontend

- Modify: `admin-web/src/stores/auth.ts`
- Modify: `admin-web/src/views/LoginView.vue`
- Modify: `admin-web/src/router/index.ts`
- Modify: `admin-web/src/components/AppSidebar.vue`
- Modify: `admin-web/src/api/client.ts`
- Modify: `admin-web/src/tests/LoginView.test.ts`
- Create: `admin-web/src/tests/AppSidebar.test.ts`
- Create: `admin-web/src/tests/router.test.ts`

## Task 1: Backend RBAC Guards

**Files:**
- Modify: `backend/tests/conftest.py`
- Modify: `backend/tests/test_auth.py`
- Create: `backend/tests/test_rbac.py`
- Modify: `backend/app/api/deps.py`
- Modify: `backend/app/api/routers/dashboard.py`
- Modify: `backend/app/api/routers/digital_humans.py`
- Modify: `backend/app/api/routers/faqs.py`
- Modify: `backend/app/api/routers/imports.py`
- Modify: `backend/app/api/routers/knowledge_documents.py`
- Modify: `backend/app/api/routers/operation_logs.py`
- Modify: `backend/app/api/routers/route_recommendations.py`
- Modify: `backend/app/api/routers/route_templates.py`
- Modify: `backend/app/api/routers/scenic_areas.py`
- Modify: `backend/app/api/routers/scenic_spots.py`
- Modify: `backend/app/api/routers/sessions.py`
- Modify: `backend/app/api/routers/settings.py`

- [ ] **Step 1: Write the failing backend RBAC tests**

```python
from fastapi.testclient import TestClient

from app.main import app


def test_auth_me_returns_username_and_role(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    response = client.get("/api/auth/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["username"] == "admin"
    assert response.json()["role"] == "super_admin"


def test_content_admin_is_blocked_from_ops_routes(test_db_session, content_auth_headers) -> None:
    client = TestClient(app)

    response = client.get("/api/dashboard/overview", headers=content_auth_headers)

    assert response.status_code == 403


def test_ops_admin_is_blocked_from_content_routes(test_db_session, ops_auth_headers) -> None:
    client = TestClient(app)

    response = client.get("/api/knowledge-documents", headers=ops_auth_headers)

    assert response.status_code == 403


def test_super_admin_can_access_settings_routes(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    response = client.get("/api/settings/ai-providers", headers=auth_headers)

    assert response.status_code == 200
```

- [ ] **Step 2: Run backend RBAC tests to verify they fail**

Run: `cd backend; .\.venv\Scripts\python -m pytest tests\test_auth.py tests\test_rbac.py -q`
Expected: FAIL because current fixtures only create `admin` with role `super_admin`, `/api/auth/me` returns `admin`, and content or ops role separation is not enforced yet.

- [ ] **Step 3: Write the minimal backend RBAC implementation**

```python
# backend/tests/conftest.py
@pytest.fixture()
def content_auth_headers(test_db_session) -> dict[str, str]:
    test_db_session.add(
        AdminUser(
            username="content_admin",
            password_hash=hash_password("content123"),
            role="content_admin",
            status="active",
        )
    )
    test_db_session.commit()
    client = TestClient(app)
    response = client.post("/api/auth/login", json={"username": "content_admin", "password": "content123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


# backend/app/api/deps.py
def require_roles(*roles: str):
    def dependency(current_user=Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return current_user

    return dependency


require_super_admin = require_roles("super_admin")
require_content_roles = require_roles("super_admin", "content_admin")
require_ops_roles = require_roles("super_admin", "ops_admin")


# backend/app/api/routers/scenic_areas.py
@router.get("")
def list_areas(_: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    ...


# backend/app/api/routers/dashboard.py
@router.get("/overview")
def get_dashboard_overview(_: object = Depends(require_ops_roles), db: Session = Depends(get_db)):
    ...


# backend/app/api/routers/settings.py
@router.get("/ai-providers")
def list_ai_providers(_: object = Depends(require_super_admin), db: Session = Depends(get_db)):
    ...
```

Implementation requirements inside this step:
- keep `/api/auth/me` available to any authenticated role
- move all content-side routers to `require_content_roles`
- move `imports` routes into content-side access because import pages already exist in the current admin UI
- move analytics, sessions, and operation-log routes to `require_ops_roles`
- move settings routes to `require_super_admin`
- keep auth error semantics as `401` for unauthenticated and `403` for forbidden

- [ ] **Step 4: Run backend RBAC tests to verify they pass**

Run: `cd backend; .\.venv\Scripts\python -m pytest tests\test_auth.py tests\test_rbac.py -q`
Expected: PASS with role-based tests green.

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/deps.py backend/app/api/routers/dashboard.py backend/app/api/routers/digital_humans.py backend/app/api/routers/faqs.py backend/app/api/routers/imports.py backend/app/api/routers/knowledge_documents.py backend/app/api/routers/operation_logs.py backend/app/api/routers/route_recommendations.py backend/app/api/routers/route_templates.py backend/app/api/routers/scenic_areas.py backend/app/api/routers/scenic_spots.py backend/app/api/routers/sessions.py backend/app/api/routers/settings.py backend/tests/conftest.py backend/tests/test_auth.py backend/tests/test_rbac.py
git commit -m "feat: add backend admin rbac guards"
```

## Task 2: Frontend Auth Profile State

**Files:**
- Modify: `admin-web/src/stores/auth.ts`
- Modify: `admin-web/src/views/LoginView.vue`
- Modify: `admin-web/src/tests/LoginView.test.ts`

- [ ] **Step 1: Write the failing frontend auth-state test**

```ts
import { createPinia, setActivePinia } from 'pinia'
import { describe, expect, it, vi } from 'vitest'

import { useAuthStore } from '../stores/auth'

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(async () => ({ data: { username: 'content_admin', role: 'content_admin' } })),
  },
}))

describe('auth store', () => {
  it('fetches and stores the current profile', async () => {
    vi.stubGlobal('localStorage', {
      getItem: vi.fn(() => 'token-1'),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    })

    setActivePinia(createPinia())
    const store = useAuthStore()

    await store.fetchProfile()

    expect(store.username).toBe('content_admin')
    expect(store.role).toBe('content_admin')
    expect(store.profileLoaded).toBe(true)
  })
})
```

- [ ] **Step 2: Run the auth-state test to verify it fails**

Run: `cd admin-web; npm.cmd run test -- LoginView`
Expected: FAIL because the current store only keeps `accessToken` and has no profile-loading logic.

- [ ] **Step 3: Write the minimal frontend auth-state implementation**

```ts
// admin-web/src/stores/auth.ts
export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('accessToken') ?? '',
    username: localStorage.getItem('username') ?? '',
    role: localStorage.getItem('role') ?? '',
    profileLoaded: false,
  }),
  actions: {
    setProfile(profile: { username: string; role: string }) {
      this.username = profile.username
      this.role = profile.role
      this.profileLoaded = true
      localStorage.setItem('username', profile.username)
      localStorage.setItem('role', profile.role)
    },
    async fetchProfile() {
      const response = await apiClient.get('/auth/me')
      this.setProfile(response.data)
      return response.data
    },
    clearAuth() {
      this.accessToken = ''
      this.username = ''
      this.role = ''
      this.profileLoaded = false
      localStorage.removeItem('accessToken')
      localStorage.removeItem('username')
      localStorage.removeItem('role')
    },
  },
})


// admin-web/src/views/LoginView.vue
const response = await apiClient.post('/auth/login', form)
authStore.setToken(response.data.access_token)
await authStore.fetchProfile()
await router.push(getDefaultRouteByRole(authStore.role))
```

Implementation requirements inside this step:
- preserve existing token storage behavior
- add a small helper for role default pages
- keep login error handling simple and unchanged in tone

- [ ] **Step 4: Run the auth-state test to verify it passes**

Run: `cd admin-web; npm.cmd run test -- LoginView`
Expected: PASS with the updated auth-store behavior.

- [ ] **Step 5: Commit**

```bash
git add admin-web/src/stores/auth.ts admin-web/src/views/LoginView.vue admin-web/src/tests/LoginView.test.ts
git commit -m "feat: persist admin auth profile"
```

## Task 3: Frontend Route Guards And Sidebar Filtering

**Files:**
- Modify: `admin-web/src/router/index.ts`
- Modify: `admin-web/src/components/AppSidebar.vue`
- Modify: `admin-web/src/api/client.ts`
- Create: `admin-web/src/tests/AppSidebar.test.ts`
- Create: `admin-web/src/tests/router.test.ts`

- [ ] **Step 1: Write the failing route/sidebar tests**

```ts
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { describe, expect, it } from 'vitest'

import AppSidebar from '../components/AppSidebar.vue'
import { useAuthStore } from '../stores/auth'

describe('AppSidebar', () => {
  it('shows only ops items for ops_admin', () => {
    setActivePinia(createPinia())
    const store = useAuthStore()
    store.setProfile({ username: 'ops_admin', role: 'ops_admin' })

    const wrapper = mount(AppSidebar, {
      global: {
        stubs: {
          RouterLink: { template: '<a><slot /></a>' },
        },
      },
    })

    expect(wrapper.text()).toContain('感受度报告')
    expect(wrapper.text()).not.toContain('知识管理')
  })
})
```

```ts
import { describe, expect, it, vi } from 'vitest'

import { router } from '../router'
import { useAuthStore } from '../stores/auth'

describe('router role guard', () => {
  it('redirects content_admin away from ops route', async () => {
    const store = useAuthStore()
    store.accessToken = 'token-1'
    store.setProfile({ username: 'content_admin', role: 'content_admin' })

    await router.push('/feedback-report')

    expect(router.currentRoute.value.fullPath).toBe('/knowledge/documents')
  })
})
```

- [ ] **Step 2: Run route/sidebar tests to verify they fail**

Run: `cd admin-web; npm.cmd run test -- AppSidebar router`
Expected: FAIL because the sidebar is static and the router guard only checks for token presence.

- [ ] **Step 3: Write the minimal route/sidebar implementation**

```ts
// admin-web/src/router/index.ts
type AdminRole = 'super_admin' | 'content_admin' | 'ops_admin'

function getDefaultRouteByRole(role: AdminRole | string): string {
  if (role === 'content_admin') return '/knowledge/documents'
  if (role === 'ops_admin') return '/analytics/dashboard'
  return '/'
}

router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  if (to.path !== '/login' && !authStore.accessToken) {
    return '/login'
  }
  if (authStore.accessToken && !authStore.profileLoaded) {
    try {
      await authStore.fetchProfile()
    } catch {
      authStore.clearAuth()
      return '/login'
    }
  }
  const roles = to.meta.roles as string[] | undefined
  if (roles && authStore.role && !roles.includes(authStore.role)) {
    return getDefaultRouteByRole(authStore.role)
  }
  if (to.path === '/login' && authStore.accessToken) {
    return getDefaultRouteByRole(authStore.role)
  }
  return true
})


// admin-web/src/components/AppSidebar.vue
const items = [
  { to: '/knowledge/documents', label: '知识管理', roles: ['super_admin', 'content_admin'] },
  { to: '/feedback-report', label: '感受度报告', roles: ['super_admin', 'ops_admin'] },
]

const visibleItems = computed(() => items.filter((item) => item.roles.includes(authStore.role || 'super_admin')))


// admin-web/src/api/client.ts
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('accessToken')
      localStorage.removeItem('username')
      localStorage.removeItem('role')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)
```

Implementation requirements inside this step:
- add `meta.roles` to all protected routes
- keep dashboard home available to `super_admin` and `ops_admin`
- keep imports available to `super_admin` and `content_admin`
- redirect `403` responses to the role default page without clearing auth
- do not create a new page for account info in this slice

- [ ] **Step 4: Run route/sidebar tests to verify they pass**

Run: `cd admin-web; npm.cmd run test -- AppSidebar router`
Expected: PASS with route redirect and menu filtering working.

- [ ] **Step 5: Commit**

```bash
git add admin-web/src/router/index.ts admin-web/src/components/AppSidebar.vue admin-web/src/api/client.ts admin-web/src/tests/AppSidebar.test.ts admin-web/src/tests/router.test.ts
git commit -m "feat: enforce frontend admin rbac"
```

## Task 4: Full Verification

**Files:**
- Modify: `backend/tests/test_rbac.py`
- Modify: `admin-web/src/tests/router.test.ts`
- Modify: `admin-web/src/tests/AppSidebar.test.ts`

- [ ] **Step 1: Run the full backend test suite**

Run: `cd backend; .\.venv\Scripts\python -m pytest tests -q`
Expected: PASS with auth, RBAC, and existing feature tests green.

- [ ] **Step 2: Run the full frontend test suite**

Run: `cd admin-web; npm.cmd run test`
Expected: PASS with login, sidebar, router, and existing view tests green.

- [ ] **Step 3: Run the frontend build**

Run: `cd admin-web; npm.cmd run build`
Expected: PASS and emit the production bundle.

- [ ] **Step 4: Apply the narrow verification polish**

```python
assert response.json()["detail"] == "Forbidden"
```

```ts
expect(wrapper.text()).not.toContain('AI 配置')
```

Apply this step only as narrowly as needed:
- keep role strings consistent between backend and frontend
- keep route default redirects aligned with the approved role model
- do not add new roles or pages during verification

- [ ] **Step 5: Commit**

```bash
git add backend/tests/test_rbac.py admin-web/src/tests/AppSidebar.test.ts admin-web/src/tests/router.test.ts
git commit -m "test: verify admin rbac slice"
```

## Self-Review

- Spec coverage: Task 1 covers backend role guards, `/api/auth/me`, and role-bound router access. Task 2 covers login-time profile fetch and persisted role state. Task 3 covers route metadata, route-guard enforcement, sidebar filtering, and frontend auth responses. Task 4 covers suite-level verification required by the spec.
- Placeholder scan: this plan avoids open-ended stubs and repeats concrete file paths, commands, and code snippets for each task.
- Type consistency: the plan consistently uses the same three roles, the same `/api/auth/me` profile fields, and the same default redirects across backend tests, auth store logic, router guards, and sidebar filtering.
