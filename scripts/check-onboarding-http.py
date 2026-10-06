"""Read-only HTTP/auth checks; run on the VPS with its private env file path."""
import http.cookiejar
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

env = dict(line.strip().split("=", 1) for line in open(sys.argv[1])
           if "=" in line and not line.startswith("#"))
base = os.environ.get("ATLAS_CHECK_URL", "http://127.0.0.1:" + env["ATLAS_HTTP_PORT"])
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def request(path, payload=None, csrf=None):
    headers = {}
    if csrf:
        headers["X-Frappe-CSRF-Token"] = csrf
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(base + path, headers=headers,
                                 data=json.dumps(payload).encode() if payload is not None else None)
    try:
        response = opener.open(req, timeout=30)
        return response.status, response.read().decode(), response.url
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode(), error.url


status, body, url = request("/atlas-setup")
assert status == 200 and "/login" in url
status, _, _ = request("/api/method/atlas_erp.business_setup.overview")
assert status in {403, 417}
status, _, _ = request("/api/method/login", {"usr": "Administrator", "pwd": env["ADMIN_PASSWORD"]})
assert status == 200, "Administrator login failed"
status, page, _ = request("/atlas-setup")
assert status == 200 and "brand-form" in page and "team-form" in page
csrf = re.search(r'<meta name="csrf-token" content="([^"]+)"', page).group(1)
status, body, _ = request("/api/method/atlas_erp.business_setup.overview")
assert status == 200 and json.loads(body)["message"]["is_admin"]
for asset in ["css/setup.css", "js/setup.js"]:
    status, body, _ = request("/assets/atlas_erp/" + asset)
    assert status == 200 and len(body) > 500
endpoint = "/api/method/atlas_erp.business_setup.save_brand"
status, _, _ = request(endpoint, {"company": "", "brand_name": "HTTP check"})
assert status == 400, "Missing CSRF token was accepted"
status, body, _ = request(endpoint, {"company": "", "brand_name": "HTTP check"}, csrf)
assert status == 417 and "Choose a valid legal company" in body
status, _, _ = request("/api/method/logout", {}, csrf)
assert status == 200
print("PASS: guest redirect/denial, admin login, setup page, assets, overview and CSRF enforcement")
