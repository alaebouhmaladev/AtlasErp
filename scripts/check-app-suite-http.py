"""Read-only application routes and built assets; credentials stay in the private env."""

import http.cookiejar
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


def request(path, payload=None):
    data = urllib.parse.urlencode(payload).encode() if payload else None
    try:
        response = opener.open(urllib.request.Request(base + path, data=data), timeout=30)
        return response.status, response.read().decode(), response.url
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode(), exc.url


status, _, url = request("/atlas")
assert status == 200 and "/login" in url
# Some apps serve a public login shell. Their private records must remain gated.
for doctype in ("Employee", "CRM Lead"):
    status, _, _ = request("/api/resource/" + urllib.parse.quote(doctype))
    assert status in (403, 417), (doctype, status)

status, _, _ = request("/api/method/login", {"usr": "Administrator", "pwd": env["ADMIN_PASSWORD"]})
assert status == 200, "Administrator login failed"
status, workspace, _ = request("/atlas")
assert status == 200 and "ATLAS HR" in workspace and "ATLAS CRM" in workspace
for route, app in (("/crm", "crm"), ("/hrms", "hrms")):
    status, body, url = request(route)
    assert status == 200 and "/login" not in url, (route, status, url)
    paths = set(re.findall(r'(?:src|href)=[\"\']([^\"\']+)[\"\']', body))
    assets = [path for path in paths if path.startswith(f"/assets/{app}/")
              and path.split("?", 1)[0].endswith((".js", ".css"))]
    assert assets, f"No built assets in {route}"
    for path in assets:
        status, asset, _ = request(path)
        assert status == 200 and asset.strip() and not asset.lstrip().lower().startswith("<!doctype"), (path, status)
    print(f"PASS: {route} authenticated HTML and {len(assets)} built assets")
print("PASS: guest workspace/private-record gates and authenticated ATLAS application workspace")
