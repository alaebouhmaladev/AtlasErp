"""Business setup/permission integration checks, restricted to a disposable site."""
import os
import uuid

import frappe


def deny(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except frappe.PermissionError:
        return
    raise AssertionError("Forbidden request was allowed")


def invalid(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except frappe.ValidationError:
        return
    raise AssertionError("Invalid request was allowed")


def main():
    site = os.environ.get("ATLAS_TEST_SITE", "")
    if not site.startswith("atlas-onboarding") or not site.endswith(".localhost"):
        raise SystemExit("Use a disposable atlas-onboarding*.localhost site only.")
    os.chdir("sites")
    frappe.init(site=site)
    frappe.connect()
    frappe.in_test = True
    from atlas_erp.business_setup import save_brand, save_branch, assign_staff, overview, set_staff_enabled
    from atlas_erp.business_access import BRAND, BRANCH, TEAM
    from frappe.client import get as api_get
    suffix = uuid.uuid4().hex[:8]
    users = []
    try:
        frappe.set_user("Administrator")
        # Normally seeded by ERPNext's first-run setup wizard.
        if not frappe.db.exists("Warehouse Type", "Transit"):
            frappe.get_doc({"doctype": "Warehouse Type", "name": "Transit"}).insert()
        companies = []
        for i in range(2):
            c = frappe.get_doc({"doctype": "Company", "company_name": f"Onboarding demo {suffix}-{i}",
                               "abbr": f"{suffix[:3]}{i}", "country": "Morocco", "default_currency": "MAD",
                               "create_chart_of_accounts_based_on": "Standard Template", "chart_of_accounts": "Standard"}).insert()
            companies.append(c.name)
        brand = save_brand(companies[0], "Demo <brand>")["name"]
        assert save_brand(companies[0], "Demo <brand>")["created"] is False
        branch = save_branch(companies[0], brand, "Centre", "CASA-01")["name"]
        assert save_branch(companies[0], brand, "Centre", "CASA-01")["created"] is False
        second = save_branch(companies[0], brand, "Other branch", "CASA-02")["name"]
        other_brand = save_brand(companies[1], "Other company")["name"]
        foreign = save_branch(companies[1], other_brand, "Foreign branch", "RABAT-01")["name"]
        before = frappe.db.count("Warehouse")
        frappe.db.savepoint("invalid_branch")
        invalid(save_branch, companies[0], other_brand, "Invalid", "BAD-01")
        frappe.db.rollback(save_point="invalid_branch")
        assert frappe.db.count("Warehouse") == before
        invalid(save_brand, companies[0], "Bad colour", accent_color="javascript:bad")
        invalid(save_branch, companies[0], brand, "Wrong warehouse", "BAD-02",
                warehouse=frappe.get_doc(BRANCH, foreign).warehouse)
        role_users = {}
        for role in ["Owner", "Manager", "Cashier", "Waiter"]:
            email = f"atlas-{role.lower()}-{suffix}@example.invalid"
            result = assign_staff(branch, email, role, role)
            users.append(email)
            assert assign_staff(branch, email, role, role)["created"] is False
            role_users[role] = (email, result["name"])
        assert frappe.db.count(TEAM, {"branch": branch}) == 4
        print("PASS: brands, branches, separate warehouses and retry safety")
        for role, (email, _) in role_users.items():
            frappe.set_user(email)
            visible = overview()
            names = {r.name for r in visible["branches"]}
            assert branch in names and foreign not in names
            assert (second in names) == (role == "Owner")
            assert not frappe.has_permission("Journal Entry", "read")
            assert not frappe.has_permission(BRANCH, "read", doc=frappe.get_doc(BRANCH, foreign))
            deny(api_get, BRANCH, foreign)
            if role != "Owner":
                assert not frappe.has_permission(BRANCH, "read", doc=frappe.get_doc(BRANCH, second))
                deny(save_brand, companies[0], "Forbidden")
                deny(assign_staff, second, f"x-{suffix}@example.invalid", "Bad", "Owner")
            else:
                assert save_brand(companies[0], "Owner-created")["created"]
                deny(save_brand, companies[1], "Forbidden")
                invalid(set_staff_enabled, role_users["Owner"][1], 0)
        print("PASS: company/branch isolation and direct API role restrictions")
        frappe.set_user("Administrator")
        cashier, assignment = role_users["Cashier"]
        set_staff_enabled(assignment, 0)
        invalid(assign_staff, foreign, cashier, "Cashier", "Cashier")
        frappe.set_user(cashier)
        try:
            assert not frappe.get_list(BRANCH)
        except frappe.PermissionError:
            pass
        assert not frappe.has_permission(BRANCH, "read", doc=frappe.get_doc(BRANCH, branch))
        frappe.set_user("Administrator")
        set_staff_enabled(assignment, 1)
        frappe.set_user(cashier)
        assert frappe.has_permission(BRANCH, "read", doc=frappe.get_doc(BRANCH, branch))
        frappe.set_user("Guest")
        deny(overview)
        print("PASS: disabling/re-enabling staff access and guest denial")
    finally:
        frappe.set_user("Administrator")
        frappe.db.rollback()
        for user in users:
            frappe.clear_cache(user=user)
        frappe.destroy()


if __name__ == "__main__":
    main()
