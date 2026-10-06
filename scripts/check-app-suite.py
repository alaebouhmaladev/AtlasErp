"""Read-only app installation, launcher and core POS regression inventory."""

import json
import os

import frappe
from frappe.apps import get_apps
from frappe.boot import get_app_data

from atlas_erp.app_catalog import available_apps
from atlas_erp.branding import boot_session
from atlas_erp.www.atlas import get_context


def main():
    os.chdir("sites")
    frappe.init(site=os.environ.get("ATLAS_CHECK_SITE", "atlas-onboarding.localhost"))
    frappe.connect()
    try:
        frappe.set_user("Administrator")
        installed = set(frappe.get_installed_apps())
        assert {"erpnext", "atlas_erp", "hrms", "whatsapp", "crm"} <= installed
        for doctype in ["Employee", "Attendance", "Leave Application", "Salary Slip", "CRM Lead", "CRM Deal"]:
            assert frappe.db.exists("DocType", doctype), doctype
            frappe.get_meta(doctype)
        apps = get_apps()
        names = {app["name"] for app in apps}
        assert {"erpnext", "hrms", "crm"} <= names, names
        context = get_context(frappe._dict())
        assert len(context.modules) >= 20
        assert any(app["title"] == "ATLAS HR" for app in available_apps())
        assert any(app["title"] == "ATLAS CRM" for app in available_apps())
        boot = frappe._dict(app_data=get_app_data())
        boot_session(boot)
        branded = {app["app_name"]: app for app in boot.app_data}
        assert branded["hrms"]["app_title"] == "ATLAS HR"
        assert branded["crm"]["app_title"] == "ATLAS CRM"
        assert branded["crm"]["app_route"] == "/crm"
        assert frappe.db.get_single_value("FCRM Settings", "brand_name") == "ATLAS CRM"
        print(json.dumps({"installed": sorted(installed), "applications": context.applications,
                          "tool_count": len(context.modules), "native_launcher": [
                              {"name": a["app_name"], "title": a["app_title"], "route": a["app_route"]}
                              for a in boot.app_data if a.get("on_apps_screen")]}))
        print("PASS: app schemas, permitted application catalog and native launcher metadata")
    finally:
        frappe.destroy()


if __name__ == "__main__":
    main()
