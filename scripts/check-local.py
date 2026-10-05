"""Check local guest/login/launchpad/static assets using only Python's stdlib.

Run after startup: python3 scripts/check-local.py
Passwords are read from the private .env and never printed.
"""

import json
from http.cookiejar import CookieJar
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, build_opener


def main():
    config = {}
    for line in (Path(__file__).resolve().parents[1] / ".env").read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            key, value = line.split("=", 1)
            config[key] = value
    base = "http://localhost:" + config.get("ATLAS_HTTP_PORT", "8000")
    client = build_opener(HTTPCookieProcessor(CookieJar()))
    with client.open(base + "/atlas", timeout=30) as response:
        assert "/login" in response.url, "Guest was not redirected to login"
    print("PASS: guest redirected to login")

    data = urlencode({"usr": "Administrator", "pwd": config["ADMIN_PASSWORD"]}).encode()
    with client.open(base + "/api/method/login", data, timeout=30) as response:
        assert json.load(response)["message"] == "Logged In"
    try:
        with client.open(base + "/atlas", timeout=30) as response:
            html = response.read().decode()
            assert response.status == 200
            assert "Your shop. One clear workspace." in html
            assert "/desk/point-of-sale" in html
            assert "/desk/item" in html
        print("PASS: authenticated launchpad and retail links")
        for path, marker in [
            ("/assets/atlas_erp/css/atlas.css", b"module-grid"),
            ("/assets/atlas_erp/images/atlas-mark.svg", b"<svg"),
        ]:
            with client.open(base + path, timeout=30) as response:
                assert response.status == 200 and marker in response.read()
        print("PASS: CSS and logo assets served")
    finally:
        with client.open(base + "/api/method/logout", data=b"", timeout=30):
            pass


if __name__ == "__main__":
    main()
