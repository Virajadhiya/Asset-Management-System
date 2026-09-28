# PRAVI — Bridge Lifecycle & Management Platform

A unified RBAC-based lifecycle platform for bridge asset tracking, inspection, maintenance, condition assessment, GIS visualization, and historical audit.

**Inspired by** MoRTH's Indian Bridge Management System (IBMS) and Indian Railways' Bridge Management System — while extending the concept into an end-to-end lifecycle management platform.

> ⚠️ All data in this system is **synthetic/demo data**. We do not claim access to or use of actual government datasets.

---

## Quick Start (Docker)

```bash
# Start everything
docker compose up --build

# Seed demo data
docker exec pravi-backend python -m app.seed.seed_data

# Access
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Quick Start (Local Dev)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt

# Start PostgreSQL (with PostGIS) separately
# Set DATABASE_URL in .env

alembic upgrade head
python -m app.seed.seed_data
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Department Head | dept_head | dept123 |
| Executive Engineer | engineer | eng123 |
| Inspector | inspector | insp123 |
| Maintenance Officer | maint_off | maint123 |
| Viewer | viewer | view123 |

---

## Architecture

```
React + TypeScript (Vercel)
        ↓ REST API
FastAPI + SQLAlchemy (Render)
        ↓
PostgreSQL + PostGIS
```

### Key Features

- **Bridge Registry** — Identity, location, engineering characteristics
- **Lifecycle Management** — State-machine controlled status transitions
- **Inspection System** — Component-level condition ratings and defect tracking
- **Bridge Health Index** — Prototype weighted scoring (structural, functional, safety, age)
- **Maintenance Workflow** — Report → Approve → Start → Complete → Verify
- **GIS Visualization** — Leaflet map with condition-colored markers
- **RBAC** — 6 roles, 20 resource:action permissions
- **Audit Trail** — Complete change history with old/new values

---

## Research References

- [MoRTH IBMS (2016)](https://www.pib.gov.in/newsite/PrintRelease.aspx?lang=2&reg=48&relid=151406) — Bridge inventory, GPS location, engineering characteristics
- [MoRTH IBMS (2024)](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2003997&lang=2&reg=48) — Periodic inspection, structural health monitoring
- [IBMS Circular (2026)](https://www.scribd.com/document/1059989975/IBMS-circular-dated-25-06-2026-260626-123439) — Inventory, Condition Survey, Health Index, Priority Ranking modules
- [IAHE Training Material](https://iahe.morth.gov.in/sites/default/files/2025-08/Bridge%20Inspection%2C%20Repair%2C%20Rehabilitation%20and%20Maintenance%20Management.pdf) — Inspection types, condition surveys, maintenance management
- [Indian Railways BMS](https://www.pib.gov.in/PressReleasePage.aspx?PRID=1884162&lang=1&reg=3) — Bridge drawings, inspection details, photographs
- [CAG Report on Railway BMS](https://cag.gov.in/webroot/uploads/ae_circulars_office_orders/CircularsOfficeOrders-063b3bac2118774-91324685.pdf) — Bridge master data, inspection, maintenance

---

## License

Built for Smart India Hackathon / educational purposes.
