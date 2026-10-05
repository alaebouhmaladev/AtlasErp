import frappe
from frappe import _

from atlas_erp.permissions import can_access

no_cache = 1
sitemap = 0


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=%2Fatlas"
        raise frappe.Redirect
    if not can_access():
        frappe.throw(_("ATLASERP is available to internal users."), frappe.PermissionError)

    context.no_cache = 1
    context.title = "ATLASERP"
    context.display_name = frappe.get_cached_value("User", frappe.session.user, "first_name")
    context.modules = []
    # Navigation respects doctype permissions. ERPNext remains responsible for
    # document/company access on every destination and backend request.
    for title, description, doctype, route, action in [
        (_("Point of sale"), _("Checkout, receipts and cashier sessions"), "POS Invoice", "point-of-sale", None),
        (_("Sales"), _("Quotes, orders and customer invoices"), "Sales Invoice", "sales-invoice", _("New invoice")),
        (_("Customers"), _("Your customer directory and contacts"), "Customer", "customer", _("New customer")),
        (_("Purchasing"), _("Supplier orders and purchase invoices"), "Purchase Order", "purchase-order", _("New purchase order")),
        (_("Inventory"), _("Items, warehouses and stock movements"), "Item", "item", _("New item")),
        (_("Payments"), _("Incoming and outgoing payments"), "Payment Entry", "payment-entry", _("New payment")),
        (_("Accounting"), _("Accounts and journal entries"), "Journal Entry", "journal-entry", _("New journal entry")),
        (_("Projects"), _("Projects, tasks and delivery"), "Project", "project", _("New project")),
    ]:
        if frappe.has_permission(doctype, "read"):
            context.modules.append({
                "title": title,
                "description": description,
                "href": f"/desk/{route}",
                "new_href": f"/desk/{route}/new" if action and frappe.has_permission(doctype, "create") else None,
                "action": action,
            })
    context.can_setup = "System Manager" in frappe.get_roles()
    return context
