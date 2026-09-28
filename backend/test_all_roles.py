import asyncio
import httpx
from app.main import app

async def check():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        users = ["admin", "dept_head", "engineer", "inspector", "maint_off", "viewer"]
        pwds = {
            "admin": "admin123",
            "dept_head": "dept123",
            "engineer": "eng123",
            "inspector": "insp123",
            "maint_off": "maint123",
            "viewer": "view123",
        }
        endpoints = [
            ("GET", "/api/bridges"),
            ("GET", "/api/dashboard/summary"),
            ("GET", "/api/dashboard/priority-list"),
            ("GET", "/api/gis/bridges"),
        ]
        for u in users:
            r = await client.post("/api/auth/login", data={"username": u, "password": pwds[u]})
            if r.status_code != 200:
                print(f"User {u} LOGIN FAILED: {r.status_code} {r.text}")
                continue
            data = r.json()
            token = data["access_token"]
            role = data["user"]["role"]
            perms = data["user"]["permissions"]
            print(f"\n=== User: {u} | Role: {role} | Permissions ({len(perms)}): {perms} ===")
            for method, ep in endpoints:
                res = await client.request(method, ep, headers={"Authorization": f"Bearer {token}"})
                print(f"  {method} {ep} -> {res.status_code}")
                if res.status_code != 200:
                    print(f"    ERROR: {res.text}")

if __name__ == "__main__":
    asyncio.run(check())
