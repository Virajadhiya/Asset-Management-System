import requests

BASE_URL = "http://127.0.0.1:8000/api"

# 1. Login as Admin
login_res = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin", "password": "admin123"})
assert login_res.status_code == 200, f"Login failed: {login_res.text}"
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("[OK] Admin Login successful")

# 2. Login as Executive Engineer
ee_login = requests.post(f"{BASE_URL}/auth/login", data={"username": "engineer", "password": "eng123"})
assert ee_login.status_code == 200, f"EE Login failed: {ee_login.text}"
ee_token = ee_login.json()["access_token"]
ee_headers = {"Authorization": f"Bearer {ee_token}"}
print("[OK] Executive Engineer Login successful")

# 3. Get Bridges
bridges_res = requests.get(f"{BASE_URL}/bridges?status=OPERATIONAL&limit=5", headers=headers)
assert bridges_res.status_code == 200
bridges = bridges_res.json()["items"]
bridge = bridges[0]
bridge_id = bridge["bridge_id"]
print(f"[OK] Retrieved bridge: {bridge['bridge_name']} ({bridge['bridge_code']}), Status: {bridge['current_status']}")

# 4. Report Distress Issue
issue_payload = {
    "bridge_id": bridge_id,
    "source": "FIELD_INSPECTION",
    "issue_type": "STRUCTURAL_CRACK",
    "severity": "CRITICAL",
    "description": "High shear distress crack along pier cap 2; immediate load audit required.",
    "location_details": "Pier 2 downstream bearing pedestal",
    "photo_url": "https://images.unsplash.com/photo-1545558014-8692077e9b5c"
}
issue_res = requests.post(f"{BASE_URL}/issues", json=issue_payload, headers=headers)
assert issue_res.status_code in [200, 201], f"Create issue failed: {issue_res.text}"
issue_data = issue_res.json()
issue_id = issue_data["id"]
print(f"[OK] Created Distress Issue #{issue_id[:8]} with status: {issue_data['status']}")

# 5. Assign Task to Inspector & Engineer
officers_res = requests.get(f"{BASE_URL}/issues/assignable-officers", headers=headers)
officers = officers_res.json()
inspector = officers["inspectors"][0]
engineer = officers["engineers"][0]

assign_res = requests.put(
    f"{BASE_URL}/issues/{issue_id}/assign",
    json={
        "assigned_inspector_id": inspector["id"],
        "assigned_engineer_id": engineer["id"],
        "target_completion_date": "2026-10-05",
        "remarks": "Priority on-site scour & crack inspection assigned."
    },
    headers=headers
)
assert assign_res.status_code == 200
print(f"[OK] Assigned task to Inspector {inspector['full_name']} & Engineer {engineer['full_name']}")

# 6. Conduct Geofenced Inspection (Within 150m of bridge coordinates)
bridge_lat = bridge["latitude"]
bridge_lng = bridge["longitude"]
insp_payload = {
    "inspection_type": "EMERGENT",
    "scheduled_date": "2026-09-28T10:00:00Z",
    "weather_condition": "Clear / Low Flow",
    "overall_comments": "Urgent distress survey completed on site.",
    "inspector_gps_latitude": bridge_lat + 0.0001,  # ~11 meters away
    "inspector_gps_longitude": bridge_lng + 0.0001,
    "photo_evidence_url": "https://images.unsplash.com/photo-1545558014-8692077e9b5c",
    "components": [
        {"component_type": "DECK", "condition_rating": 4, "notes": "Minor wear"},
        {"component_type": "SUBSTRUCTURE", "condition_rating": 2, "notes": "Pier 2 shear crack observed"}
    ],
    "defects": [
        {"severity": "CRITICAL", "description": "Pier 2 shear crack 2.5mm width"}
    ]
}
insp_res = requests.post(f"{BASE_URL}/bridges/{bridge_id}/inspections", json=insp_payload, headers=headers)
assert insp_res.status_code == 201, f"Create inspection failed: {insp_res.text}"
insp_data = insp_res.json()
insp_id = insp_data["inspection_id"]
print(f"[OK] Inspection recorded! Geofence verified: {insp_data['geofence_verified']}, Distance: {insp_data['geofence_distance_meters']}m")

# 7. Counter-Sign Inspection by Executive Engineer
cs_res = requests.post(
    f"{BASE_URL}/inspections/{insp_id}/counter-sign",
    json={"verification_remarks": "Reviewed field survey, distress measurements and photo evidence. Countersigned."},
    headers=ee_headers
)
assert cs_res.status_code == 200, f"Counter-sign failed: {cs_res.text}"
print(f"[OK] Executive Engineer Counter-Signed inspection #{insp_id[:8]}")

# 8. Maintenance Procurement Lifecycle (6 Stages)
# Stage 1: Reported
maint_create_res = requests.post(
    f"{BASE_URL}/bridges/{bridge_id}/maintenance",
    json={
        "maintenance_type": "REPAIR",
        "priority": "HIGH",
        "description": "Pier 2 structural jacketing and epoxy injection repair.",
        "estimated_cost": 250000
    },
    headers=headers
)
assert maint_create_res.status_code in [200, 201], f"Maint create failed: {maint_create_res.text}"
maint_id = maint_create_res.json()["maintenance_id"]
print(f"[OK] Maintenance Record #{maint_id[:8]} created in state: REPORTED")

# Stage 2: DPR Estimate prepared by Executive Engineer
est_res = requests.put(
    f"{BASE_URL}/maintenance/{maint_id}/status",
    json={
        "action": "estimate",
        "estimated_cost": 320000,
        "remarks": "DPR estimate prepared with Schedule of Rates SoR-2026."
    },
    headers=ee_headers
)
assert est_res.status_code == 200
print(f"[OK] DPR Estimate recorded by Executive Engineer: Rs {est_res.json()['estimated_cost']}")

# Stage 3: Financial Sanction (AA) by Department Head
dh_login = requests.post(f"{BASE_URL}/auth/login", data={"username": "dept_head", "password": "dept123"})
dh_token = dh_login.json()["access_token"]
dh_headers = {"Authorization": f"Bearer {dh_token}"}

sanc_res = requests.put(
    f"{BASE_URL}/maintenance/{maint_id}/status",
    json={
        "action": "sanction",
        "sanction_number": "AA/PWD/2026/088",
        "sanctioned_amount": 320000,
        "remarks": "Administrative Approval and Financial Sanction accorded."
    },
    headers=dh_headers
)
assert sanc_res.status_code == 200
print(f"[OK] Financial Sanction granted: #{sanc_res.json()['sanction_number']} for Rs {sanc_res.json()['sanctioned_amount']}")

# Stage 4: Tender Award & Work Order
tender_res = requests.put(
    f"{BASE_URL}/maintenance/{maint_id}/status",
    json={
        "action": "award_tender",
        "tender_number": "NIT/NHAI/2026/045",
        "work_order_number": "WO-PWD-7712",
        "tender_value": 315000,
        "assigned_contractor": "Larsen & Toubro Ltd.",
        "remarks": "Work Order issued to L1 contractor."
    },
    headers=headers
)
assert tender_res.status_code == 200
print(f"[OK] Work Order #{tender_res.json()['work_order_number']} awarded to {tender_res.json()['assigned_contractor']}")

# Stage 5: Mobilize & Start Work
start_res = requests.put(
    f"{BASE_URL}/maintenance/{maint_id}/status",
    json={"action": "start", "remarks": "Contractor mobilized equipment on site."},
    headers=headers
)
assert start_res.status_code == 200
bridge_after_start = requests.get(f"{BASE_URL}/bridges/{bridge_id}", headers=headers).json()
print(f"[OK] Work Started! Bridge status automatically updated to: {bridge_after_start['current_status']}")

# Stage 6: Mark Complete
comp_res = requests.put(
    f"{BASE_URL}/maintenance/{maint_id}/status",
    json={"action": "complete", "actual_cost": 312000, "remarks": "Physical repairs completed."},
    headers=headers
)
assert comp_res.status_code == 200
print(f"[OK] Work Completed! Final Expenditure: Rs {comp_res.json()['actual_cost']}")

# Stage 7: Quality Verification by Executive Engineer
verify_res = requests.put(
    f"{BASE_URL}/maintenance/{maint_id}/status",
    json={"action": "verify", "remarks": "Field inspection verified quality compliance. Issued Completion Certificate."},
    headers=ee_headers
)
assert verify_res.status_code == 200
bridge_after_verify = requests.get(f"{BASE_URL}/bridges/{bridge_id}", headers=headers).json()
print(f"[OK] Quality Verified by Executive Engineer! Bridge restored to: {bridge_after_verify['current_status']}")

print("\nALL INDIAN GOVERNMENT INFRASTRUCTURE WORKFLOW TESTS PASSED!")
