"""Idempotent, scoped setup endpoints; stock and accounting remain in ERPNext."""
import frappe
from frappe.utils import validate_email_address
from atlas_erp.permissions import can_access
from atlas_erp.business import identity
from atlas_erp.business_access import BRAND, BRANCH, TEAM, ROLES, assignments, can_manage, check_manage, is_admin


def require_internal():
    if not can_access():
        frappe.throw("Sign in with an internal account.", frappe.PermissionError)


@frappe.whitelist()
def overview():
    require_internal()
    scopes = assignments()
    companies = frappe.get_list("Company", filters={"is_group": 0},
                               fields=["name", "country", "default_currency"], limit_page_length=200) if is_admin() else [
        frappe._dict(name=n, **frappe.db.get_value("Company", n, ["country", "default_currency"], as_dict=True))
        for n in sorted({r.company for r in scopes})]
    return {
        "companies": companies,
        "brands": frappe.get_list(BRAND, fields=["name", "company", "brand_name", "business_type", "accent_color", "logo", "disabled"], limit_page_length=200),
        "branches": frappe.get_list(BRANCH, fields=["name", "company", "brand", "branch_name", "code", "city", "warehouse", "disabled"], limit_page_length=200),
        "team": frappe.get_list(TEAM, fields=["name", "company", "branch", "user", "staff_role", "enabled"], limit_page_length=200),
        "managed_companies": [c.name for c in companies if can_manage(c.name)],
        "is_admin": is_admin(),
    }


@frappe.whitelist(methods=["POST"])
def save_brand(company, brand_name, business_type="Restaurant", accent_color="#123e36"):
    require_internal()
    check_manage(company)
    if business_type not in {"Restaurant", "Retail"}:
        frappe.throw("Choose Restaurant or Retail.")
    key = identity(company, brand_name)
    existing = frappe.db.get_value(BRAND, {"identity_key": key})
    if existing:
        return {"name": existing, "created": False}
    doc = frappe.get_doc(dict(doctype=BRAND, company=company, brand_name=brand_name,
                             business_type=business_type, accent_color=accent_color)).insert()
    return {"name": doc.name, "created": True}


@frappe.whitelist(methods=["POST"])
def save_branch(company, brand, branch_name, code, city="", address="", warehouse=None):
    require_internal()
    check_manage(company)
    key = identity(company, code)
    existing = frappe.db.get_value(BRANCH, {"identity_key": key})
    if existing:
        doc = frappe.get_doc(BRANCH, existing)
        if doc.brand != brand or (warehouse and doc.warehouse != warehouse):
            frappe.throw("This branch code already exists with different details.")
        return {"name": doc.name, "created": False}
    if frappe.db.get_value(BRAND, brand, "company") != company:
        frappe.throw("The brand must belong to the selected company.")
    if not warehouse:
        warehouse_name = f"ATLAS {code.strip().upper()} {branch_name.strip()}"
        root = frappe.db.get_value("Warehouse", {"company": company, "is_group": 1, "parent_warehouse": ["is", "not set"]})
        doc = frappe.get_doc(dict(doctype="Warehouse", warehouse_name=warehouse_name,
                                 company=company, is_group=0, parent_warehouse=root)).insert(ignore_permissions=True)
        warehouse = doc.name
    doc = frappe.get_doc(dict(doctype=BRANCH, company=company, brand=brand,
                             branch_name=branch_name, code=code, warehouse=warehouse,
                             city=city, address=address)).insert()
    return {"name": doc.name, "created": True}


@frappe.whitelist(methods=["POST"])
def assign_staff(branch, email, first_name, staff_role):
    require_internal()
    branch_doc = frappe.get_doc(BRANCH, branch)
    check_manage(branch_doc.company)
    if staff_role not in ROLES:
        frappe.throw("Choose a supported staff role.")
    email = validate_email_address(email.strip().lower(), throw=True)
    if email in {"guest", "administrator"} or not first_name.strip():
        frappe.throw("Enter a staff email and name.")
    if frappe.db.exists("User", email):
        user = frappe.get_doc("User", email)
        unexpected = {r.role for r in user.roles} - {"All", "Guest", "Desk User", "ATLAS Staff", *["ATLAS " + r for r in ROLES]}
        if unexpected or user.user_type != "System User" or not user.enabled:
            frappe.throw("This account has other permissions or is disabled. Ask an administrator to review it.")
        existing_companies = {r.company for r in frappe.get_all(TEAM, filters={"user": email}, fields=["company"])}
        if existing_companies - {branch_doc.company}:
            frappe.throw("Use a separate staff account for another legal company.")
    else:
        user = frappe.get_doc(dict(doctype="User", email=email, first_name=first_name.strip(),
                                  enabled=1, user_type="System User", send_welcome_email=0,
                                  roles=[{"role": "ATLAS " + staff_role}])).insert(ignore_permissions=True)
    key = identity(branch, email)
    existing = frappe.db.get_value(TEAM, {"identity_key": key})
    if existing:
        doc = frappe.get_doc(TEAM, existing)
        doc.staff_role = staff_role
        doc.enabled = 1
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.get_doc(dict(doctype=TEAM, company=branch_doc.company, branch=branch,
                                 user=email, staff_role=staff_role, enabled=1)).insert(ignore_permissions=True)
    return {"name": doc.name, "user": email, "created": not bool(existing),
            "activation": "Account created. Configure password/reset access through User management; email is not configured."}


@frappe.whitelist(methods=["POST"])
def set_staff_enabled(name, enabled):
    require_internal()
    if str(enabled) not in {"0", "1"}:
        frappe.throw("Choose enabled or disabled.")
    doc = frappe.get_doc(TEAM, name)
    check_manage(doc.company)
    if doc.user == frappe.session.user and doc.staff_role == "Owner" and str(enabled) != "1":
        others = [r for r in assignments() if r.company == doc.company and r.staff_role == "Owner" and r.branch != doc.branch]
        if not others:
            frappe.throw("Ask another owner or administrator to disable your last owner assignment.")
    doc.enabled = 1 if str(enabled) == "1" else 0
    doc.save(ignore_permissions=True)
    return {"name": doc.name, "enabled": doc.enabled}
