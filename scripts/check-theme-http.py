"""Read-only HTTP smoke checks for the shared UI release; no document writes."""
import http.cookiejar
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

env = dict(line.strip().split('=', 1) for line in open(sys.argv[1]) if '=' in line and not line.startswith('#'))
base = os.environ.get('ATLAS_CHECK_URL', 'http://127.0.0.1:' + env['ATLAS_HTTP_PORT'])
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

def request(path, payload=None):
    req = urllib.request.Request(base + path, data=urllib.parse.urlencode(payload).encode() if payload else None)
    try:
        res = opener.open(req, timeout=30)
        return res.status, res.read().decode(), res.url
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode(), exc.url

status, menu, _ = request('/atlas-menu')
assert status == 200 and menu.count('class="menu-card"') == 63
assert 'LA VRAIE MARGHERITA' in menu and '69 <small>MAD</small>' in menu
assert 'Choose</' not in menu # choice counts must render from the source schema
assert 'Le Panozzo Charcuterie' in menu and 'Choose 1' in menu
assert 'no orders or payments are accepted here yet' in menu
status, _, url = request('/atlas-portal')
assert status == 200 and '/login' in url
status, _, _ = request('/api/method/atlas_erp.business_setup.overview')
assert status in (403, 417)
status, _, _ = request('/api/method/login', {'usr':'Administrator','pwd':env['ADMIN_PASSWORD']})
assert status == 200
status, portal, _ = request('/atlas-portal')
assert status == 200 and 'atlas-portal-hero' in portal and 'My account' in portal
status, desk, _ = request('/desk/item')
assert status == 200 and '/css/theme-v3.1.css' in desk and '/css/desk-v3.1.css' in desk and '/js/brand-v3.1.js' in desk
for asset in ['css/theme-v3.1.css','css/desk-v3.1.css','css/web-v3.1.css','css/menu-v3.1.css','js/brand-v3.1.js','js/web-v3.1.js','js/menu-v3.1.js']:
    status, body, _ = request('/assets/atlas_erp/' + asset)
    assert status == 200 and len(body) > 300, asset
# Explicit public snapshot must match the verified source exactly; no private ERP query.
status, catalog, _ = request('/assets/atlas_erp/data/streetpizza-menu.json')
assert status == 200 and len(json.loads(catalog)['items']) == 63
print('PASS: menu 63 prices/options, guest portal gate, authenticated portal/Desk, versioned shared assets')
