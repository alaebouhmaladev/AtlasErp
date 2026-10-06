"""Customer entry point; document retrieval stays in native scoped portal routes."""
import frappe
from frappe import _

no_cache = 1
sitemap = 0


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=%2Fatlas-portal"
        raise frappe.Redirect
    context.no_cache = 1
    context.title = _("Your customer workspace")
    context.show_sidebar = True
    context.display_name = frappe.get_cached_value("User", frappe.session.user, "first_name")
    context.tools = []
    # Mirrors ERPNext's supported portal roles, not internal Desk permissions.
    roles = set(frappe.get_roles())
    if "Customer" in roles:
        context.tools.extend([
            {"title": _("Orders"), "description": _("Follow your orders and their progress."), "href": "/orders"},
            {"title": _("Invoices"), "description": _("View your invoices and payment status."), "href": "/invoices"},
            {"title": _("Quotations"), "description": _("Review proposals prepared for you."), "href": "/quotations"},
            {"title": _("Shipments"), "description": _("Follow deliveries for your orders."), "href": "/shipments"},
            {"title": _("Support"), "description": _("View and follow your support requests."), "href": "/issues"},
        ])
    if "Supplier" in roles:
        context.tools.extend([
            {"title": _("Purchase orders"), "description": _("Review orders sent to your business."), "href": "/purchase-orders"},
            {"title": _("Purchase invoices"), "description": _("View your supplier invoices."), "href": "/purchase-invoices"},
        ])
    context.tools.append({"title": _("My account"), "description": _("Manage your profile and account details."), "href": "/me"})
    context.sidebar_items = [{"title": _("Overview"), "route": "/atlas-portal"}] + [
        {"title": tool["title"], "route": tool["href"]} for tool in context.tools if tool["href"] != "/me"
    ]
    context.sidebar_title = _("YOUR ACCOUNT")
    return context
