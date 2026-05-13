# LunchTogether — Thesis ↔ Codebase Alignment Plan

## Purpose

This document lists every concrete item described in [docs/thesis_report.md](thesis_report.md) that is **not yet present, partially implemented, or inconsistent with the actual code base**, together with a focused roadmap to close those gaps before the thesis defense.

It is intentionally narrow: anything the thesis already describes accurately is omitted. Each gap is tied back to the specific section of the thesis report that asserts it, the file/area of the code where the work has to land, and a rough effort estimate.

## Audit methodology

The thesis (`docs/thesis_report.md`, 1506 lines, 6 chapters) was compared section by section against:

- `backend/app/**` — 46 Python files
- `frontend/src/**` — 72 TypeScript / TSX files
- `.github/workflows/*` — 2 workflows (`ci.yml`, `deploy.yml`)
- `infrastructure/**` — `setup.sh`, `deploy.sh`, `nginx/`, `systemd/`, `scripts/`
- `docs/diagrams/**` — 7 mermaid files (created together with the thesis)
- `docs/` — adjacent documents (`business_requirements.txt`, `generated_report.txt`, etc.)

For every asserted feature, endpoint, file, permission rule, or test, the corresponding artifact was located and verified. Inconsistencies are listed below; matched items are omitted.

## High-level summary

| Category                                          | Severity | Approx. effort |
| ------------------------------------------------- | :------: | :------------: |
| Backend integration test suite (Chapter 6)        | Critical |   5–7 days     |
| Screenshots for thesis figures (Chapter 4, 5)     | Critical |   ½–1 day      |
| Small backend behaviour gaps (admin self-protect) | Medium   |   ½ day        |
| Thesis claim about `deploy.yml` being a "plan"    | Low      |   < 1 hour     |
| Add `ESLint` + `Vitest` (referenced in CI plan)   | Medium   |   1 day        |
| Add `Vitest` reference to thesis source list      | Low      |   negligible   |
| Minor frontend polish referenced in Chapter 4     | Low      |   1 day        |
| Documentation cross-links from thesis to code     | Low      |   ½ day        |

**Total budget**: ≈ 10 working days, of which integration tests dominate. Everything else combined fits inside ~3 days.

---

## Chapter 6 — Testing (largest gap)

The thesis describes a full integration test suite of ≈ 80 scenarios across 10 functional areas, plus a manual test catalogue and a requirements traceability matrix. **None of those tests exist yet**:

- `backend/tests/` directory does **not** exist in the repo.
- `.github/workflows/ci.yml` explicitly omits the test step (`# Tests step intentionally omitted: no pytest suite exists yet.`).
- Frontend has no `vitest.config.ts`, no `tests/`, and no test script in `frontend/package.json`.
- The dev-dependency block in `backend/pyproject.toml` already includes `pytest>=8`, `pytest-asyncio>=0.23`, and `httpx>=0.27`, so the libraries are available; only the suite itself is missing.

### 6.A. Backend test infrastructure (prerequisite)

Create the following skeleton **before** writing individual tests:

| Path                                       | Purpose                                                                                                   |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| `backend/tests/__init__.py`                | Empty package marker                                                                                      |
| `backend/tests/conftest.py`                | Root fixtures (see below)                                                                                 |
| `backend/tests/integration/__init__.py`    | Package marker                                                                                            |
| `backend/tests/integration/test_*.py`      | One file per functional area, per §6.4 of the thesis                                                       |
| `backend/pytest.ini` *(or in pyproject)*   | `asyncio_mode = "auto"`, `testpaths = ["tests"]`                                                          |
| `backend/.env.test` *(gitignored)* + sample| Test environment variables (`TEST_DATABASE_URL`, `JWT_SECRET_KEY=test-secret`, `UPLOAD_DIR=/tmp/uploads`) |

**Required fixtures in `conftest.py`** (per thesis §6.3):

- `engine` — session-scoped async engine bound to `TEST_DATABASE_URL`.
- `tables` — session-scoped, creates all tables on entry, drops on exit.
- `db` — function-scoped `AsyncSession` wrapped in an outer transaction that is rolled back at teardown (so each test sees a clean DB without recreating tables).
- `client` — `httpx.AsyncClient` with `ASGITransport(app=app)` and `app.dependency_overrides[get_db] = lambda: db`.
- `factory_user(email=..., role=..., is_active=True)` — creates and returns a `User`.
- `factory_group(owner: User)` — creates a group + admin membership + 5 admin permissions.
- `factory_group_with_members(owner, members: list[(User, GroupRole)])` — convenience helper.
- `auth_client(user)` / `admin_client(user)` — returns an `AsyncClient` that already has the JWT cookie set (call `/api/auth/login` once or set the cookie directly with `create_access_token`).

**CI integration** — once the suite exists, update `.github/workflows/ci.yml`:

- Add a `services:` block to `backend-lint` (or new `backend-test` job) starting `postgres:16` with `POSTGRES_PASSWORD=test` and `POSTGRES_DB=test`.
- Run `uv run pytest -v` after `uv sync --dev`.
- Pass `DATABASE_URL=postgresql+asyncpg://postgres:test@localhost:5432/test`, `JWT_SECRET_KEY=test-secret`, `UPLOAD_DIR=/tmp/uploads`.

### 6.B. Test implementation per area

Implement the test files documented in thesis §6.4 (each row = one `async def test_*` function). Estimated counts come straight from the thesis tables.

| File                                                    | Source section | # of tests |
| ------------------------------------------------------- | -------------- | :--------: |
| `tests/integration/test_auth.py`                        | §6.4.1         |    11      |
| `tests/integration/test_users.py`                       | §6.4.2         |     7      |
| `tests/integration/test_groups.py`                      | §6.4.3         |     8      |
| `tests/integration/test_invitations.py`                 | §6.4.4         |    11      |
| `tests/integration/test_permissions.py`                 | §6.4.5         |     8      |
| `tests/integration/test_restaurants.py`                 | §6.4.6         |     6      |
| `tests/integration/test_order_lifecycle.py`             | §6.4.7         |    19      |
| `tests/integration/test_delivery_fee.py`                | §6.4.8         |     6      |
| `tests/integration/test_balances.py`                    | §6.4.9         |     7      |
| `tests/integration/test_analytics.py`                   | §6.4.10        |     7      |
| **Total**                                               |                |  **90**    |

Two test ideas in the thesis tables expose real bugs/missing behaviour in the code — flag them while implementing (see §3.A below).

### 6.C. Manual test plan document

Thesis §6.5 references a manual test template. Add a sibling document `docs/manual_test_plan.md` containing:

- The template table (ID, передумова, кроки, очікуваний результат, фактичний результат, статус, скріншот).
- The five worked examples already drafted in §6.5 (MT-LOGIN-1, MT-INVITE-1, MT-ORDER-FULL, MT-BALANCE-ADJ, MT-NAV-CONTEXT, MT-RESP-1).
- A blank table the user can extend during defense preparation.

### 6.D. Frontend tests (optional but referenced)

The thesis §5.10 CI table says *"тестового раннера для фронтенду ще не налаштовано"*, so this is technically consistent with reality. However, the wording in §6 implies the project will eventually have one. Decision needed:

- **Option A (minimal)**: leave as-is; reference Vitest as "future work" — but the thesis explicitly excludes a future-work section, so this is awkward.
- **Option B (recommended)**: add a thin Vitest setup with 3-5 smoke tests (e.g. `combobox.test.tsx`, `useLoginForm.test.ts`, `Sidebar.test.tsx` context-switch). Add `npm run test` step to `frontend-build` job.

Choose Option B unless time is tight: it removes an awkwardness from the report and gives the defense panel a clean answer to "did you test the frontend?".

---

## Chapter 5 — Deployment (mostly aligned; one inversion)

### 5.A. `deploy.yml` already exists — fix the thesis cross-reference

Thesis §5.11 says:

> «У майбутньому розширенні конвеєра CI/CD буде додано окремий workflow `deploy.yml`, який після успішного завершення `ci.yml` на гілці `main` підключається до сервера через SSH та запускає `./infrastructure/deploy.sh`. У межах цієї роботи такий workflow задокументовано у документі [docs/implementation_plan_deployment.md](implementation_plan_deployment.md) як план реалізації.»

But [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml) is **already implemented and active**: it runs on push to `main`, sets up SSH from `SSH_PRIVATE_KEY`/`SERVER_HOST`/`SERVER_USER` secrets, runs the same steps that `deploy.sh` runs (git fetch/reset, `uv sync`, `alembic upgrade head`, systemctl restart, `npm ci && npm run build`, nginx reload), and finishes with a health check against `https://$DOMAIN/api/health`.

**Action**: rewrite §5.11 of the thesis to describe `deploy.yml` as a real artifact, mention the three secrets (`SSH_PRIVATE_KEY`, `SERVER_HOST`, `SERVER_USER`, `DOMAIN`), and add a §5.10 table row in §5.10 calling out the second workflow. Replace the screenshot placeholder `5.11.1` with a real screenshot of a successful `deploy.yml` run.

### 5.B. Sentry vs `.env`

Thesis §5.9 says Sentry init reads `SENTRY_DSN` from the environment — code matches (`config.py: sentry_dsn: str = ""`, `main.py: if settings.sentry_dsn: sentry_sdk.init(...)`). The `setup.sh` step 13 already writes `SENTRY_DSN=$SENTRY_DSN` to the production `.env`. No code change required, but verify the screenshot for §5.9.1 (Sentry dashboard) shows real events from the deployed instance — otherwise grade panel may flag it.

### 5.C. UFW firewall — claim vs reality

The thesis §1.6 deliberately does **not** mention UFW (per the user's explicit choice during planning), but `infrastructure/setup.sh` step 17 does configure it. This is OK as-is — the deployment script is more cautious than the document. No action needed unless reviewer flags it.

---

## Chapter 3 — Backend (small but real gaps)

### 3.A. Admin self-protection (FR not enforced)

Thesis §6.4.2, test **T-USER-7** asserts:

> `test_admin_cannot_deactivate_self` — Адмін; PATCH `/api/users/{self_id}` із `is_active: false` → **403** (захист від самовиключення).

Current code in [`backend/app/api/users.py`](../backend/app/api/users.py) does **not** enforce this. The `admin_update_user` endpoint (`PUT /{user_id}/admin`) accepts arbitrary `AdminUserUpdate` including `is_active=False` even when `user_id == current_user.id`. The thesis treats this as already implemented in the FR/test matrix.

**Fix** (in `api/users.py`, both `update_user` and `admin_update_user`):

```python
if user_id == current_user.id and data.is_active is False:
    raise ForbiddenError(detail="You cannot deactivate your own account")
if user_id == current_user.id and data.role is not None and data.role != current_user.role:
    raise ForbiddenError(detail="You cannot change your own role")
```

### 3.B. `PATCH /api/users/{user_id}` vs `PUT /api/users/{user_id}/admin`

Thesis §2.4 lists a single line:

> `PATCH /api/users/{user_id}` — Зміна ролі/активності користувача (Admin) або профілю

In reality there are **two** endpoints: a `PATCH` (self-update or limited admin update via `UserUpdate` schema, which does **not** include `role`/`is_active`) and a `PUT /{user_id}/admin` (admin-only update via `AdminUserUpdate`, which does).

**Fix options**:

- **(A)** Adjust the thesis table to list both endpoints separately. This is the cleanest path — change a single line in §2.4.
- **(B)** Collapse the two endpoints in code into a single PATCH that branches on `current_user.role`. Higher risk and changes the API surface; do not pick this unless §A is unacceptable.

Use **(A)**.

### 3.C. Endpoint shape: permissions update path

Thesis §2.4 lists:

> `PATCH /api/groups/{group_id}/members/{user_id}/permissions` — Зміна дозволів учасника

The actual endpoint is `PATCH /api/groups/{group_id}/members/{member_user_id}` (no `/permissions` suffix), and the payload (`GroupMemberUpdate`) carries `role` + `permissions[]` together.

**Fix**: change the thesis row to:

> `PATCH /api/groups/{group_id}/members/{member_user_id}` — Зміна ролі та дозволів учасника

### 3.D. Group analytics endpoint actually lives at root

Thesis §2.4 places `GET /api/groups/{group_id}/analytics` and `GET /api/users/me/analytics` under tag *analytics*. Code matches — `api/analytics.py` declares `APIRouter(tags=["analytics"])` without a prefix and registers two routes manually. No action.

### 3.E. `Balance:Viewer` returns balances; thesis claim

Thesis §2.5 says `Balances:None → "приховано"`. The code in `api/balances.py::_check_balance_permission` raises **403** when level is `None`. That matches.

But the thesis also says (T-BAL-2 in §6.4.9) that the **adjust** endpoint requires Editor. Code matches via `require_editor=True`. Good.

### 3.F. `/api/auth/me` returning `is_admin`

Thesis §3.7 step 7 says `get_current_user` returns the `User` object. Frontend code in `useAuth` reads `user.role === "admin"` (e.g. Sidebar.tsx line 249). Verify the `UserResponse` schema exposes `role` — it does. No action.

### 3.G. `ExecStartPre` of migrations vs `deploy.sh`

Thesis §5.6 explicitly explains that migrations are **not** run via `ExecStartPre`, and the systemd unit file confirms this with a comment. Aligned, no action.

### 3.H. Workflow names cited in §3.5

Thesis §3.5 names the workflows:

- `RegisterWorkflow` ✓
- `LoginWorkflow` ✓
- `CreateGroupWorkflow` ✓
- `ManageMembersWorkflow` ✓
- `InviteWorkflow` ✓ (thesis also mentions `InviteWorkflow.accept` — that is a method, not a separate class — matches)
- `CreateOrderWorkflow` ✓
- `OrderLifecycleWorkflow` ✓
- `AdjustBalanceWorkflow` ✓

All accounted for. No action.

---

## Chapter 4 — Frontend (mostly aligned)

### 4.A. Dark mode / next-themes

Thesis §4.6 says:

> «Підключена бібліотека `next-themes` для перемикання теми, проте її використання обмежене базовою інфраструктурою — повноцінна реалізація темної теми позиціонується як майбутній етап.»

This contradicts the thesis decision **not** to include a "future work" section in the conclusions. Two options:

- **(A)** Remove `next-themes` from `frontend/package.json` (it's not used anywhere) and delete the sentence from §4.6. Clean and honest.
- **(B)** Actually implement a `ThemeProvider` wrapper around `RouterProvider` and a toggle in the Header. ½ day of work, adds genuine value.

Prefer **(B)** since the dependency is already there.

### 4.B. `ESLint` config

Thesis §5.10 calls out that "ESLint and test steps intentionally omitted: no ESLint config or test runner is set up yet". This is faithful to the current state but inconsistent with the thesis §4.2 phrase listing ESLint in the toolchain.

**Fix**: either (a) drop ESLint from the §4.2 toolchain list, or (b) add `eslint.config.js` with `@typescript-eslint`, `eslint-plugin-react`, `eslint-plugin-react-hooks`, run `npm run lint` in CI. **Prefer (b)** — it's a half-day item that closes a real gap.

### 4.C. Screenshot placeholders → real screenshots

Thesis chapters 4–5 contain 26 screenshot placeholders pointing at `docs/screenshots/*.png`. The directory does not exist yet. Each placeholder line is grep-able for find/replace:

```
> _Рис. X.Y.Z. <description> — `screenshots/<filename>.png`_
```

**Action list** (one PNG per row):

| File                                  | Captured from                                                              |
| ------------------------------------- | -------------------------------------------------------------------------- |
| `sidebar_home_context.png`            | Header + Sidebar, route `/`                                                |
| `sidebar_group_context.png`           | Header + Sidebar, route `/groups/:id`                                      |
| `login_page.png`                      | `/login`                                                                   |
| `register_page.png`                   | `/register`                                                                |
| `user_dashboard.png`                  | `/`                                                                        |
| `settings_page.png`                   | `/settings`                                                                |
| `group_list.png`                      | `/groups`                                                                  |
| `group_dashboard.png`                 | `/groups/:id` with an active order (so the banner shows)                   |
| `group_members.png`                   | `/groups/:id/members`                                                      |
| `invite_dialog.png`                   | `/groups/:id/members` with the invite dialog open                          |
| `profile_page.png`                    | `/profile`                                                                 |
| `users_list.png`                      | `/users` as admin                                                          |
| `restaurants_list.png`                | `/groups/:id/restaurants`                                                  |
| `restaurant_detail.png`               | `/groups/:id/restaurants/:rid`                                             |
| `order_list.png`                      | `/groups/:id/orders`                                                       |
| `order_create_dialog.png`             | Order list with the Combobox dialog open and typing                        |
| `order_initiated.png`                 | Order detail in Initiated state, 2-3 items                                 |
| `order_confirmed.png`                 | Order detail in Confirmed state with delivery fee input visible            |
| `order_finished.png`                  | Order detail in Finished state                                             |
| `balances_page.png`                   | `/groups/:id/balances`                                                     |
| `balance_adjust_dialog.png`           | Balances page with the adjust dialog open                                  |
| `balance_history.png`                 | Balances page with one user's history row expanded                         |
| `combobox_create.png`                 | Order create dialog, Combobox showing the "Create …" suggestion            |
| `sentry_dashboard.png`                | Sentry web UI showing real events from the deployed instance               |
| `github_actions_ci.png`               | GitHub Actions run page showing successful CI                              |
| `deploy_script_output.png`            | Terminal output of `./infrastructure/deploy.sh` on a real deployment       |

Store under `docs/screenshots/`. The placeholder lines do not need to change — they already point at this exact path.

### 4.D. Pages claimed in §4.7 vs implemented

All pages mentioned in §4.7 exist. Verified file-by-file:

- `LoginPage`, `RegisterPage` — `modules/auth/pages/` ✓
- `UserDashboardPage`, `SettingsPage` — `modules/dashboard/pages/` ✓
- `GroupListPage`, `GroupDetailPage`, `GroupMembersPage` — `modules/group/pages/` ✓
- `ProfilePage`, `UserListPage`, `UserDetailPage` — `modules/user/pages/` ✓
- `RestaurantListPage`, `RestaurantDetailPage` — `modules/restaurant/pages/` ✓
- `OrderListPage`, `OrderDetailPage` — `modules/order/pages/` ✓
- `BalancesPage` — `modules/balance/pages/` ✓

No code changes needed.

### 4.E. `Combobox` "Create …" suggestion claim

Thesis §4.8 says the Combobox shows "Create …" only when the typed text does not match any option. This matches `frontend/src/components/ui/combobox.tsx` (already verified during integration into `OrderListPage`). No action.

---

## Chapter 2 — Architecture (aligned, one wording fix)

### 2.A. Endpoint table line cleanup

Apply the four small text fixes already listed under §3.B and §3.C (separate `PUT` for admin user update; correct path for member permission update).

### 2.B. ER diagram entity list

Thesis §2.3 names exactly 12 entities and they match `backend/app/models/__init__.py`'s `__all__`. The diagram file `docs/diagrams/02_er_diagram.md` lists all 12. No action.

### 2.C. `Numeric(10, 2)` for money

Verified: every monetary column (`Order.delivery_fee_total`, `Order.delivery_fee_per_person`, `OrderItem.price`, `Dish.price`, `Balance.amount`, `BalanceHistory.amount`, `BalanceHistory.balance_after`) is `Numeric(10, 2)`. No action.

---

## Cross-chapter polish

### P1. References list pruning

Thesis bibliography lists Vitest as planned (per the original plan: "Vitest (referenced as alternative)"), but no Vitest reference made it into the final §"СПИСОК ВИКОРИСТАНИХ ДЖЕРЕЛ". Either add it (if §4.D Option B is taken) or remove the implicit promise from the plan. **No-op** in the deliverable unless §4.D Option B is taken.

### P2. Conformance of `infrastructure/implementation_plan_deployment.md` reference

Thesis §5.11 mentions [`docs/implementation_plan_deployment.md`](implementation_plan_deployment.md). The doc exists. After §5.A above the wording will say "see for the original implementation plan" rather than "documented as a plan to implement". One-line edit.

### P3. Per-chapter "Висновки до розділу" sanity check

All six chapters have them. Verified by grep `^### .*Висновки до розділу` against `docs/thesis_report.md`. No action.

---

## Phased roadmap

### Phase 1 — Critical (≈ 6 days)

1. **Backend test infrastructure** (§6.A) — 1 day.
2. **Implement integration tests** (§6.B) — 4 days, prioritised:
   1. Auth + Users + Groups + Invitations (≈ 1.5 days)
   2. Permissions + Restaurants (≈ 1 day)
   3. Order lifecycle + Delivery fee (≈ 1 day, this is the most business-critical area)
   4. Balances + Analytics (≈ 0.5 day)
3. **Wire tests into CI** — ½ day.

After Phase 1 the largest thesis claim is true.

### Phase 2 — Important (≈ 2 days)

4. **Admin self-protection fix** (§3.A) — 1 hour + 2 tests.
5. **Thesis endpoint-table corrections** (§3.B, §3.C) — 30 min.
6. **Rewrite thesis §5.11** to describe the real `deploy.yml` (§5.A) — 1 hour.
7. **Capture all 26 screenshots** (§4.C) — ½ day.
8. **ESLint setup** (§4.B Option b) — ½ day.
9. **Vitest smoke tests** (§6.D Option B) — ½ day.

### Phase 3 — Polish (≈ 1 day)

10. **Theme toggle wired up via `next-themes`** (§4.A Option B) — ½ day.
11. **Manual test plan document** (§6.C) — 2 hours.
12. **Sanity sweep**: re-run thesis grep against codebase, fix any new drift — 2 hours.

---

## Acceptance criteria

The codebase matches the thesis once **all** of the following are true:

- [ ] `cd backend && uv run pytest` runs 80+ integration tests, all green.
- [ ] `.github/workflows/ci.yml` invokes `pytest` with a `postgres:16` service and the job is green on `main`.
- [ ] `cd frontend && npm run lint && npm run test && npm run type-check && npm run build` all pass locally.
- [ ] `docs/screenshots/` contains the 26 PNGs listed in §4.C, each readable at 1920×1080 or matching the surrounding text.
- [ ] Admin cannot deactivate their own account via either user-update endpoint (verified by `test_admin_cannot_deactivate_self`).
- [ ] Thesis §2.4 endpoint table lists the real two endpoints for user update and the real path for member permission update.
- [ ] Thesis §5.11 describes the existing `deploy.yml` rather than treating it as a plan.
- [ ] `docs/manual_test_plan.md` exists with the template and the six worked examples.
- [ ] Thesis bibliography reflects the final state of the source list (Vitest in or out, depending on §6.D decision).

When every box is checked, every assertion in `docs/thesis_report.md` is grounded in a real artifact in the repository.
