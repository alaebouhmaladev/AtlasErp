import frappe
from atlas_erp.permissions import can_access
from atlas_erp.business_access import is_admin, ROLES

no_cache = 1
sitemap = 0


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=%2Fatlas-setup"
        raise frappe.Redirect
    if not can_access() or not (is_admin() or set(frappe.get_roles()) & {"ATLAS " + r for r in ROLES}):
        frappe.throw("Ask an administrator to assign your business access.", frappe.PermissionError)
    context.no_cache = 1
    context.title = "Business setup · ATLASERP"
    context.csrf_token = frappe.sessions.get_csrf_token()
    return context
