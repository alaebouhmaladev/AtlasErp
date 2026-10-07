import frappe

from atlas_erp.pos_api.readiness import overview

no_cache = 1
sitemap = 0


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=%2Fatlas-pos"
        raise frappe.Redirect
    context.update(overview())
    context.no_cache = 1
    context.title = "Point of sale · ATLASERP"
    return context
