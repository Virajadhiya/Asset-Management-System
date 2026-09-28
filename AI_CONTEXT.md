# PRAVI Bridge Platform — AI Development Rules

## Product

Government bridge lifecycle tracking platform inspired by MoRTH's IBMS and Indian Railways' BMS.
All demo data is synthetic. We do not claim access to or use of actual government datasets.

## Asset

Bridges only for MVP.

## Data

All data is synthetic/demo data. Primarily Gujarat-based coordinates but not exclusively.

## Backend

FastAPI + SQLAlchemy + Pydantic + Alembic.

## Frontend

React + TypeScript + Vite + Tailwind CSS + Leaflet (maps) + Recharts (charts).

## Database

PostgreSQL + PostGIS.

## Authentication

JWT (JSON Web Tokens). Stateless. Access token only for MVP.

## Authorization

Resource:action RBAC with 20 granular permissions.
Permissions: `bridge:read`, `bridge:create`, `bridge:update`, `bridge:delete`, `inspection:read`, `inspection:create`, `inspection:update`, `defect:create`, `defect:update`, `condition:read`, `condition:create`, `maintenance:read`, `maintenance:create`, `maintenance:update`, `maintenance:approve`, `lifecycle:read`, `lifecycle:create`, `audit:read`, `user:read`, `user:manage`.

## Roles

ADMIN, DEPARTMENT_HEAD, EXECUTIVE_ENGINEER, INSPECTOR, MAINTENANCE_OFFICER, VIEWER.
These are prototype roles, not official government designations.

---

## Critical Rules

### 1. Status Mutation

`bridges.current_status` may **ONLY** be changed by `lifecycle_service.py`.
No other service, API endpoint, or direct SQL update may modify this field.
The bridge update API endpoint must explicitly strip/ignore `current_status` from the request body.

### 2. Audit Trail

Every create, update, and delete operation on any entity must generate an `audit_logs` record
with `old_value` and `new_value` as JSONB.

### 3. Lifecycle Events

When an inspection is completed, maintenance is started/completed, or a status-changing action occurs,
the corresponding service must automatically create a `lifecycle_events` record.
The frontend should never need to manually create lifecycle events for system-generated actions.

### 4. No Invented Requirements

Do not invent new business requirements, entities, or fields beyond what is specified in the implementation plan.
If a feature seems needed, flag it — do not silently add it.

### 5. API Contract

Do not modify API request/response shapes without updating `docs/api-contract.md`.
The frontend depends on stable API contracts.

### 6. Database Schema

Do not modify database schema without updating `docs/data-model.md`.
All foreign-key dependencies must be created in dependency order. Never rely on model file order.

Required table creation order:
1. roles
2. permissions
3. role_permissions
4. users
5. bridges
6. bridge_locations
7. bridge_engineering
8. inspections
9. inspection_components
10. defects
11. condition_assessments
12. maintenance_records
13. lifecycle_events
14. audit_logs

### 7. RBAC Enforcement

RBAC must be enforced **server-side** on every API endpoint.
Hiding UI elements in React is NOT security. The backend must independently return 403 for unauthorized requests.

### 8. Health Index

The BHI formula is our prototype methodology (`prototype-v1`), not the official IBMS formula.
Store `calculation_version` with every condition assessment.
Age is one contributing factor — it does not directly equal structural deterioration.

### 9. Research Grounding

Use documented IBMS / Indian Railways BMS references for domain concepts.
Clearly distinguish government-backed concepts from our prototype design decisions.

---

## Conventions

### Python

- Python 3.11+
- Use `async def` for all API route handlers
- Use Pydantic v2 for all request/response schemas
- Use SQLAlchemy 2.0 style (mapped_column, etc.)
- Use `uuid.uuid4()` for all primary keys
- Use `TIMESTAMPTZ` (timezone-aware) for all timestamps

### TypeScript

- Strict mode enabled
- All API types defined in `src/types/`
- Use React hooks, no class components
- Use TanStack Query (React Query) for API state management
- Use React Router v6 for routing

### API

- All endpoints prefixed with `/api/`
- Pagination: `?page=1&limit=20`
- Filtering: query parameters (e.g., `?status=OPERATIONAL&district=Ahmedabad`)
- Error responses: `{ "detail": "..." }` with appropriate HTTP status codes
- All list endpoints return `{ "items": [...], "total": N, "page": N, "limit": N }`

### Git

- Commit messages: `feat:`, `fix:`, `chore:`, `docs:` prefixes
- One logical change per commit
