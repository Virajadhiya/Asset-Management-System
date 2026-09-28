import os
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.models.bridge import Bridge, BridgeLocation, BridgeEngineering
from app.models.inspection import Inspection, InspectionComponent, Defect
from app.models.condition import ConditionAssessment
from app.models.lifecycle import LifecycleEvent
from app.models.maintenance import MaintenanceRecord
from app.models.user import User

# Use sync engine
raw_url = os.getenv("SYNC_DATABASE_URL") or os.getenv("DATABASE_URL", "sqlite:///./pravi.db")
db_url = raw_url.replace("+asyncpg", "").replace("+aiosqlite", "")
if db_url.startswith("postgresql://") and not os.getenv("DATABASE_URL"):
    db_url = "sqlite:///./pravi.db"
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

MULTI_ASSETS = [
    # ── TUNNELS ────────────────────────────────────────────────────────
    {
        "asset_type": "TUNNEL",
        "code": "TN-GJ-0001",
        "name": "Okha Subsea Underpass Tunnel",
        "bridge_type": "OTHER",
        "structure_category": "MAJOR",
        "status": "OPERATIONAL",
        "department": "Gujarat Maritime Board & Roads",
        "district": "Devbhumi Dwarka",
        "road": "Dwarka-Bet Okha Coastal Link",
        "lat": 22.4635,
        "lng": 69.0722,
        "traffic": 8500,
        "eng": {
            "total_length": 1850.0,
            "number_of_spans": 1,
            "deck_width": 12.5,
            "design_life": 120,
            "year_built": 2021,
            "tunnel_type": "TBM (Slurry Shield)",
            "bore_diameter": 12.5,
            "ventilation_system": "Transverse Jet Fan Battery",
            "number_of_lanes": 2,
        },
        "condition": {"health": 88.5, "cat": "EXCELLENT", "struct": 90.0, "func": 88.0, "safe": 87.0},
        "components": [
            ("TUNNEL_LINING", 5, "Precast segmental lining intact with hydrophobic coating"),
            ("TUNNEL_VENTILATION", 4, "Jet fan array operating at 98% nominal thrust"),
            ("TUNNEL_LIGHTING", 5, "Dual circuit LED luminaire system fully functional"),
            ("TUNNEL_FIRE_SAFETY", 5, "Automated deluge foam suppression test passed"),
        ],
        "events": ["PROPOSED", "DESIGNED", "CONSTRUCTION_STARTED", "CONSTRUCTION_COMPLETED", "COMMISSIONED"]
    },
    {
        "asset_type": "TUNNEL",
        "code": "TN-GJ-0002",
        "name": "Ahmedabad Metro Underground Rail Tunnel",
        "bridge_type": "OTHER",
        "structure_category": "MAJOR",
        "status": "OPERATIONAL",
        "department": "Gujarat Metro Rail Corporation (GMRC)",
        "district": "Ahmedabad",
        "road": "Kalupur - Shahpur Corridor",
        "lat": 23.0298,
        "lng": 72.5975,
        "traffic": 45000,
        "eng": {
            "total_length": 3200.0,
            "number_of_spans": 2,
            "deck_width": 6.6,
            "design_life": 100,
            "year_built": 2022,
            "tunnel_type": "Twin EPB-TBM",
            "bore_diameter": 6.6,
            "ventilation_system": "Tunnel Ventilation Dampers (TVS)",
            "number_of_lanes": 2,
        },
        "condition": {"health": 92.0, "cat": "EXCELLENT", "struct": 94.0, "func": 91.0, "safe": 91.0},
        "components": [
            ("TUNNEL_LINING", 5, "Zero water ingress detected across all 2,400 ring segments"),
            ("TUNNEL_CROWN", 5, "Crown convergence monitoring within +/- 1.2mm tolerance"),
            ("TUNNEL_DRAINAGE", 4, "Invert sump pumps clear and debris free"),
        ],
        "events": ["PROPOSED", "APPROVED", "CONSTRUCTION_STARTED", "COMMISSIONED"]
    },
    {
        "asset_type": "TUNNEL",
        "code": "TN-GJ-0003",
        "name": "Narmada Riverbed Hydro Utility Tunnel",
        "bridge_type": "OTHER",
        "structure_category": "MAJOR",
        "status": "UNDER_MAINTENANCE",
        "department": "Sardar Sarovar Narmada Nigam",
        "district": "Narmada",
        "road": "Kevadia Dam Access Subterranean",
        "lat": 21.8315,
        "lng": 73.7485,
        "traffic": 3200,
        "eng": {
            "total_length": 950.0,
            "number_of_spans": 1,
            "deck_width": 8.0,
            "design_life": 80,
            "year_built": 2005,
            "tunnel_type": "Drill & Blast",
            "bore_diameter": 8.0,
            "ventilation_system": "Forced Axial Exhaust",
            "number_of_lanes": 2,
        },
        "condition": {"health": 62.4, "cat": "FAIR", "struct": 60.0, "func": 65.0, "safe": 62.0},
        "components": [
            ("TUNNEL_LINING", 3, "Localized micro-cracking and dampness along invert seepage joints"),
            ("TUNNEL_VENTILATION", 3, "Motor bearing vibration detected in exhaust unit #2"),
            ("TUNNEL_FIRE_SAFETY", 4, "Emergency call points tested and verified"),
        ],
        "events": ["COMMISSIONED", "INSPECTION_COMPLETED", "MAINTENANCE_STARTED"]
    },
    {
        "asset_type": "TUNNEL",
        "code": "TN-GJ-0004",
        "name": "Pavagadh Hill Grade Separator Tunnel",
        "bridge_type": "OTHER",
        "structure_category": "MINOR",
        "status": "OPERATIONAL",
        "department": "Gujarat State Road Dev Corp",
        "district": "Panchmahal",
        "road": "Halol - Pavagadh Highway SH-150",
        "lat": 22.4611,
        "lng": 73.5312,
        "traffic": 14200,
        "eng": {
            "total_length": 680.0,
            "number_of_spans": 1,
            "deck_width": 10.5,
            "design_life": 100,
            "year_built": 2018,
            "tunnel_type": "Cut & Cover",
            "bore_diameter": 10.5,
            "ventilation_system": "Natural Longitudinal Draft",
            "number_of_lanes": 2,
        },
        "condition": {"health": 74.8, "cat": "GOOD", "struct": 76.0, "func": 75.0, "safe": 73.0},
        "components": [
            ("TUNNEL_LINING", 4, "Shotcrete membrane stable; slight efflorescence on north portal"),
            ("TUNNEL_LIGHTING", 4, "Portal daylight transition fixtures operating normally"),
        ],
        "events": ["COMMISSIONED", "INSPECTION_COMPLETED"]
    },
    {
        "asset_type": "TUNNEL",
        "code": "TN-GJ-0005",
        "name": "Dahej Petrochemical Corridor Sub-Tunnel",
        "bridge_type": "OTHER",
        "structure_category": "MAJOR",
        "status": "UNDER_REHABILITATION",
        "department": "GIDC Engineering",
        "district": "Bharuch",
        "road": "Dahej PCPIR Dedicated Access",
        "lat": 21.7125,
        "lng": 72.5855,
        "traffic": 6800,
        "eng": {
            "total_length": 1400.0,
            "number_of_spans": 1,
            "deck_width": 9.2,
            "design_life": 75,
            "year_built": 1998,
            "tunnel_type": "Box Jacking & Immersed Tube",
            "bore_diameter": 9.2,
            "ventilation_system": "Chemical Vapor Extraction",
            "number_of_lanes": 2,
        },
        "condition": {"health": 38.2, "cat": "POOR", "struct": 35.0, "func": 40.0, "safe": 39.0},
        "components": [
            ("TUNNEL_LINING", 2, "Severe saline moisture corrosion and chemical pitting on crown rebar"),
            ("TUNNEL_VENTILATION", 2, "Extraction ducts degraded; emergency bypass activated"),
            ("TUNNEL_FIRE_SAFETY", 3, "Sprinkler piping pressure loss identified"),
        ],
        "events": ["COMMISSIONED", "INSPECTION_COMPLETED", "REHABILITATION_STARTED"]
    },

    # ── HIGHWAYS & EXPRESSWAYS ─────────────────────────────────────────
    {
        "asset_type": "HIGHWAY",
        "code": "HW-GJ-0001",
        "name": "NE-1 Ahmedabad-Vadodara National Expressway",
        "bridge_type": "OTHER",
        "structure_category": "EXTRA_LONG",
        "status": "OPERATIONAL",
        "department": "National Highways Authority of India (NHAI)",
        "district": "Ahmedabad",
        "road": "National Expressway 1",
        "lat": 22.8125,
        "lng": 72.8450,
        "traffic": 62000,
        "eng": {
            "total_length": 93100.0,
            "number_of_spans": 0,
            "deck_width": 24.0,
            "carriageway_width": 24.0,
            "design_life": 30,
            "year_built": 2004,
            "pavement_type": "Asphalt Concrete (Dense Bituminous)",
            "number_of_lanes": 4,
        },
        "condition": {"health": 91.0, "cat": "EXCELLENT", "struct": 92.0, "func": 90.0, "safe": 91.0},
        "components": [
            ("PAVEMENT_SURFACE", 5, "Friction coefficient 0.65; minimal ravelling detected"),
            ("ROAD_BASE", 5, "FWD deflection testing shows sound subgrade resilience"),
            ("SHOULDERS", 4, "Paved shoulders clean with edge rumble strips intact"),
            ("ROAD_MARKINGS", 5, "Thermoplastic retroreflective paint compliant with IRC:35"),
        ],
        "events": ["COMMISSIONED", "INSPECTION_COMPLETED"]
    },
    {
        "asset_type": "HIGHWAY",
        "code": "HW-GJ-0002",
        "name": "NH-48 Surat-Navsari Golden Quadrilateral",
        "bridge_type": "OTHER",
        "structure_category": "EXTRA_LONG",
        "status": "OPERATIONAL",
        "department": "Ministry of Road Transport & Highways",
        "district": "Surat",
        "road": "NH-48 Golden Quadrilateral",
        "lat": 21.0540,
        "lng": 72.9320,
        "traffic": 78000,
        "eng": {
            "total_length": 42500.0,
            "number_of_spans": 0,
            "deck_width": 32.0,
            "carriageway_width": 32.0,
            "design_life": 40,
            "year_built": 2014,
            "pavement_type": "Rigid Pavement (Pavement Quality Concrete PQC)",
            "number_of_lanes": 6,
        },
        "condition": {"health": 84.5, "cat": "GOOD", "struct": 86.0, "func": 83.0, "safe": 84.0},
        "components": [
            ("PAVEMENT_SURFACE", 4, "Transverse expansion joints well-sealed; minor corner chipping"),
            ("ROAD_DRAINAGE", 4, "Concrete trapezoidal side drains flowing unobstructed"),
            ("ROAD_BARRIERS", 5, "W-beam crash barriers fully tensioned throughout corridor"),
        ],
        "events": ["COMMISSIONED", "INSPECTION_COMPLETED"]
    },
    {
        "asset_type": "HIGHWAY",
        "code": "HW-GJ-0003",
        "name": "Sarkhej-Gandhinagar (SG) Highway Corridor",
        "bridge_type": "OTHER",
        "structure_category": "MAJOR",
        "status": "OPERATIONAL",
        "department": "Gujarat Roads & Buildings Dept",
        "district": "Gandhinagar",
        "road": "SH-141 / SG Highway",
        "lat": 23.1150,
        "lng": 72.5350,
        "traffic": 85000,
        "eng": {
            "total_length": 28000.0,
            "number_of_spans": 0,
            "deck_width": 30.0,
            "carriageway_width": 30.0,
            "design_life": 25,
            "year_built": 2019,
            "pavement_type": "Stone Matrix Asphalt (SMA)",
            "number_of_lanes": 6,
        },
        "condition": {"health": 78.0, "cat": "GOOD", "struct": 79.0, "func": 77.0, "safe": 78.0},
        "components": [
            ("PAVEMENT_SURFACE", 4, "High skid resistance; light rutting in slow-traffic lanes"),
            ("ROAD_MARKINGS", 4, "Pedestrian crossings and lane dividers repainted Q1 2026"),
        ],
        "events": ["COMMISSIONED", "INSPECTION_COMPLETED"]
    },
    {
        "asset_type": "HIGHWAY",
        "code": "HW-GJ-0004",
        "name": "NH-27 Rajkot-Porbandar Coastal Highway",
        "bridge_type": "OTHER",
        "structure_category": "EXTRA_LONG",
        "status": "UNDER_MAINTENANCE",
        "department": "National Highways Authority of India",
        "district": "Porbandar",
        "road": "National Highway 27",
        "lat": 21.6850,
        "lng": 69.8520,
        "traffic": 24000,
        "eng": {
            "total_length": 64000.0,
            "number_of_spans": 0,
            "deck_width": 18.0,
            "carriageway_width": 18.0,
            "design_life": 20,
            "year_built": 2010,
            "pavement_type": "Flexible Bituminous Macadam",
            "number_of_lanes": 4,
        },
        "condition": {"health": 54.2, "cat": "FAIR", "struct": 52.0, "func": 56.0, "safe": 55.0},
        "components": [
            ("PAVEMENT_SURFACE", 3, "Monsoon water ponding; localized alligator fatigue cracking"),
            ("SHOULDERS", 2, "Erosion on unpaved earthen shoulder edge drops (> 75mm)"),
        ],
        "events": ["COMMISSIONED", "INSPECTION_COMPLETED", "MAINTENANCE_STARTED"]
    },
    {
        "asset_type": "HIGHWAY",
        "code": "HW-GJ-0005",
        "name": "SH-41 Mehsana-Palanpur Industrial Corridor",
        "bridge_type": "OTHER",
        "structure_category": "MAJOR",
        "status": "CLOSED",
        "department": "Gujarat State Road Dev Corp",
        "district": "Mehsana",
        "road": "State Highway 41",
        "lat": 23.8200,
        "lng": 72.3950,
        "traffic": 18000,
        "eng": {
            "total_length": 52000.0,
            "number_of_spans": 0,
            "deck_width": 10.0,
            "carriageway_width": 10.0,
            "design_life": 20,
            "year_built": 2002,
            "pavement_type": "Semi-Dense Bituminous Concrete",
            "number_of_lanes": 2,
        },
        "condition": {"health": 34.0, "cat": "POOR", "struct": 30.0, "func": 36.0, "safe": 36.0},
        "components": [
            ("PAVEMENT_SURFACE", 2, "Severe wheel rutting (> 25mm depth) and structural base failure"),
            ("ROAD_BASE", 2, "Subgrade pumping causing recurrent potholes under monsoon loading"),
        ],
        "events": ["COMMISSIONED", "INSPECTION_COMPLETED", "CLOSED"]
    },

    # ── CULVERTS & CROSS-DRAINAGE ──────────────────────────────────────
    {
        "asset_type": "CULVERT",
        "code": "CV-GJ-0001",
        "name": "Mahi Canal Cross-Drainage Box Culvert",
        "bridge_type": "OTHER",
        "structure_category": "CULVERT",
        "status": "OPERATIONAL",
        "department": "Irrigation & PWD Gujarat",
        "district": "Kheda",
        "road": "Kheda-Matar Link Road",
        "lat": 22.7520,
        "lng": 72.6840,
        "traffic": 5400,
        "eng": {
            "total_length": 24.0,
            "number_of_spans": 4,
            "deck_width": 12.0,
            "design_life": 80,
            "year_built": 2016,
            "culvert_type": "RCC Quadruple Box Culvert",
            "opening_span": 3.5,
            "clear_height": 3.0,
            "number_of_lanes": 2,
        },
        "condition": {"health": 86.0, "cat": "GOOD", "struct": 88.0, "func": 85.0, "safe": 85.0},
        "components": [
            ("CULVERT_BARREL", 4, "Box barrels structurally sound; minor algae discoloration"),
            ("CULVERT_APRON", 4, "Concrete downstream apron intact; rip-rap boulders undisturbed"),
            ("CULVERT_SILT_TRAP", 4, "Silt accumulation < 15% barrel clearance"),
        ],
        "events": ["COMMISSIONED", "INSPECTION_COMPLETED"]
    },
    {
        "asset_type": "CULVERT",
        "code": "CV-GJ-0002",
        "name": "Sabarmati Flood Diversion Multi-Cell Culvert",
        "bridge_type": "OTHER",
        "structure_category": "CULVERT",
        "status": "OPERATIONAL",
        "department": "Gandhinagar Municipal Corporation",
        "district": "Gandhinagar",
        "road": "Pethapur - Randheja Road",
        "lat": 23.2840,
        "lng": 72.6710,
        "traffic": 9200,
        "eng": {
            "total_length": 36.0,
            "number_of_spans": 6,
            "deck_width": 14.0,
            "design_life": 100,
            "year_built": 2020,
            "culvert_type": "RCC Multi-Cell Box",
            "opening_span": 4.0,
            "clear_height": 3.5,
            "number_of_lanes": 2,
        },
        "condition": {"health": 89.2, "cat": "EXCELLENT", "struct": 90.0, "func": 89.0, "safe": 89.0},
        "components": [
            ("CULVERT_BARREL", 5, "Precast cells show pristine alignment with elastomeric seals"),
            ("CULVERT_HEADWALL", 5, "Drop inlet headwalls free of vegetation or debris"),
        ],
        "events": ["COMMISSIONED", "INSPECTION_COMPLETED"]
    },
    {
        "asset_type": "CULVERT",
        "code": "CV-GJ-0003",
        "name": "Sardar Sarovar Feeder Siphon Culvert",
        "bridge_type": "OTHER",
        "structure_category": "CULVERT",
        "status": "UNDER_MAINTENANCE",
        "department": "Sardar Sarovar Narmada Nigam",
        "district": "Vadodara",
        "road": "Dabhoi - Bodeli Road",
        "lat": 22.1850,
        "lng": 73.4210,
        "traffic": 4100,
        "eng": {
            "total_length": 48.0,
            "number_of_spans": 3,
            "deck_width": 10.0,
            "design_life": 60,
            "year_built": 2008,
            "culvert_type": "Pre-cast Reinforced Concrete Pipe Battery",
            "opening_span": 2.0,
            "clear_height": 2.0,
            "number_of_lanes": 2,
        },
        "condition": {"health": 58.0, "cat": "FAIR", "struct": 55.0, "func": 60.0, "safe": 59.0},
        "components": [
            ("CULVERT_BARREL", 3, "Pipe joint dislocation in Barrel #2; minor water leakage"),
            ("CULVERT_SILT_TRAP", 2, "Upstream catch pit 60% choked with monsoon silt"),
        ],
        "events": ["COMMISSIONED", "INSPECTION_COMPLETED", "MAINTENANCE_STARTED"]
    },
    {
        "asset_type": "CULVERT",
        "code": "CV-GJ-0004",
        "name": "Bhavnagar Coastal Tidal Inundation Culvert",
        "bridge_type": "OTHER",
        "structure_category": "CULVERT",
        "status": "OPERATIONAL",
        "department": "Bhavnagar Port & PWD",
        "district": "Bhavnagar",
        "road": "Ghogha Coastal Link",
        "lat": 21.6910,
        "lng": 72.2640,
        "traffic": 3800,
        "eng": {
            "total_length": 18.0,
            "number_of_spans": 2,
            "deck_width": 8.5,
            "design_life": 50,
            "year_built": 2012,
            "culvert_type": "Tidal Flap-Gate Slab Culvert",
            "opening_span": 3.0,
            "clear_height": 2.5,
            "number_of_lanes": 2,
        },
        "condition": {"health": 71.5, "cat": "GOOD", "struct": 72.0, "func": 71.0, "safe": 71.0},
        "components": [
            ("CULVERT_BARREL", 4, "Slab top structurally sound; saltwater resistant coating holding"),
            ("CULVERT_WINGWALL", 4, "Masonry wingwalls intact with weep holes operational"),
        ],
        "events": ["COMMISSIONED", "INSPECTION_COMPLETED"]
    },
    {
        "asset_type": "CULVERT",
        "code": "CV-GJ-0005",
        "name": "Vapi Industrial Effluent Drainage Culvert",
        "bridge_type": "OTHER",
        "structure_category": "CULVERT",
        "status": "UNDER_REHABILITATION",
        "department": "GIDC Environmental Infrastructure",
        "district": "Valsad",
        "road": "Vapi GIDC Ring Road",
        "lat": 20.3620,
        "lng": 72.9150,
        "traffic": 11500,
        "eng": {
            "total_length": 16.0,
            "number_of_spans": 2,
            "deck_width": 11.0,
            "design_life": 40,
            "year_built": 1995,
            "culvert_type": "Acid-Resistant RCC Box Culvert",
            "opening_span": 3.2,
            "clear_height": 2.8,
            "number_of_lanes": 2,
        },
        "condition": {"health": 32.5, "cat": "CRITICAL", "struct": 28.0, "func": 35.0, "safe": 34.0},
        "components": [
            ("CULVERT_BARREL", 1, "Extreme chemical concrete spalling; exposed corroded reinforcement"),
            ("CULVERT_WINGWALL", 2, "Right downstream wingwall fractured due to foundation scouring"),
            ("CULVERT_APRON", 2, "Apron slab washed out; scouring undermining barrel outlet"),
        ],
        "events": ["COMMISSIONED", "INSPECTION_COMPLETED", "REHABILITATION_STARTED"]
    }
]

def seed_multi_assets():
    db = SessionLocal()
    try:
        # Get admin / inspector users
        admin_user = db.query(User).filter(User.username == "admin").first()
        inspector_user = db.query(User).filter(User.username == "inspector").first()
        user_id = admin_user.id if admin_user else None
        insp_id = inspector_user.id if inspector_user else user_id

        print(f"[*] Seeding {len(MULTI_ASSETS)} multi-asset infrastructure structures...")
        added_count = 0

        for a in MULTI_ASSETS:
            # Check if exists
            existing = db.query(Bridge).filter(Bridge.bridge_id_str == a["code"]).first()
            if existing:
                continue

            # Create asset
            asset = Bridge(
                bridge_id_str=a["code"],
                name=a["name"],
                asset_type=a["asset_type"],
                bridge_type=a["bridge_type"],
                structure_category=a["structure_category"],
                current_status=a["status"],
                department=a["department"],
                owning_authority=a["department"],
                maintaining_authority=a["department"],
                daily_traffic_estimate=a["traffic"],
                traffic_status="Heavy" if a["traffic"] > 20000 else "Normal",
                responsible_officer_id=user_id,
            )
            db.add(asset)
            db.flush()

            # Location
            loc = BridgeLocation(
                bridge_id=asset.id,
                latitude=a["lat"],
                longitude=a["lng"],
                district=a["district"],
                state="Gujarat",
                road_name=a["road"],
                taluka=a["district"],
                chainage_start=0.0,
                chainage_end=round(a["eng"]["total_length"] / 1000.0, 2),
            )
            db.add(loc)

            # Engineering
            eng_data = a["eng"]
            eng = BridgeEngineering(
                bridge_id=asset.id,
                total_length=eng_data.get("total_length"),
                number_of_spans=eng_data.get("number_of_spans", 1),
                deck_width=eng_data.get("deck_width", 10.0),
                carriageway_width=eng_data.get("carriageway_width", eng_data.get("deck_width", 10.0)),
                number_of_lanes=eng_data.get("number_of_lanes", 2),
                design_life=eng_data.get("design_life", 100),
                year_built=eng_data.get("year_built", 2018),
                tunnel_type=eng_data.get("tunnel_type"),
                bore_diameter=eng_data.get("bore_diameter"),
                ventilation_system=eng_data.get("ventilation_system"),
                pavement_type=eng_data.get("pavement_type"),
                culvert_type=eng_data.get("culvert_type"),
                opening_span=eng_data.get("opening_span"),
                clear_height=eng_data.get("clear_height"),
            )
            db.add(eng)

            # Condition Assessment
            cond_data = a["condition"]
            cond = ConditionAssessment(
                bridge_id=asset.id,
                health_index_score=cond_data["health"],
                condition_category=cond_data["cat"],
                structural_score=cond_data["struct"],
                functional_score=cond_data["func"],
                safety_score=cond_data["safe"],
                assessment_date=datetime.utcnow() - timedelta(days=random.randint(10, 90)),
                calculation_version="prototype-v1",
            )
            db.add(cond)
            db.flush()

            # Inspection + Components
            insp = Inspection(
                bridge_id=asset.id,
                inspector_id=insp_id,
                inspection_type="ROUTINE",
                status="COMPLETED",
                scheduled_date=datetime.utcnow() - timedelta(days=60),
                completion_date=datetime.utcnow() - timedelta(days=58),
                overall_condition=cond_data["cat"],
                overall_comments=f"Periodic comprehensive assessment of {a['name']}",
            )
            db.add(insp)
            db.flush()

            # Add components
            for comp_type, rating, note in a.get("components", []):
                ic = InspectionComponent(
                    inspection_id=insp.id,
                    component_type=comp_type,
                    condition_rating=rating,
                    notes=note,
                )
                db.add(ic)
                db.flush()

                if rating <= 2:
                    defect = Defect(
                        inspection_id=insp.id,
                        component_id=ic.id,
                        defect_type="STRUCTURAL_DISTRESS",
                        severity="CRITICAL" if rating == 1 else "HIGH",
                        description=f"Defect identified during survey: {note}",
                        repair_recommendation="Immediate engineering remediation required",
                        immediate_action_required=(rating == 1),
                        status="OPEN"
                    )
                    db.add(defect)

            # Lifecycle events
            for i, evt_type in enumerate(a.get("events", [])):
                evt = LifecycleEvent(
                    bridge_id=asset.id,
                    event_type=evt_type,
                    event_date=datetime(2020 + i, 1, 15) if i < 3 else datetime.utcnow() - timedelta(days=30 * (len(a.get("events", [])) - i)),
                    description=f"{evt_type.replace('_', ' ')} event for {a['name']}",
                    recorded_by=user_id,
                )
                db.add(evt)

            # If under maintenance/rehab, add a maintenance record
            if a["status"] in ["UNDER_MAINTENANCE", "UNDER_REHABILITATION"]:
                maint = MaintenanceRecord(
                    bridge_id=asset.id,
                    maintenance_type="REHABILITATION" if a["status"] == "UNDER_REHABILITATION" else "PREVENTIVE",
                    priority="CRITICAL" if cond_data["cat"] in ["CRITICAL", "POOR"] else "MEDIUM",
                    status="IN_PROGRESS",
                    description=f"Active civil & mechanical maintenance works for {a['name']}",
                    estimated_cost=random.uniform(5000000, 25000000),
                    start_date=datetime.utcnow() - timedelta(days=20),
                )
                db.add(maint)

            added_count += 1

        db.commit()
        print(f"[SUCCESS] Successfully seeded {added_count} multi-asset infrastructure records!")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to seed multi-asset infrastructure: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_multi_assets()
