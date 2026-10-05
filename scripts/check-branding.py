"""Read-only local checks for product identity and launcher metadata.

docker compose exec app env/bin/python /workspace/scripts/check-branding.py
"""

import os

import frappe
from frappe.apps import get_apps

from atlas_erp.branding import MARK, WORDMARK


def main():
    os.chdir("sites")
    frappe.init(site=os.environ.get("ATLAS_SITE", "atlas.localhost"))
    frappe.connect()
    try:
        frappe.set_user("Administrator")
        for doctype in ["System Settings", "Website Settings"]:
            assert frappe.db.get_single_value(doctype, "app_name") == "ATLASERP"
        assert frappe.db.get_single_value("Website Settings", "app_logo") == WORDMARK
        assert frappe.db.get_single_value("Website Settings", "favicon") == MARK
        assert frappe.db.get_single_value("Navbar Settings", "app_logo") == WORDMARK
        apps = get_apps()
        product = [app for app in apps if app["title"] == "ATLASERP"]
        assert len(product) == 1, "Expected one product launcher entry"
        assert product[0]["name"] == "erpnext", "Internal app identifier changed"
        assert product[0]["route"] == "/atlas"
        assert not any(app["title"] == "ERPNext" for app in apps)
        assert not any(app["name"] == "atlas_erp" for app in apps)
        navbar = frappe.get_single("Navbar Settings")
        assert any(item.item_label == "About ATLASERP" and item.route == "/atlas-about"
                   for item in navbar.help_dropdown)
        assert all(item.hidden for item in navbar.help_dropdown if item.item_label == "About")
        print("PASS: ATLASERP settings, logos, one launcher entry and About menu")
    finally:
        frappe.destroy()


if __name__ == "__main__":
    main()
