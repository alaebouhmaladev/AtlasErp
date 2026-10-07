"""Verify POS readiness over HTTP without opening a register or selling."""
import http.cookiejar
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


env = dict(line.strip().split("=", 1) for line in open(sys.argv[1])
           if "=" in line and not line.startswith("#"))
base = os.environ.get("ATLAS_CHECK_URL", "http://127.0.0.1:" + env["ATLAS_HTTP_PORT"])
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def request(path, payload=None):
    try:
        response = opener.open(base + path, data=urllib.parse.urlencode(payload).encode() if payload else None, timeout=30)
        return response.status, response.read().decode(), response.url
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode(), exc.url


status, _, url = request("/atlas-pos")
assert status == 200 and "/login" in url
status, _, _ = request("/api/method/atlas_erp.pos_api.readiness.overview")
assert status in (403, 417)
status, _, _ = request("/api/method/login", {"usr": "Administrator", "pwd": env["ADMIN_PASSWORD"]})
assert status == 200
status, body, _ = request("/atlas-pos")
assert status == 200 and "Ready for your next customer" in body and "Street Pizza" in body
status, css, _ = request("/assets/atlas_erp/css/pos-readiness-v1.css")
assert status == 200 and ".register-grid" in css
status, data, _ = request("/api/method/atlas_erp.pos_api.readiness.overview")
assert status == 200 and json.loads(data)["message"]["registers"]
status, _, _ = request("/api/method/atlas_erp.pos_api.readiness.register_context?pos_profile=forged-register")
assert status in (403, 417)
print("PASS: guest gating, authenticated POS readiness HTML/API/CSS, forged register rejection")
