import os
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.models.user import Role, Permission, RolePermission, User
from app.models.bridge import Bridge, BridgeLocation, BridgeEngineering
from app.models.inspection import Inspection, InspectionComponent, Defect
from app.models.condition import ConditionAssessment
from app.models.lifecycle import LifecycleEvent
from app.models.maintenance import MaintenanceRecord
from app.services.auth_service import hash_password
from app.services.health_index import calculate_health_index
import uuid

# Use sync engine
raw_url = os.getenv("SYNC_DATABASE_URL") or os.getenv("DATABASE_URL", "sqlite:///./pravi.db")
db_url = raw_url.replace("+asyncpg", "").replace("+aiosqlite", "")
if db_url.startswith("postgresql://") and not os.getenv("DATABASE_URL"):
    db_url = "sqlite:///./pravi.db"
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ──────────────────────────────────────────
# Permission matrix from implementation plan
# ──────────────────────────────────────────
ALL_PERMISSIONS = [
    "bridge:read", "bridge:create", "bridge:update", "bridge:delete",
    "inspection:read", "inspection:create", "inspection:update",
    "defect:create", "defect:update",
    "condition:read", "condition:create",
    "maintenance:read", "maintenance:create", "maintenance:update", "maintenance:approve",
    "lifecycle:read", "lifecycle:create",
    "audit:read",
    "user:read", "user:manage",
]

ROLE_PERMISSIONS = {
    "ADMIN": ALL_PERMISSIONS,
    "DEPARTMENT_HEAD": [
        "bridge:read", "bridge:create", "bridge:update",
        "inspection:read", "inspection:create", "inspection:update",
        "defect:create", "defect:update",
        "condition:read", "condition:create",
        "maintenance:read", "maintenance:create", "maintenance:update", "maintenance:approve",
        "lifecycle:read", "lifecycle:create",
        "audit:read", "user:read",
    ],
    "EXECUTIVE_ENGINEER": [
        "bridge:read", "bridge:create", "bridge:update",
        "inspection:read", "inspection:create", "inspection:update",
        "defect:create", "defect:update",
        "condition:read", "condition:create",
        "maintenance:read", "maintenance:create", "maintenance:update", "maintenance:approve",
        "lifecycle:read", "lifecycle:create",
    ],
    "INSPECTOR": [
        "bridge:read",
        "inspection:read", "inspection:create", "inspection:update",
        "defect:create", "defect:update",
        "condition:read", "condition:create",
        "maintenance:read",
        "lifecycle:read",
    ],
    "MAINTENANCE_OFFICER": [
        "bridge:read",
        "inspection:read",
        "condition:read",
        "maintenance:read", "maintenance:create", "maintenance:update",
        "lifecycle:read",
    ],
    "VIEWER": [
        "bridge:read",
        "inspection:read",
        "condition:read",
        "maintenance:read",
        "lifecycle:read",
    ],
}

# ──────────────────────────────────────────
# 30 intentional bridge scenarios
# ──────────────────────────────────────────
BRIDGES = [
    # (code, name, district, status, type, category, lat, lng, year, road, route, dept, traffic)
    ("BR-GJ-0001", "Sabarmati Bridge", "Ahmedabad", "OPERATIONAL", "BEAM", "MAJOR", 23.0300, 72.5800, 2018, "NH-48", "NH-48", "NHAI", 25000),
    ("BR-GJ-0002", "Tapi Crossing", "Surat", "OPERATIONAL", "BOX_GIRDER", "MAJOR", 21.1702, 72.8311, 2015, "NH-48", "NH-48", "PWD Gujarat", 22000),
    ("BR-GJ-0003", "Narmada Minor Bridge", "Bharuch", "OPERATIONAL", "SLAB", "MINOR", 21.7051, 72.9959, 2010, "SH-6", "SH-6", "PWD Gujarat", 8000),
    ("BR-GJ-0004", "Aji River Bridge", "Rajkot", "UNDER_MAINTENANCE", "TRUSS", "MAJOR", 22.3039, 70.8022, 1985, "NH-27", "NH-27", "NHAI", 18000),
    ("BR-GJ-0005", "Vishwamitri Bridge", "Vadodara", "OPERATIONAL", "BEAM", "MAJOR", 22.3072, 73.1812, 1962, "NH-48", "NH-48", "NHAI", 30000),
    ("BR-GJ-0006", "Banas Bridge", "Banaskantha", "OPERATIONAL", "ARCH", "MAJOR", 24.1700, 72.4400, 2000, "NH-14", "NH-14", "PWD Gujarat", 12000),
    ("BR-GJ-0007", "Shetrunji Culvert", "Bhavnagar", "UNDER_REHABILITATION", "SLAB", "CULVERT", 21.7700, 71.8300, 1975, "SH-31", "SH-31", "PWD Gujarat", 5000),
    ("BR-GJ-0008", "Mahi Bridge", "Panchmahal", "PLANNED", "CABLE_STAYED", "EXTRA_LONG", 22.7500, 73.6000, None, "NH-56", "NH-56", "NHAI", None),
    ("BR-GJ-0009", "Damanganga Bridge", "Valsad", "UNDER_CONSTRUCTION", "BOX_GIRDER", "MAJOR", 20.6100, 72.9300, None, "NH-48", "NH-48", "NHAI", None),
    ("BR-GJ-0010", "Rukmavati Bridge", "Devbhumi Dwarka", "CLOSED", "BEAM", "MAJOR", 22.2400, 68.9700, 1958, "SH-57", "SH-57", "PWD Gujarat", 3000),
    # 11-20: Various Gujarat bridges with mixed conditions
    ("BR-GJ-0011", "Meshwo Bridge", "Mehsana", "OPERATIONAL", "BEAM", "MINOR", 23.5900, 72.3800, 2012, "SH-7", "SH-7", "PWD Gujarat", 9000),
    ("BR-GJ-0012", "Bhader Bridge", "Amreli", "OPERATIONAL", "SLAB", "MINOR", 21.6000, 71.2200, 2008, "SH-28", "SH-28", "PWD Gujarat", 6000),
    ("BR-GJ-0013", "Ozat River Bridge", "Junagadh", "OPERATIONAL", "TRUSS", "MAJOR", 21.5200, 70.4600, 1990, "NH-8D", "NH-8D", "NHAI", 15000),
    ("BR-GJ-0014", "Khari Bridge", "Ahmedabad", "OPERATIONAL", "BEAM", "MINOR", 22.9800, 72.6300, 2020, "SH-17", "SH-17", "AMC", 20000),
    ("BR-GJ-0015", "Vatrak Bridge", "Anand", "OPERATIONAL", "SLAB", "MINOR", 22.5600, 73.0100, 2005, "SH-3", "SH-3", "PWD Gujarat", 7000),
    ("BR-GJ-0016", "Purna Bridge", "Navsari", "UNDER_MAINTENANCE", "BEAM", "MAJOR", 20.9500, 72.9200, 1988, "NH-48", "NH-48", "NHAI", 16000),
    ("BR-GJ-0017", "Auranga Bridge", "Valsad", "OPERATIONAL", "ARCH", "MINOR", 20.5300, 73.0500, 2016, "SH-60", "SH-60", "PWD Gujarat", 5500),
    ("BR-GJ-0018", "Machhu Bridge", "Morbi", "OPERATIONAL", "BEAM", "MAJOR", 22.8200, 70.8400, 1995, "SH-25", "SH-25", "PWD Gujarat", 14000),
    ("BR-GJ-0019", "Dhadhar Bridge", "Vadodara", "UNDER_MAINTENANCE", "SLAB", "MINOR", 22.2800, 73.2500, 1998, "SH-11", "SH-11", "PWD Gujarat", 8500),
    ("BR-GJ-0020", "Bhadar Bridge", "Jamnagar", "OPERATIONAL", "TRUSS", "MAJOR", 22.4700, 70.0700, 1982, "NH-27", "NH-27", "NHAI", 11000),
    # 21-30: More variety
    ("BR-GJ-0021", "Tapti Railway Overbridge", "Surat", "OPERATIONAL", "BOX_GIRDER", "MAJOR", 21.2050, 72.8400, 2019, "NH-53", "NH-53", "NHAI", 28000),
    ("BR-GJ-0022", "Ambika Bridge", "Navsari", "OPERATIONAL", "BEAM", "MINOR", 20.8800, 72.9000, 2013, "SH-63", "SH-63", "PWD Gujarat", 4500),
    ("BR-GJ-0023", "Und Bridge", "Junagadh", "PLANNED", "BEAM", "MINOR", 21.4800, 70.5500, None, "SH-35", "SH-35", "PWD Gujarat", None),
    ("BR-GJ-0024", "Kim Bridge", "Surat", "PLANNED", "SLAB", "MINOR", 21.3500, 72.9600, None, "SH-6", "SH-6", "PWD Gujarat", None),
    ("BR-GJ-0025", "Heran Bridge", "Chhota Udepur", "OPERATIONAL", "ARCH", "MINOR", 22.3100, 74.0100, 2007, "SH-5", "SH-5", "PWD Gujarat", 3500),
    ("BR-GJ-0026", "Ghelo Bridge", "Bhavnagar", "OPERATIONAL", "SLAB", "CULVERT", 21.8000, 72.1500, 2011, "SH-31", "SH-31", "PWD Gujarat", 4000),
    ("BR-GJ-0027", "Sukhbhadar Bridge", "Rajkot", "PLANNED", "BEAM", "MAJOR", 22.2700, 70.7500, None, "NH-27", "NH-27", "NHAI", None),
    ("BR-GJ-0028", "Damanganga Culvert", "Dang", "OPERATIONAL", "SLAB", "CULVERT", 20.7500, 73.7500, 2014, "SH-56", "SH-56", "PWD Gujarat", 2000),
    ("BR-GJ-0029", "Karjan Bridge", "Vadodara", "PLANNED", "BOX_GIRDER", "MAJOR", 22.0500, 73.1200, None, "NH-48", "NH-48", "NHAI", None),
    ("BR-GJ-0030", "Sabarmati Riverfront Bridge", "Ahmedabad", "UNDER_CONSTRUCTION", "SUSPENSION", "EXTRA_LONG", 23.0500, 72.5600, None, "Ring Road", "RR-1", "AMC", None),
]

# Intentional condition scenarios
BRIDGE_CONDITIONS = {
    "BR-GJ-0001": (92, "EXCELLENT"),   # Flagship, recently inspected
    "BR-GJ-0002": (78, "GOOD"),        # Routine maintenance completed
    "BR-GJ-0003": (62, "FAIR"),        # Inspection due, bearing wear
    "BR-GJ-0004": (45, "POOR"),        # Active repair, 3 critical defects
    "BR-GJ-0005": (32, "CRITICAL"),    # Worst condition, urgent rehab needed
    "BR-GJ-0006": (75, "GOOD"),        # Recently rehabilitated
    "BR-GJ-0007": (38, "CRITICAL"),    # Major rehab in progress
    "BR-GJ-0010": (28, "CRITICAL"),    # Closed for safety
    "BR-GJ-0011": (88, "EXCELLENT"),
    "BR-GJ-0012": (72, "GOOD"),
    "BR-GJ-0013": (58, "FAIR"),
    "BR-GJ-0014": (91, "EXCELLENT"),
    "BR-GJ-0015": (65, "FAIR"),
    "BR-GJ-0016": (42, "POOR"),
    "BR-GJ-0017": (82, "GOOD"),
    "BR-GJ-0018": (55, "FAIR"),
    "BR-GJ-0019": (48, "POOR"),
    "BR-GJ-0020": (52, "FAIR"),
    "BR-GJ-0021": (85, "EXCELLENT"),
    "BR-GJ-0022": (77, "GOOD"),
    "BR-GJ-0025": (70, "GOOD"),
    "BR-GJ-0026": (80, "GOOD"),
    "BR-GJ-0028": (73, "GOOD"),
}

COMPONENT_TYPES = ["DECK", "SUPERSTRUCTURE", "SUBSTRUCTURE", "FOUNDATION", "BEARINGS", "EXPANSION_JOINTS"]
SAFETY_COMPONENTS = ["SAFETY_BARRIERS", "DRAINAGE", "APPROACHES"]


def rating_from_health(health_score):
    """Generate component ratings that roughly produce the target health score."""
    base = max(1, min(5, round(health_score / 20)))
    return max(1, min(5, base + random.choice([-1, 0, 0, 0, 1])))


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # ── 1. Permissions ──
        perms = {}
        for p_name in ALL_PERMISSIONS:
            perm = db.query(Permission).filter_by(name=p_name).first()
            if not perm:
                perm = Permission(name=p_name)
                db.add(perm)
                db.flush()
            perms[p_name] = perm

        # ── 2. Roles + Role Permissions ──
        roles = {}
        for r_name, r_perms in ROLE_PERMISSIONS.items():
            role = db.query(Role).filter_by(name=r_name).first()
            if not role:
                role = Role(name=r_name, description=f"{r_name.replace('_', ' ').title()}")
                db.add(role)
                db.flush()
                for p_name in r_perms:
                    if p_name in perms:
                        rp = RolePermission(role_id=role.id, permission_id=perms[p_name].id)
                        db.add(rp)
            roles[r_name] = role

        # ── 3. Demo Users ──
        users_data = [
            ("admin", "admin123", "System Administrator", "admin@pravi.gov.in", "IT", "ADMIN"),
            ("dept_head", "dept123", "Rajesh Kumar", "rajesh.kumar@pravi.gov.in", "PWD Gujarat", "DEPARTMENT_HEAD"),
            ("engineer", "eng123", "Priya Sharma", "priya.sharma@pravi.gov.in", "NHAI", "EXECUTIVE_ENGINEER"),
            ("inspector", "insp123", "Raj Patel", "raj.patel@pravi.gov.in", "PWD Gujarat", "INSPECTOR"),
            ("maint_off", "maint123", "Amit Shah", "amit.shah@pravi.gov.in", "PWD Gujarat", "MAINTENANCE_OFFICER"),
            ("viewer", "view123", "Guest Viewer", "viewer@pravi.gov.in", "Public", "VIEWER"),
        ]
        users = {}
        for u_name, u_pass, u_full, u_email, u_dept, u_role in users_data:
            user = db.query(User).filter_by(username=u_name).first()
            if not user:
                user = User(
                    username=u_name,
                    hashed_password=hash_password(u_pass),
                    full_name=u_full,
                    email=u_email,
                    department=u_dept,
                    role_id=roles[u_role].id,
                )
                db.add(user)
                db.flush()
            users[u_name] = user

        inspector_user = users["inspector"]
        engineer_user = users["engineer"]

        # ── 4. Bridges ──
        bridge_objs = {}
        for (code, name, district, status, btype, cat, lat, lng, year, road, route, dept, traffic) in BRIDGES:
            bridge = db.query(Bridge).filter_by(bridge_id_str=code).first()
            if not bridge:
                bridge = Bridge(
                    bridge_id_str=code,
                    name=name,
                    bridge_type=btype,
                    structure_category=cat,
                    current_status=status,
                    department=dept,
                    owning_authority=dept,
                    maintaining_authority="PWD Gujarat",
                    traffic_status="Normal" if traffic else None,
                    daily_traffic_estimate=traffic,
                )
                db.add(bridge)
                db.flush()

                loc = BridgeLocation(
                    bridge_id=bridge.id,
                    latitude=lat,
                    longitude=lng,
                    district=district,
                    state="Gujarat",
                    road_name=road,
                )
                db.add(loc)

                eng = BridgeEngineering(
                    bridge_id=bridge.id,
                    total_length=random.uniform(20, 500) if cat != "CULVERT" else random.uniform(5, 20),
                    number_of_spans=random.randint(1, 12),
                    deck_width=random.choice([7.5, 10.0, 12.0, 14.0]),
                    design_life=100,
                    year_built=year,
                )
                db.add(eng)
                db.flush()

            bridge_objs[code] = bridge

        # ── 5. Inspections + Components + Defects + Condition Assessments ──
        for code, cond_data in BRIDGE_CONDITIONS.items():
            bridge = bridge_objs.get(code)
            if not bridge:
                continue
            target_score, target_cat = cond_data

            # Create 3-8 historical inspections
            num_inspections = random.randint(3, 8)
            base_date = datetime(2020, 1, 1)

            for i in range(num_inspections):
                insp_date = base_date + timedelta(days=i * random.randint(120, 365))
                is_latest = (i == num_inspections - 1)

                inspection = Inspection(
                    bridge_id=bridge.id,
                    inspector_id=inspector_user.id,
                    inspection_type=random.choice(["ROUTINE", "PRINCIPAL", "ROUTINE", "ROUTINE"]),
                    status="COMPLETED",
                    scheduled_date=insp_date,
                    completion_date=insp_date,
                )
                db.add(inspection)
                db.flush()

                # Component ratings
                components = []
                for comp_type in COMPONENT_TYPES + SAFETY_COMPONENTS:
                    if is_latest:
                        rating = rating_from_health(target_score)
                    else:
                        rating = random.randint(2, 5)
                    comp = InspectionComponent(
                        inspection_id=inspection.id,
                        component_type=comp_type,
                        condition_rating=rating,
                        notes=f"Condition assessment for {comp_type.lower().replace('_', ' ')}",
                    )
                    db.add(comp)
                    components.append(comp)

                db.flush()

                # Defects for POOR/CRITICAL bridges on latest inspection
                if is_latest and target_score < 55:
                    num_defects = random.randint(2, 5)
                    defect_types = ["Cracking", "Corrosion", "Spalling", "Delamination", "Scour", "Settlement", "Bearing Failure"]
                    for _ in range(num_defects):
                        defect = Defect(
                            inspection_id=inspection.id,
                            severity=random.choice(["HIGH", "CRITICAL"]) if target_score < 40 else random.choice(["MEDIUM", "HIGH"]),
                            description=f"{random.choice(defect_types)} observed",
                        )
                        db.add(defect)

                # Condition assessment for latest inspection
                if is_latest:
                    condition = ConditionAssessment(
                        bridge_id=bridge.id,
                        inspection_id=inspection.id,
                        health_index_score=target_score,
                        condition_category=target_cat,
                        calculation_version="prototype-v1",
                    )
                    db.add(condition)

        # ── 6. Lifecycle Events ──
        for code, (_, _, district, status, _, _, _, _, year, *_) in [
            (b[0], b) for b in BRIDGES
        ]:
            bridge = bridge_objs.get(code)
            if not bridge:
                continue

            events = []
            if year:
                events.append(("PROPOSED", datetime(year - 2, 1, 15), "Bridge proposed"))
                events.append(("APPROVED", datetime(year - 1, 6, 1), "Project approved"))
                events.append(("CONSTRUCTION_STARTED", datetime(year - 1, 9, 1), "Construction commenced"))
                events.append(("COMMISSIONED", datetime(year, 6, 15), "Bridge commissioned and opened to traffic"))
            elif status == "PLANNED":
                events.append(("PROPOSED", datetime(2025, 6, 1), "Bridge proposed for construction"))
            elif status == "UNDER_CONSTRUCTION":
                events.append(("PROPOSED", datetime(2024, 1, 1), "Bridge proposed"))
                events.append(("APPROVED", datetime(2024, 6, 1), "Project approved"))
                events.append(("CONSTRUCTION_STARTED", datetime(2025, 3, 1), "Construction commenced"))

            if status == "UNDER_MAINTENANCE" and year:
                events.append(("MAINTENANCE_STARTED", datetime(2026, 8, 1), "Maintenance work initiated"))
            if status == "UNDER_REHABILITATION" and year:
                events.append(("REHABILITATION_STARTED", datetime(2026, 7, 1), "Major rehabilitation started"))
            if status == "CLOSED" and year:
                events.append(("CLOSED", datetime(2026, 3, 1), "Bridge closed for safety reasons"))

            for evt_type, evt_date, evt_desc in events:
                event = LifecycleEvent(
                    bridge_id=bridge.id,
                    event_type=evt_type,
                    event_date=evt_date,
                    description=evt_desc,
                    recorded_by=engineer_user.id,
                )
                db.add(event)

        # ── 7. Maintenance Records ──
        # POOR/CRITICAL bridges get maintenance records
        for code in ["BR-GJ-0004", "BR-GJ-0005", "BR-GJ-0016", "BR-GJ-0019"]:
            bridge = bridge_objs.get(code)
            if not bridge:
                continue
            maint = MaintenanceRecord(
                bridge_id=bridge.id,
                maintenance_type="REPAIR",
                priority="HIGH" if code != "BR-GJ-0005" else "CRITICAL",
                status="IN_PROGRESS" if bridge.current_status == "UNDER_MAINTENANCE" else "REPORTED",
                description=f"Repair work for {bridge.name}",
                estimated_cost=random.uniform(500000, 5000000),
            )
            db.add(maint)

        for code in ["BR-GJ-0007"]:
            bridge = bridge_objs.get(code)
            if not bridge:
                continue
            maint = MaintenanceRecord(
                bridge_id=bridge.id,
                maintenance_type="REHABILITATION",
                priority="CRITICAL",
                status="IN_PROGRESS",
                description=f"Major rehabilitation for {bridge.name}",
                estimated_cost=random.uniform(10000000, 50000000),
                start_date=datetime(2026, 7, 15),
            )
            db.add(maint)

        # Completed maintenance for recently rehabilitated bridge
        bridge_006 = bridge_objs.get("BR-GJ-0006")
        if bridge_006:
            maint = MaintenanceRecord(
                bridge_id=bridge_006.id,
                maintenance_type="REHABILITATION",
                priority="HIGH",
                status="VERIFIED",
                description="Full rehabilitation completed",
                estimated_cost=15000000,
                actual_cost=14200000,
                start_date=datetime(2024, 1, 1),
                completion_date=datetime(2025, 6, 1),
            )
            db.add(maint)

        db.commit()
        print("[SUCCESS] Database seeded successfully!")
        print(f"   - {len(ALL_PERMISSIONS)} permissions")
        print(f"   - {len(ROLE_PERMISSIONS)} roles")
        print(f"   - {len(users_data)} demo users")
        print(f"   - {len(BRIDGES)} bridges")
        print(f"   - {len(BRIDGE_CONDITIONS)} bridges with condition data")
        print("   - Inspections, components, defects, lifecycle events, maintenance records")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error seeding database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
