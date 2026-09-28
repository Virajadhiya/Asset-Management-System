import asyncio
import httpx
from app.main import app

async def run_tests():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        print("\n==============================================")
        print("PRAVI PLATFORM - COMPREHENSIVE SECURITY & API TESTS")
        print("==============================================")

        # 1. Logins
        print("\n--- 1. Authenticating Demo Users ---")
        tokens = {}
        for role, user, pwd in [
            ("ADMIN", "admin", "admin123"),
            ("DEPARTMENT_HEAD", "dept_head", "dept123"),
            ("EXECUTIVE_ENGINEER", "engineer", "eng123"),
            ("INSPECTOR", "inspector", "insp123"),
            ("MAINTENANCE_OFFICER", "maint_off", "maint123"),
            ("VIEWER", "viewer", "view123"),
        ]:
            res = await client.post("/api/auth/login", data={"username": user, "password": pwd})
            assert res.status_code == 200, f"Login failed for {user}: {res.text}"
            tokens[role] = res.json()["access_token"]
            print(f"[OK] Logged in as {role} ({user})")

        # 2. Cross-role RBAC Enforcement
        print("\n--- 2. Verifying Cross-Role Server-Side RBAC Enforcement ---")
        
        # Test A: Viewer -> POST /api/bridges (MUST 403)
        res = await client.post(
            "/api/bridges",
            headers={"Authorization": f"Bearer {tokens['VIEWER']}"},
            json={"name": "Hacked Bridge", "bridge_type": "BEAM", "structure_category": "MAJOR", "current_status": "PLANNED", "location": {"latitude": 23.0, "longitude": 72.0, "district": "Ahmedabad", "state": "Gujarat"}, "engineering": {}}
        )
        assert res.status_code == 403, f"Expected 403 for Viewer bridge creation, got {res.status_code}"
        print("[PASS] Viewer -> POST /api/bridges: 403 Forbidden")

        # Get a sample bridge ID
        res = await client.get("/api/bridges?limit=1", headers={"Authorization": f"Bearer {tokens['ADMIN']}"})
        sample_bridge_id = res.json()["items"][0]["bridge_id"]

        # Test B: Inspector -> PUT /api/bridges/{id} (MUST 403, inspectors inspect, engineers update)
        res = await client.put(
            f"/api/bridges/{sample_bridge_id}",
            headers={"Authorization": f"Bearer {tokens['INSPECTOR']}"},
            json={"name": "Inspector Renamed Bridge"}
        )
        assert res.status_code == 403, f"Expected 403 for Inspector bridge update, got {res.status_code}"
        print("[PASS] Inspector -> PUT /api/bridges/{id}: 403 Forbidden")

        # Test C: Maintenance Officer -> POST /api/bridges/{id}/inspections (MUST 403)
        res = await client.post(
            f"/api/bridges/{sample_bridge_id}/inspections",
            headers={"Authorization": f"Bearer {tokens['MAINTENANCE_OFFICER']}"},
            json={"inspection_type": "ROUTINE", "findings": "Unauthorized"}
        )
        assert res.status_code == 403, f"Expected 403 for Maintenance Officer creating inspection, got {res.status_code}"
        print("[PASS] Maintenance Officer -> POST /api/bridges/{id}/inspections: 403 Forbidden")

        # Test D: Viewer -> GET /api/audit/logs (MUST 403)
        res = await client.get("/api/audit/logs", headers={"Authorization": f"Bearer {tokens['VIEWER']}"})
        assert res.status_code == 403, f"Expected 403 for Viewer audit read, got {res.status_code}"
        print("[PASS] Viewer -> GET /api/audit/logs: 403 Forbidden")

        # Test E: Admin / Engineer -> PUT /api/bridges/{id} with current_status (MUST BE IGNORED)
        orig_res = await client.get(f"/api/bridges/{sample_bridge_id}", headers={"Authorization": f"Bearer {tokens['ADMIN']}"})
        original_status = orig_res.json()["current_status"]
        
        # Attempt to maliciously set status to DECOMMISSIONED directly via PUT
        res = await client.put(
            f"/api/bridges/{sample_bridge_id}",
            headers={"Authorization": f"Bearer {tokens['EXECUTIVE_ENGINEER']}"},
            json={"name": "Updated Bridge Name", "current_status": "DECOMMISSIONED"}
        )
        assert res.status_code == 200, f"Update failed: {res.text}"
        after_res = await client.get(f"/api/bridges/{sample_bridge_id}", headers={"Authorization": f"Bearer {tokens['ADMIN']}"})
        after_status = after_res.json()["current_status"]
        assert after_status == original_status, f"CRITICAL: current_status was modified via direct PUT! Expected {original_status}, got {after_status}"
        print(f"[PASS] Direct PUT current_status mutation safely stripped/ignored! Status remains: {after_status}")

        # 3. Domain Workflow Tests
        print("\n--- 3. Testing Core Lifecycle & Maintenance Workflows ---")
        
        # Test Inspector creating a real inspection with component scores
        insp_res = await client.post(
            f"/api/bridges/{sample_bridge_id}/inspections",
            headers={"Authorization": f"Bearer {tokens['INSPECTOR']}"},
            json={
                "inspection_type": "PRINCIPAL",
                "weather_condition": "Clear",
                "findings": "Routine verification of bearings and expansion joints",
                "recommendations": "Apply anti-corrosive coating",
                "components": [
                    {"component_type": "DECK", "condition_rating": 4, "notes": "Good"},
                    {"component_type": "SUPERSTRUCTURE", "condition_rating": 4, "notes": "Minor hair cracks"},
                    {"component_type": "SUBSTRUCTURE", "condition_rating": 5, "notes": "Sound"},
                    {"component_type": "FOUNDATION", "condition_rating": 5, "notes": "Stable"},
                    {"component_type": "BEARINGS", "condition_rating": 3, "notes": "Moderate corrosion"},
                    {"component_type": "EXPANSION_JOINTS", "condition_rating": 4, "notes": "Clean"}
                ],
                "defects": [
                    {"defect_type": "Bearing Corrosion", "severity": "MEDIUM", "component_type": "BEARINGS", "description": "Left pier bearing surface corrosion"}
                ]
            }
        )
        assert insp_res.status_code == 201, f"Inspection creation failed: {insp_res.text}"
        print("[PASS] Inspector recorded inspection with components and defects")

        # Test Maintenance Officer reporting an issue
        maint_res = await client.post(
            f"/api/bridges/{sample_bridge_id}/maintenance",
            headers={"Authorization": f"Bearer {tokens['MAINTENANCE_OFFICER']}"},
            json={
                "maintenance_type": "REPAIR",
                "priority": "HIGH",
                "description": "Bearing cleaning and lubrication",
                "estimated_cost": 75000.0
            }
        )
        assert maint_res.status_code == 201, f"Maintenance creation failed: {maint_res.text}"
        maint_id = maint_res.json()["maintenance_id"]
        print(f"[PASS] Maintenance Officer logged maintenance ticket: {maint_id}")

        # Test Engineer approving the maintenance
        appr_res = await client.put(
            f"/api/maintenance/{maint_id}/status",
            headers={"Authorization": f"Bearer {tokens['EXECUTIVE_ENGINEER']}"},
            json={"action": "approve", "remarks": "Approved by EE"}
        )
        assert appr_res.status_code == 200, f"Approve failed: {appr_res.text}"
        print("[PASS] Executive Engineer approved maintenance workflow")

        # Verify lifecycle timeline recorded these domain events
        life_res = await client.get(f"/api/bridges/{sample_bridge_id}/lifecycle", headers={"Authorization": f"Bearer {tokens['VIEWER']}"})
        assert life_res.status_code == 200
        events = life_res.json()
        assert any(e["event_type"] == "INSPECTION_COMPLETED" for e in events), "Inspection event missing from lifecycle timeline"
        print("[PASS] Lifecycle timeline contains automatic INSPECTION_COMPLETED event")

        print("\n==============================================")
        print("ALL SECURITY, RBAC & DOMAIN WORKFLOW TESTS PASSED!")
        print("==============================================")

if __name__ == "__main__":
    asyncio.run(run_tests())
