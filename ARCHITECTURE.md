# PRAVI — System Architecture

> **Bridge Lifecycle & Management Platform**  
> Inspired by MoRTH's IBMS and Indian Railways' BMS  
> All data is synthetic/demo — no actual government datasets used

---

## 1. High-Level System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              PRAVI PLATFORM                                  │
│                                                                              │
│  ┌─────────────────────────┐        REST API        ┌────────────────────┐  │
│  │     FRONTEND (SPA)      │ ◄──────────────────────► │     BACKEND API    │  │
│  │                         │   JSON / JWT Bearer     │                    │  │
│  │  React 18 + TypeScript  │   Port 5173 → 8000     │  FastAPI (Python)  │  │
│  │  Vite + Tailwind CSS    │                         │  SQLAlchemy 2.0    │  │
│  │  Leaflet (GIS Maps)     │                         │  Pydantic v2       │  │
│  │  TanStack Query         │                         │                    │  │
│  └─────────────────────────┘                         └────────┬───────────┘  │
│                                                               │              │
│                                                    ┌──────────▼───────────┐  │
│                                                    │     DATABASE          │  │
│                                                    │                      │  │
│                                                    │  PostgreSQL + PostGIS │  │
│                                                    │  (SQLite for dev)    │  │
│                                                    │  14 Tables           │  │
│                                                    └──────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Backend Architecture

```
backend/
├── app/
│   ├── main.py                  # FastAPI app, CORS, lifespan (auto-create tables)
│   ├── config.py                # Settings (DATABASE_URL, SECRET_KEY, JWT config)
│   ├── database.py              # AsyncSession engine + get_db dependency
│   │
│   ├── api/                     # Route handlers (controllers)
│   │   ├── router.py            # Central router — mounts all sub-routers
│   │   ├── auth.py              # POST /login, GET /me
│   │   ├── bridges.py           # CRUD + GET /{id}/issues
│   │   ├── inspections.py       # CRUD + component ratings + counter-sign
│   │   ├── maintenance.py       # CRUD + workflow status transitions
│   │   ├── lifecycle.py         # Event log + status transitions
│   │   ├── issues.py            # Distress reports + assign + resolve
│   │   ├── dashboard.py         # Summary stats + priority list
│   │   ├── gis.py               # GIS bridge data for map visualization
│   │   └── audit.py             # Audit log viewer
│   │
│   ├── middleware/              # Security middleware
│   │   ├── auth.py              # JWT token validation → get_current_user
│   │   └── rbac.py              # require_permission(resource, action)
│   │
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── __init__.py          # Base + all model imports (dependency order)
│   │   ├── user.py              # Role, Permission, RolePermission, User
│   │   ├── bridge.py            # Bridge, BridgeLocation, BridgeEngineering
│   │   ├── inspection.py        # Inspection, InspectionComponent, Defect
│   │   ├── condition.py         # ConditionAssessment
│   │   ├── maintenance.py       # MaintenanceRecord
│   │   ├── lifecycle.py         # LifecycleEvent
│   │   ├── issue.py             # DistressIssue
│   │   ├── audit.py             # AuditLog
│   │   └── enums.py             # All enum definitions
│   │
│   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── auth.py              # Token, LoginRequest
│   │   ├── bridge.py            # BridgeCreate, BridgeUpdate, BridgeResponse
│   │   ├── inspection.py        # InspectionCreate, InspectionResponse
│   │   ├── maintenance.py       # MaintenanceCreate, MaintenanceResponse
│   │   ├── lifecycle.py         # LifecycleEventCreate
│   │   ├── issue.py             # DistressIssueCreate/Assign/Resolve
│   │   ├── dashboard.py         # DashboardSummary
│   │   └── common.py            # PaginatedResponse
│   │
│   ├── services/                # Business logic layer
│   │   ├── bridge_service.py    # Bridge CRUD + detail assembly
│   │   ├── inspection_service.py# Inspection + auto condition assessment
│   │   ├── maintenance_service.py# Maintenance workflow state machine
│   │   ├── lifecycle_service.py # Status transitions + event logging
│   │   ├── health_index.py      # Bridge Health Index (BHI) calculation
│   │   ├── dashboard_service.py # Aggregation queries for dashboard
│   │   ├── audit_service.py     # Audit log creation
│   │   └── auth_service.py      # Password hashing + token generation
│   │
│   └── seed/
│       └── seed_data.py         # Demo data seeder (roles, users, bridges)
│
├── Dockerfile
├── requirements.txt
└── alembic.ini
```

---

## 3. Frontend Architecture

```
frontend/
├── src/
│   ├── main.tsx                 # React entry point
│   ├── App.tsx                  # Router + providers (Auth, Asset, QueryClient)
│   ├── index.css                # Tailwind imports + global styles
│   │
│   ├── api/
│   │   ├── client.ts            # Axios instance + JWT interceptor
│   │   └── endpoints.ts         # All API functions (typed)
│   │
│   ├── context/
│   │   ├── AuthContext.tsx       # Auth state (user, token, login/logout)
│   │   └── AssetContext.tsx      # Multi-asset type switcher
│   │
│   ├── types/
│   │   └── index.ts             # All TypeScript interfaces
│   │
│   ├── pages/
│   │   ├── Login.tsx            # Login form
│   │   ├── Dashboard.tsx        # Overview stats, charts, priority list
│   │   ├── BridgeList.tsx       # Paginated asset registry
│   │   ├── BridgeDetail.tsx     # Full detail view (tabs: overview, inspections,
│   │   │                        #   maintenance, issues, lifecycle)
│   │   ├── InspectionForm.tsx   # Component-level inspection with geofencing
│   │   ├── IssueRegistry.tsx    # Distress incidents + task allocation
│   │   ├── MapView.tsx          # Leaflet GIS map with condition markers
│   │   └── AuditLogs.tsx        # Audit trail viewer
│   │
│   └── components/
│       ├── layout/
│       │   ├── AppLayout.tsx    # Sidebar navigation + main content area
│       │   ├── AssetSwitcher.tsx # Asset type tabs (Bridge/Tunnel/Highway/Culvert)
│       │   └── ProtectedRoute.tsx# Auth + permission guard
│       └── common/
│           ├── StatusBadge.tsx   # Colored status indicator
│           ├── ConditionBadge.tsx# Health condition badge
│           └── PriorityBadge.tsx # Priority level badge
│
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── Dockerfile
```

---

## 4. API Endpoint Map

```
/api
├── /auth
│   ├── POST   /login                    # OAuth2 password grant → JWT
│   └── GET    /me                       # Current user profile + permissions
│
├── /bridges
│   ├── GET    /                          # List (filter: status, district, type, search)
│   ├── POST   /                          # Create bridge + location + engineering
│   ├── GET    /{id}                      # Full detail (location, engineering, condition,
│   │                                     #   latest inspection, active maintenance)
│   ├── PUT    /{id}                      # Update bridge
│   ├── DELETE /{id}                      # Delete bridge + cascade
│   ├── GET    /{id}/inspections          # Bridge's inspections
│   ├── POST   /{id}/inspections          # Create inspection for bridge
│   ├── GET    /{id}/maintenance          # Bridge's maintenance records
│   ├── POST   /{id}/maintenance          # Create maintenance for bridge
│   ├── GET    /{id}/lifecycle            # Bridge's lifecycle events
│   ├── POST   /{id}/lifecycle            # Create lifecycle event
│   └── GET    /{id}/issues              # Bridge's distress issues
│
├── /inspections
│   ├── GET    /{id}                      # Inspection detail + components + defects
│   └── POST   /{id}/counter-sign        # Executive engineer verification
│
├── /maintenance
│   └── PUT    /{id}/status               # Workflow: REPORTED → ESTIMATED → SANCTIONED
│                                         #   → TENDER_AWARDED → IN_PROGRESS → COMPLETED
│                                         #   → VERIFIED
│
├── /issues
│   ├── GET    /                          # List distress issues (filter: status, severity)
│   ├── POST   /                          # Report distress incident
│   ├── PUT    /{id}/assign              # Assign inspector + engineer + target date
│   ├── PUT    /{id}/resolve             # Mark resolved/closed
│   └── GET    /assignable-officers      # Officers available for assignment
│
├── /lifecycle
│   ├── GET    /                          # All lifecycle events
│   └── POST   /transition               # Status transition (state machine)
│
├── /dashboard
│   ├── GET    /summary                   # Stats: by status, condition, critical count
│   └── GET    /priority-list            # Priority-ranked bridges
│
├── /gis
│   └── GET    /bridges                   # Lightweight bridge data for map markers
│
└── /audit
    └── GET    /logs                      # Audit trail (filter: entity, action, user)
```

---

## 5. Database Schema (Entity Relationship)

```
┌──────────┐     ┌──────────────┐     ┌────────────────┐
│  roles   │────►│role_permissions│◄────│  permissions   │
└────┬─────┘     └──────────────┘     └────────────────┘
     │                                  20 resource:action
     │ 1:N                              permissions
┌────▼─────┐
│  users   │ ──────────────────────────────────────────────┐
└────┬─────┘                                                │
     │ FK                                                   │
     ▼                                                      │
┌──────────┐  1:1  ┌──────────────────┐                    │
│ bridges  │──────►│ bridge_locations  │                    │
│          │       └──────────────────┘                    │
│          │  1:1  ┌──────────────────┐                    │
│          │──────►│bridge_engineering │                    │
│          │       └──────────────────┘                    │
│          │                                               │
│          │  1:N  ┌──────────────┐  1:N ┌──────────────┐ │
│          │──────►│ inspections  │─────►│ inspection_  │ │
│          │       │              │      │ components   │ │
│          │       │              │ 1:N  └──────────────┘ │
│          │       │              │─────►┌──────────────┐ │
│          │       └──────────────┘      │   defects    │ │
│          │                             └──────────────┘ │
│          │  1:N  ┌──────────────────┐                   │
│          │──────►│condition_         │                   │
│          │       │assessments        │                   │
│          │       └──────────────────┘                   │
│          │  1:N  ┌──────────────────┐                   │
│          │──────►│maintenance_       │                   │
│          │       │records            │                   │
│          │       └──────────────────┘                   │
│          │  1:N  ┌──────────────────┐                   │
│          │──────►│lifecycle_events   │                   │
│          │       └──────────────────┘                   │
│          │  1:N  ┌──────────────────┐                   │
│          │──────►│distress_issues   │◄──────────────────┘
└──────────┘       │ (assigned_       │  (assigned_inspector_id,
                   │  inspector/eng)  │   assigned_engineer_id,
                   └──────────────────┘   reported_by_id → users)

┌──────────────┐
│  audit_logs  │  ← Every create/update/delete across all entities
└──────────────┘
```

**Total: 15 tables** (including `distress_issues`)

---

## 6. Security Architecture

```
┌────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Browser   │────►│  JWT Token   │────►│ Auth Middleware  │
│  (Axios    │     │ (Bearer)     │     │ get_current_user │
│  Intercep) │     │ localStorage │     │ decode + verify  │
└────────────┘     └──────────────┘     └────────┬────────┘
                                                  │
                                        ┌─────────▼────────┐
                                        │ RBAC Middleware   │
                                        │ require_permission│
                                        │ (resource:action) │
                                        └────────┬─────────┘
                                                 │
                                        ┌────────▼─────────┐
                                        │  Route Handler   │
                                        │  (if authorized) │
                                        └──────────────────┘
```

### Roles & Permissions Matrix

| Role                | Key Permissions                                           |
|---------------------|----------------------------------------------------------|
| **ADMIN**           | Full superuser access to all resources                    |
| **DEPARTMENT_HEAD** | bridge:*, inspection:*, maintenance:approve, user:read    |
| **EXECUTIVE_ENGINEER** | bridge:read/update, inspection:*, maintenance:*        |
| **INSPECTOR**       | bridge:read, inspection:create/update, defect:create      |
| **MAINTENANCE_OFFICER** | bridge:read, maintenance:create/update                |
| **VIEWER**          | bridge:read, inspection:read, condition:read              |

---

## 7. Bridge Health Index (BHI) — Prototype Formula

```
BHI = 0.40 × Structural + 0.30 × Functional + 0.20 × Safety + 0.10 × Age Factor

Structural Score:
  Weighted average of component ratings (1–5 → 0–100%)
  ┌──────────────────┬────────┐
  │ Component        │ Weight │
  ├──────────────────┼────────┤
  │ Deck             │  0.25  │
  │ Superstructure   │  0.25  │
  │ Substructure     │  0.20  │
  │ Foundation       │  0.15  │
  │ Bearings         │  0.10  │
  │ Expansion Joints │  0.05  │
  └──────────────────┴────────┘

Age Factor = max(0, 100 - (age / design_life × 100))

Category:
  ≥ 85 → EXCELLENT
  ≥ 70 → GOOD
  ≥ 55 → FAIR
  ≥ 40 → POOR
  < 40 → CRITICAL
```

---

## 8. Key Workflows

### Maintenance Workflow (State Machine)
```
REPORTED → ESTIMATED → SANCTIONED → TENDER_AWARDED → IN_PROGRESS → COMPLETED → VERIFIED
                                                                          ↓
                                                                      CANCELLED
```

### Distress Issue Workflow
```
OPEN → ASSIGNED → UNDER_INSPECTION → RESOLVED
                                         ↓
                                      CLOSED
```

### Bridge Lifecycle States
```
PLANNED → UNDER_CONSTRUCTION → OPERATIONAL → UNDER_MAINTENANCE → OPERATIONAL
                                     ↓               ↑
                              UNDER_REHABILITATION ───┘
                                     ↓
                                  CLOSED → DECOMMISSIONED
```

---

## 9. Deployment Architecture

```
┌─── Docker Compose ────────────────────────────────────────┐
│                                                            │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────────┐ │
│  │   Frontend   │  │    Backend    │  │   Database     │ │
│  │              │  │               │  │                │ │
│  │  Node.js     │  │  Python 3.11  │  │  PostGIS       │ │
│  │  Vite Dev    │  │  Uvicorn      │  │  16-3.4        │ │
│  │  Port: 5173  │──│  Port: 8000   │──│  Port: 5432    │ │
│  │              │  │               │  │                │ │
│  └──────────────┘  └───────────────┘  └────────────────┘ │
│                                                            │
└────────────────────────────────────────────────────────────┘

Local Dev: SQLite (aiosqlite) — zero-config, single file
Production: PostgreSQL + PostGIS — spatial queries, concurrency
```

---

## 10. Technology Stack Summary

| Layer        | Technology                                          |
|--------------|-----------------------------------------------------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS            |
| **State**    | TanStack Query (server state), React Context (auth) |
| **Maps**     | Leaflet + react-leaflet                             |
| **Charts**   | Recharts                                            |
| **HTTP**     | Axios with JWT interceptor                          |
| **Routing**  | React Router v6                                     |
| **Backend**  | FastAPI, Python 3.11+                               |
| **ORM**      | SQLAlchemy 2.0 (async), Pydantic v2                 |
| **Auth**     | JWT (python-jose), OAuth2 password flow             |
| **Database** | PostgreSQL + PostGIS / SQLite (dev)                  |
| **Deploy**   | Docker Compose                                      |

---

*Architecture version: 1.0 — September 2026*
*Calculation version: prototype-v1*
