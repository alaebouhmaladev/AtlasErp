import frappe
from frappe import _

from atlas_erp.permissions import can_access
from atlas_erp.app_catalog import available_apps

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
    context.applications = available_apps()
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
        (_("Sales leads"), _("Leads and opportunities in your ERP workspace"), "Lead", "lead", _("New lead")),
        (_("Manufacturing"), _("Production planning, work orders and bills of materials"), "Work Order", "work-order", _("New work order")),
        (_("Assets"), _("Assets, depreciation and asset movements"), "Asset", "asset", _("New asset")),
        (_("Quality"), _("Inspections and quality controls"), "Quality Inspection", "quality-inspection", _("New inspection")),
        (_("Support"), _("Customer issues and support requests"), "Issue", "issue", _("New issue")),
        (_("Maintenance"), _("Maintenance visits and service schedules"), "Maintenance Visit", "maintenance-visit", _("New visit")),
        (_("Subscriptions"), _("Recurring billing and subscription records"), "Subscription", "subscription", _("New subscription")),
        (_("Employees"), _("Employee records and your organization"), "Employee", "employee", _("New employee")),
        (_("Attendance"), _("Attendance records and employee check-ins"), "Attendance", "attendance", _("New attendance")),
        (_("Leave"), _("Leave requests, allocations and approvals"), "Leave Application", "leave-application", _("New leave request")),
        (_("Recruitment"), _("Job openings, applicants and interviews"), "Job Applicant", "job-applicant", _("New applicant")),
        (_("Payroll"), _("Salary slips and payroll processing"), "Salary Slip", "salary-slip", None),
        (_("Expenses"), _("Employee expenses and reimbursements"), "Expense Claim", "expense-claim", _("New expense claim")),
    ]:
        if frappe.db.exists("DocType", doctype) and frappe.has_permission(doctype, "read"):
            context.modules.append({
                "title": title,
                "description": description,
                "href": f"/desk/{route}",
                "new_href": f"/desk/{route}/new" if action and frappe.has_permission(doctype, "create") else None,
                "action": action,
            })
    context.can_setup = bool({"System Manager", "ATLAS Owner"} & set(frappe.get_roles()))
    context.has_business_access = context.can_setup or any(r.startswith("ATLAS ") for r in frappe.get_roles())
    return context
