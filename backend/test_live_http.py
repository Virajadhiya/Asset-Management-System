import urllib.request
import urllib.parse
import json

def test_live_server():
    users = ["admin", "dept_head", "engineer", "inspector", "maint_off", "viewer"]
    pwds = {
        "admin": "admin123",
        "dept_head": "dept123",
        "engineer": "eng123",
        "inspector": "insp123",
        "maint_off": "maint123",
        "viewer": "view123",
    }
    
    for u in users:
        print(f"\n--- Testing Live HTTP for User: {u} ---")
        login_url = "http://127.0.0.1:8000/api/auth/login"
        data = urllib.parse.urlencode({"username": u, "password": pwds[u]}).encode()
        req = urllib.request.Request(login_url, data=data, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                body = json.loads(resp.read().decode())
                token = body["access_token"]
                role = body["user"]["role"]
                perms = body["user"]["permissions"]
                print(f"Login 200 OK: role={role}, perms count={len(perms)}")
        except Exception as e:
            print(f"LOGIN FAILED for {u}: {e}")
            continue

        # Test GET /api/bridges
        bridges_url = "http://127.0.0.1:8000/api/bridges?page=1&limit=10"
        b_req = urllib.request.Request(bridges_url, headers={"Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(b_req) as b_resp:
                b_body = json.loads(b_resp.read().decode())
                items = b_body.get("items", [])
                total = b_body.get("total", 0)
                print(f"GET /api/bridges 200 OK: returned {len(items)} items, total={total}")
        except Exception as e:
            print(f"GET /api/bridges FAILED for {u}: {e}")

        # Test GET /api/dashboard/summary
        dash_url = "http://127.0.0.1:8000/api/dashboard/summary"
        d_req = urllib.request.Request(dash_url, headers={"Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(d_req) as d_resp:
                d_body = json.loads(d_resp.read().decode())
                print(f"GET /api/dashboard/summary 200 OK: total_bridges={d_body.get('total_bridges')}")
        except Exception as e:
            print(f"GET /api/dashboard/summary FAILED for {u}: {e}")

if __name__ == "__main__":
    test_live_server()
