# PRAVI — Research References

This document tracks the official government sources that ground our domain model.
Every field in our data model is either:
- **Government-referenced** — backed by official IBMS/BMS documentation
- **Our design** — clearly our own prototype extension
- **Derived/calculated** — computed from other data (e.g., Health Index)

---

## Primary Sources

### 1. MoRTH IBMS (2016 Launch)

**Source:** [Press Information Bureau — IBMS Launch](https://www.pib.gov.in/newsite/PrintRelease.aspx?lang=2&reg=48&relid=151406)

**What it establishes:**
- Unique bridge identification
- GPS-based location information (latitude/longitude)
- Engineering characteristics: design, materials, bridge type, age, loading, traffic lanes, length, carriageway width
- Bridge inventory concept
- Condition assessment concept

**Fields we derive from this:**
- bridge_code, bridge_name, bridge_type
- latitude, longitude
- total_length, carriageway_width, number_of_lanes, construction_material, design_loading, year_constructed

---

### 2. MoRTH IBMS (2024 Update)

**Source:** [Press Information Bureau — IBMS 2024](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2003997&lang=2&reg=48)

**What it establishes:**
- IBMS sanctioned for monitoring and maintenance across National Highway network
- Periodic visual/equipment-based inspection
- Real-time structural-health monitoring for important bridges
- Active government direction (not abandoned)

**Fields we derive from this:**
- inspection_type, inspection_date, inspection_status
- Concept of periodic vs. special inspection

---

### 3. MoRTH IBMS Circular (2026)

**Source:** [Scribd — IBMS Circular 2026](https://www.scribd.com/document/1059989975/IBMS-circular-dated-25-06-2026-260626-123439)

**What it establishes:**
- Inventory Module
- Condition Survey Module
- Health Index Module — overall structural and functional condition
- Priority Ranking Module — data-based prioritization for maintenance/repair/rehabilitation/reconstruction
- Mobile-based data collection
- Web dashboard for agencies/officers

**Fields we derive from this:**
- condition_assessments: structural_score, functional_score, overall_health_index, condition_category
- Priority ranking concept
- Dashboard concept

---

### 4. IAHE Training Material

**Source:** [IAHE — Bridge Inspection, Repair, Rehabilitation and Maintenance Management](https://iahe.morth.gov.in/sites/default/files/2025-08/Bridge%20Inspection%2C%20Repair%2C%20Rehabilitation%20and%20Maintenance%20Management.pdf)

**What it establishes:**
- Inspection types: Routine, Principal, Emergent, Underwater
- Bridge management process: Inventory → Inspection → Condition Survey → Condition Rating → Priority → Maintenance → Repair/Rehabilitation → Performance Evaluation
- Modern collection techniques: drones, LiDAR, mobile bridge inspection units
- Distress types, causes, condition surveys
- Component-level assessment

**Fields we derive from this:**
- InspectionType enum values
- ComponentType enum values
- Defect/distress concept
- Lifecycle workflow design

---

### 5. Indian Railways BMS

**Source:** [Press Information Bureau — Railways BMS](https://www.pib.gov.in/PressReleasePage.aspx?PRID=1884162&lang=1&reg=3)

**What it establishes:**
- Web application for bridge management
- Bridge drawings/design details
- Inspection details
- Photographs and videos for analysis of deterioration
- Load capacity analysis

**Fields we derive from this:**
- Documents/media concept
- Photograph/video association with inspections

---

### 6. CAG Report on Railway BMS

**Source:** [CAG — Railway BMS](https://cag.gov.in/webroot/uploads/ae_circulars_office_orders/CircularsOfficeOrders-063b3bac2118774-91324685.pdf)

**What it establishes:**
- Bridge master data
- Inspection/monitoring information
- Maintenance information
- Bridge type, category, location, ownership
- Maintaining authority
- Width, guard rails, protective screens
- Drawings and other bridge details

**Fields we derive from this:**
- owning_authority, maintaining_authority
- structure_category
- Administrative ownership concept

---

### 7. MoRTH Maintenance Philosophy

**Source:** [Press Information Bureau — Bridge Maintenance](https://www.pib.gov.in/PressReleasePage.aspx?PRID=1885355&lang=2&reg=48)

**What it establishes:**
- Periodic assessment of physical condition
- Repair, rehabilitation, or reconstruction decisions based on:
  - Nature and extent of distress
  - Functional requirements
  - Loading requirements

**Fields we derive from this:**
- MaintenanceType enum values
- Condition → maintenance decision workflow

---

## Our Design Decisions (Not Government-Sourced)

These are explicitly our prototype extensions:

| Feature | Rationale |
|---------|-----------|
| UUID primary keys | Standard database practice |
| RBAC with 6 roles | Prototype — not official government roles |
| JWT authentication | Standard web application auth |
| Lifecycle state machine | Our design for status transition control |
| Health Index formula (prototype-v1) | Inspired by IBMS concept, but our own weighted formula |
| Priority Score formula | Inspired by IBMS priority ranking, but our own calculation |
| Audit trail with JSONB | Our design for change tracking |
| Synthetic Gujarat data | Demo data for hackathon |
| Maintenance workflow states | Our design (REPORTED → APPROVED → IN_PROGRESS → COMPLETED → VERIFIED) |
| calculation_version tracking | Our design for formula versioning |
