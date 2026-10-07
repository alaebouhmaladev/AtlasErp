"""Read-only checkout smoke test; never opens a shift or submits an invoice."""
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
profile = os.environ.get("ATLAS_CHECK_PROFILE", "Street Pizza - Maarif - Demo POS")
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def request(path, payload=None):
    try:
        response = opener.open(base + path, data=urllib.parse.urlencode(payload).encode() if payload else None, timeout=30)
        return response.status, response.read().decode()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()


query = "?" + urllib.parse.urlencode({"pos_profile": profile})
for method in ("context", "service_addons"):
    status, _ = request("/api/method/atlas_erp.pos_api.checkout." + method + query)
    assert status in (403, 417), "Guest checkout endpoint was accessible"
status, _ = request("/api/method/login", {"usr": "Administrator", "pwd": env["ADMIN_PASSWORD"]})
assert status == 200, "Existing administrator login failed"
status, data = request("/api/method/atlas_erp.pos_api.checkout.context" + query)
assert status == 200, "Checkout context failed over HTTP"
context = json.loads(data)["message"]
assert context["pos_profile"] == profile and context["currency"] == "MAD"
status, data = request("/api/method/atlas_erp.pos_api.checkout.service_addons" + query)
assert status == 200, "Service catalog failed over HTTP"
addons = json.loads(data)["message"]
assert isinstance(addons, list)
if os.environ.get("ATLAS_CHECK_FIXTURE") == "1":
    assert len(addons) == 1 and addons[0]["rate"] == 100
    assert context["tips_enabled"] and context["confirm_external"]
else:
    assert not context["tips_enabled"] and not context["confirm_external"] and not addons
status, _ = request("/api/method/atlas_erp.pos_api.checkout.context?pos_profile=forged-register")
assert status in (403, 404, 417)
print("PASS: checkout HTTP authentication, MAD context, service catalog and forged-profile rejection")
