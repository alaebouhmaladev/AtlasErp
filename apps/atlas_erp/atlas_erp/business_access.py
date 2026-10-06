"""Explicit scopes for business metadata; roles alone never grant all branches."""
import frappe

BRAND = "Atlas Business Brand"
BRANCH = "Atlas Business Branch"
TEAM = "Atlas Team Member"
ROLES = ("Owner", "Manager", "Cashier", "Waiter")


def is_admin(user=None):
    return "System Manager" in frappe.get_roles(user or frappe.session.user)


def assignments(user=None):
    user = user or frappe.session.user
    if user == "Guest" or not frappe.db.exists("DocType", TEAM):
        return []
    return frappe.get_all(TEAM, filters={"user": user, "enabled": 1},
                          fields=["company", "branch", "staff_role"])


def owned_companies(user=None):
    return {r.company for r in assignments(user) if r.staff_role == "Owner"}


def can_manage(company, user=None):
    return is_admin(user) or company in owned_companies(user)


def check_manage(company):
    if not company or not frappe.db.exists("Company", {"name": company, "is_group": 0}):
        frappe.throw("Choose a valid legal company.")
    if not can_manage(company):
        frappe.throw("You cannot manage this company.", frappe.PermissionError)


def permitted_names(doctype, user=None):
    rows = assignments(user)
    companies = {r.company for r in rows if r.staff_role == "Owner"}
    branches = {r.branch for r in rows}
    if doctype == BRANCH:
        return {r.name for r in frappe.get_all(BRANCH, fields=["name", "company"])
                if r.company in companies or r.name in branches}
    if doctype == BRAND:
        brands = {r.brand for r in frappe.get_all(BRANCH, filters={"name": ["in", list(branches)]},
                                                 fields=["brand"])} if branches else set()
        return {r.name for r in frappe.get_all(BRAND, fields=["name", "company"])
                if r.company in companies or r.name in brands}
    return {r.name for r in frappe.get_all(TEAM, fields=["name", "company", "user"])
            if r.company in companies or r.user == (user or frappe.session.user)}


def record_permission(doc, user=None, ptype=None):
    if is_admin(user):
        return True
    if ptype in {"read", "select", "report", None}:
        return doc.name in permitted_names(doc.doctype, user)
    if doc.doctype == TEAM:
        return False
    return doc.company in owned_companies(user)


def query_condition(doctype, user=None):
    if is_admin(user):
        return ""
    names = permitted_names(doctype, user)
    if not names:
        return "1=0"
    values = ",".join(frappe.db.escape(n) for n in names)
    return f"`tab{doctype}`.name in ({values})"


def brand_query(user=None):
    return query_condition(BRAND, user)


def branch_query(user=None):
    return query_condition(BRANCH, user)


def team_query(user=None):
    return query_condition(TEAM, user)
