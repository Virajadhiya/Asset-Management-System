import asyncio
import httpx
from app.main import app

async def test_all_30_bridge_details():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Login as engineer
        res = await client.post("/api/auth/login", data={"username": "engineer", "password": "eng123"})
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get all bridges
        list_res = await client.get("/api/bridges?limit=100", headers=headers)
        bridges = list_res.json()["items"]
        print(f"Testing individual detail view for all {len(bridges)} bridges...")

        failed = 0
        for b in bridges:
            b_id = b["bridge_id"]
            detail_res = await client.get(f"/api/bridges/{b_id}", headers=headers)
            if detail_res.status_code != 200:
                print(f"[FAIL] Bridge {b['bridge_code']} ({b_id}): {detail_res.status_code} - {detail_res.text}")
                failed += 1
            else:
                detail = detail_res.json()
                # Also test related detail tabs endpoints
                insp_res = await client.get(f"/api/bridges/{b_id}/inspections", headers=headers)
                maint_res = await client.get(f"/api/bridges/{b_id}/maintenance", headers=headers)
                life_res = await client.get(f"/api/bridges/{b_id}/lifecycle", headers=headers)

                assert insp_res.status_code == 200, f"Inspections failed for {b_id}: {insp_res.text}"
                assert maint_res.status_code == 200, f"Maintenance failed for {b_id}: {maint_res.text}"
                assert life_res.status_code == 200, f"Lifecycle failed for {b_id}: {life_res.text}"

        if failed == 0:
            print(f"\n[SUCCESS] All {len(bridges)} bridge detail endpoints + inspections + maintenance + lifecycle returned 200 OK cleanly!")
        else:
            print(f"\n[FAIL] {failed} bridges failed!")

if __name__ == "__main__":
    asyncio.run(test_all_30_bridge_details())
