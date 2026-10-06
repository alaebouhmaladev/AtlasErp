"""Installed application navigation using the framework's own access checks."""

from frappe import _
from frappe.apps import get_apps

APP_TITLES = {"erpnext": "ATLASERP", "hrms": "ATLAS HR", "crm": "ATLAS CRM"}


def available_apps():
    descriptions = {
        "erpnext": _("Sales, stock, purchasing, accounting and business operations"),
        "hrms": _("Employees, attendance, leave, recruitment and payroll"),
        "crm": _("Leads, deals, contacts and sales activities"),
    }
    return [
        {
            "title": _(APP_TITLES.get(app["name"], app["title"])),
            "description": descriptions.get(app["name"], _("Open this installed application")),
            "href": app["route"],
            "logo": ("/assets/atlas_erp/images/atlas-mark.svg" if app["name"] in APP_TITLES
                     else app.get("logo") or "/assets/atlas_erp/images/atlas-mark.svg"),
        }
        for app in get_apps()
        if app.get("route")
    ]
