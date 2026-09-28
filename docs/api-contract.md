# PRAVI API Contract

This document defines the exact request/response shapes for all API endpoints.
Both backend and frontend must conform to this contract.

---

## Common Response Formats

### Paginated List Response

```json
{
  "items": [...],
  "total": 30,
  "page": 1,
  "limit": 20
}
```

### Error Response

```json
{
  "detail": "Error description"
}
```

---

## Authentication

### POST /api/auth/login

**Request:**

```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200):**

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "admin",
    "full_name": "System Administrator",
    "email": "admin@pravi.gov.in",
    "department": "IT",
    "role": "ADMIN",
    "permissions": [
      "bridge:read",
      "bridge:create",
      "bridge:update",
      "bridge:delete",
      "inspection:read",
      "..."
    ]
  }
}
```

**Errors:** 401 (invalid credentials)

---

## Bridges

### GET /api/bridges

**Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| status | string | Filter by current_status |
| condition | string | Filter by latest condition_category |
| district | string | Filter by district |
| bridge_type | string | Filter by bridge_type |
| search | string | Search bridge_code or bridge_name |
| page | int | Page number (default: 1) |
| limit | int | Items per page (default: 20) |

**Response (200):**

```json
{
  "items": [
    {
      "bridge_id": "uuid",
      "bridge_code": "BR-GJ-0001",
      "bridge_name": "Sabarmati Bridge",
      "bridge_type": "BEAM",
      "structure_category": "MAJOR",
      "current_status": "OPERATIONAL",
      "year_constructed": 2018,
      "district": "Ahmedabad",
      "state": "Gujarat",
      "latitude": 23.0300,
      "longitude": 72.5800,
      "latest_health_index": 92.0,
      "latest_condition_category": "EXCELLENT",
      "road_name": "NH-48"
    }
  ],
  "total": 30,
  "page": 1,
  "limit": 20
}
```

### POST /api/bridges

**Permission:** `bridge:create`

**Request:**

```json
{
  "bridge_code": "BR-GJ-0031",
  "bridge_name": "New Test Bridge",
  "bridge_type": "BEAM",
  "structure_category": "MINOR",
  "department": "PWD Gujarat",
  "owning_authority": "NHAI",
  "maintaining_authority": "PWD Gujarat",
  "road_name": "SH-12",
  "route_number": "SH-12",
  "year_constructed": 2024,
  "description": "New minor bridge",
  "location": {
    "state": "Gujarat",
    "district": "Ahmedabad",
    "taluka": "Daskroi",
    "latitude": 23.0500,
    "longitude": 72.6200
  },
  "engineering": {
    "total_length": 45.5,
    "carriageway_width": 7.5,
    "overall_width": 10.0,
    "number_of_lanes": 2,
    "number_of_spans": 3,
    "superstructure_type": "RCC T-Beam",
    "construction_material": "RCC",
    "design_loading": "IRC Class A",
    "design_life": 100
  }
}
```

**Response (201):** Full bridge object with location and engineering nested.

### GET /api/bridges/{id}

**Response (200):**

```json
{
  "bridge_id": "uuid",
  "bridge_code": "BR-GJ-0001",
  "bridge_name": "Sabarmati Bridge",
  "bridge_type": "BEAM",
  "structure_category": "MAJOR",
  "current_status": "OPERATIONAL",
  "department": "PWD Gujarat",
  "owning_authority": "NHAI",
  "maintaining_authority": "PWD Gujarat",
  "road_name": "NH-48",
  "route_number": "NH-48",
  "year_constructed": 2018,
  "date_commissioned": "2018-06-15",
  "traffic_status": "Normal",
  "daily_traffic_estimate": 25000,
  "load_restriction": null,
  "speed_restriction": null,
  "description": "Major bridge over Sabarmati River",
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-09-01T00:00:00Z",
  "location": {
    "state": "Gujarat",
    "district": "Ahmedabad",
    "taluka": "City",
    "village_or_city": "Ahmedabad",
    "latitude": 23.0300,
    "longitude": 72.5800,
    "elevation": 52.0,
    "chainage_start": 120.500,
    "chainage_end": 120.750
  },
  "engineering": {
    "total_length": 250.0,
    "carriageway_width": 12.0,
    "overall_width": 15.0,
    "number_of_lanes": 4,
    "number_of_spans": 8,
    "superstructure_type": "Pre-stressed Concrete",
    "substructure_type": "RCC Piers",
    "foundation_type": "Well Foundation",
    "construction_material": "Pre-stressed Concrete",
    "deck_material": "RCC",
    "design_loading": "IRC Class 70R",
    "design_speed": 80,
    "waterway": 180.0,
    "vertical_clearance": 6.5,
    "horizontal_clearance": null,
    "design_life": 100
  },
  "latest_condition": {
    "overall_health_index": 92.0,
    "condition_category": "EXCELLENT",
    "structural_score": 95.0,
    "functional_score": 90.0,
    "safety_score": 88.0,
    "assessment_date": "2026-08-12",
    "calculation_version": "prototype-v1"
  },
  "latest_inspection": {
    "inspection_id": "uuid",
    "inspection_type": "ROUTINE",
    "inspection_date": "2026-08-12",
    "overall_condition": "EXCELLENT",
    "next_inspection_date": "2027-08-12"
  },
  "active_maintenance": []
}
```

### PUT /api/bridges/{id}

**Permission:** `bridge:update`

> ⚠️ `current_status` field is **ignored** if sent. Status changes only through lifecycle API.

**Request:** Partial bridge fields (same shape as create, without location/engineering — those update separately or inline).

---

## Inspections

### GET /api/bridges/{id}/inspections

**Response (200):**

```json
{
  "items": [
    {
      "inspection_id": "uuid",
      "inspection_type": "ROUTINE",
      "inspection_date": "2026-08-12",
      "inspector_name": "Raj Patel",
      "overall_condition": "EXCELLENT",
      "inspection_status": "COMPLETED",
      "next_inspection_date": "2027-08-12",
      "findings": "Bridge in excellent condition",
      "created_at": "2026-08-12T10:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "limit": 20
}
```

### POST /api/bridges/{id}/inspections

**Permission:** `inspection:create`

**Request:**

```json
{
  "inspection_type": "ROUTINE",
  "inspection_date": "2026-09-28",
  "weather_condition": "Clear",
  "findings": "Minor wear on bearings",
  "recommendations": "Schedule bearing replacement within 6 months",
  "next_inspection_date": "2027-03-28",
  "components": [
    { "component_type": "DECK", "condition_rating": 4, "observations": "Good condition" },
    { "component_type": "SUPERSTRUCTURE", "condition_rating": 4, "observations": "Minor cracks" },
    { "component_type": "SUBSTRUCTURE", "condition_rating": 5, "observations": "Excellent" },
    { "component_type": "FOUNDATION", "condition_rating": 4, "observations": "Good" },
    { "component_type": "BEARINGS", "condition_rating": 2, "observations": "Significant wear" },
    { "component_type": "EXPANSION_JOINTS", "condition_rating": 3, "observations": "Fair" }
  ],
  "defects": [
    {
      "defect_type": "Bearing Corrosion",
      "severity": "HIGH",
      "component_type": "BEARINGS",
      "location_on_bridge": "Pier 3, Left bearing",
      "description": "Significant corrosion on steel bearing plate",
      "immediate_action_required": false
    }
  ]
}
```

**Response (201):** Full inspection with components, defects, and auto-generated condition_assessment.

**Side effects:**
- Creates condition_assessment with calculated BHI
- Creates lifecycle_event (INSPECTION_COMPLETED)
- Creates audit_log entry

### GET /api/inspections/{id}

**Response (200):** Full inspection detail with components array, defects array, and condition_assessment object.

---

## Maintenance

### GET /api/bridges/{id}/maintenance

**Response (200):** Paginated list of maintenance records.

### POST /api/bridges/{id}/maintenance

**Permission:** `maintenance:create`

**Request:**

```json
{
  "maintenance_type": "REPAIR",
  "issue_description": "Bearing replacement required on Pier 3",
  "priority": "HIGH",
  "estimated_cost": 250000.00
}
```

**Response (201):** Maintenance record with status "REPORTED".

### PUT /api/maintenance/{id}/status

**Request:**

```json
{
  "action": "approve",
  "remarks": "Approved for immediate repair"
}
```

**Valid actions:** `approve`, `start`, `complete`, `verify`

**Side effects:**
- `start` → creates lifecycle event (MAINTENANCE_STARTED), may change bridge status to UNDER_MAINTENANCE
- `complete` → creates lifecycle event (MAINTENANCE_COMPLETED), may change bridge status to OPERATIONAL
- All actions create audit_log entries

---

## Lifecycle

### GET /api/bridges/{id}/lifecycle

**Response (200):**

```json
{
  "items": [
    {
      "event_id": "uuid",
      "event_type": "COMMISSIONED",
      "event_date": "2018-06-15",
      "performed_by_name": "Admin User",
      "department": "PWD Gujarat",
      "description": "Bridge commissioned after construction",
      "previous_status": "UNDER_CONSTRUCTION",
      "new_status": "OPERATIONAL",
      "remarks": null,
      "created_at": "2018-06-15T00:00:00Z"
    }
  ],
  "total": 12
}
```

### POST /api/bridges/{id}/lifecycle

**Permission:** `lifecycle:create`

**Request:**

```json
{
  "event_type": "MAINTENANCE_STARTED",
  "event_date": "2026-09-28",
  "description": "Preventive maintenance started",
  "remarks": "Scheduled quarterly maintenance"
}
```

> Frontend sends event_type, event_date, description, remarks only.
> Backend calculates previous_status and new_status from state machine.
> Returns 400 if transition is invalid.

---

## Dashboard

### GET /api/dashboard/summary

**Response (200):**

```json
{
  "total_bridges": 30,
  "by_status": {
    "PLANNED": 5,
    "UNDER_CONSTRUCTION": 1,
    "OPERATIONAL": 18,
    "UNDER_MAINTENANCE": 3,
    "UNDER_REHABILITATION": 2,
    "CLOSED": 1,
    "DECOMMISSIONED": 0
  },
  "by_condition": {
    "EXCELLENT": 5,
    "GOOD": 10,
    "FAIR": 7,
    "POOR": 5,
    "CRITICAL": 3
  },
  "critical_bridges_count": 3,
  "overdue_inspections_count": 4,
  "recent_events": [
    {
      "event_id": "uuid",
      "bridge_code": "BR-GJ-0004",
      "bridge_name": "Aji River Bridge",
      "event_type": "MAINTENANCE_STARTED",
      "event_date": "2026-09-15",
      "description": "Repair work initiated"
    }
  ]
}
```

### GET /api/dashboard/priority-list

**Response (200):**

```json
{
  "items": [
    {
      "bridge_id": "uuid",
      "bridge_code": "BR-GJ-0005",
      "bridge_name": "Vishwamitri Bridge",
      "health_index": 32.0,
      "condition_category": "CRITICAL",
      "priority": "CRITICAL",
      "priority_score": 82.5,
      "reasons": [
        "Health Index below 40",
        "4 critical defects",
        "Inspection overdue by 8 months",
        "High traffic importance"
      ],
      "district": "Vadodara",
      "current_status": "OPERATIONAL"
    }
  ]
}
```

---

## GIS

### GET /api/gis/bridges

**Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| condition | string | Filter by condition_category |
| status | string | Filter by current_status |
| district | string | Filter by district |

**Response (200):**

```json
{
  "bridges": [
    {
      "bridge_id": "uuid",
      "bridge_code": "BR-GJ-0001",
      "bridge_name": "Sabarmati Bridge",
      "latitude": 23.0300,
      "longitude": 72.5800,
      "current_status": "OPERATIONAL",
      "condition_category": "EXCELLENT",
      "health_index": 92.0,
      "bridge_type": "BEAM",
      "district": "Ahmedabad",
      "year_constructed": 2018
    }
  ]
}
```

---

## Audit

### GET /api/audit/logs

**Permission:** `audit:read`

**Query Parameters:** entity_type, entity_id, user_id, page, limit

**Response (200):** Paginated list of audit log entries.
