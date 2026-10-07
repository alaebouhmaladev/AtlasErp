"""Read-only register checks; never open, cancel or post a cashier session."""
from urllib.parse import quote

import frappe
from frappe import _

from atlas_erp.business_access import BRANCH, BRAND, assignments, can_manage, is_admin
from atlas_erp.permissions import can_access


def require_cashier_account():
    if not can_access() or not frappe.get_cached_value("User", frappe.session.user, "enabled"):
        frappe.throw(_("Sign in with an enabled internal account."), frappe.PermissionError)


def desk_link(doctype, name, permission="read"):
    if name and frappe.has_permission(doctype, permission, doc=name):
        return "/desk/" + frappe.scrub(doctype).replace("_", "-") + "/" + quote(name, safe="")
    return None


def profile_in_scope(profile):
    if is_admin():
        return True
    user = frappe.session.user
    # Native permissions AND explicit cashier assignment are required. An empty
    # users table is not treated as an ATLAS register assignment.
    if not frappe.has_permission("POS Profile", "read", doc=profile):
        return False
    if user not in {row.user for row in profile.applicable_for_users}:
        return False
    scopes = assignments()
    atlas_roles = set(frappe.get_roles()) & {
        "ATLAS Owner", "ATLAS Manager", "ATLAS Cashier", "ATLAS Waiter", "ATLAS Staff"
    }
    if scopes or atlas_roles:
        for scope in scopes:
            if scope.company != profile.company or scope.staff_role not in {"Owner", "Manager", "Cashier"}:
                continue
            branch = frappe.db.get_value(BRANCH, scope.branch, ["company", "warehouse", "brand", "disabled"], as_dict=True)
            if (branch and not branch.disabled and branch.company == profile.company
                    and branch.warehouse == profile.warehouse
                    and not frappe.db.get_value(BRAND, branch.brand, "disabled")):
                return True
        return False
    # Preserve existing, explicitly assigned native ERP operators. These are
    # governed by native record/user permissions, not ATLAS branch metadata.
    return True


def active_sessions(**filters):
    return frappe.get_all("POS Opening Entry", filters={
        "docstatus": 1, "status": "Open", "pos_closing_entry": ["in", ["", None]], **filters
    }, fields=["name", "pos_profile", "company", "user", "period_start_date"],
        order_by="period_start_date desc")


def inspect_register(profile, own_sessions=None):
    user = frappe.session.user
    checks = []
    manager = can_manage(profile.company)

    def add(code, label, passed, message, href=None, warning=False):
        checks.append({"code": code, "label": label, "passed": bool(passed),
                       "message": message, "href": href if not passed else None,
                       "blocking": not warning and not passed})

    profile_href = desk_link("POS Profile", profile.name, "write") if manager else None
    add("profile", _("Register enabled"), not profile.disabled,
        _("Enable this register in its POS profile."), profile_href)
    assigned = user in {row.user for row in profile.applicable_for_users}
    add("cashier", _("Cashier assignment"), assigned,
        _("Ask your manager to assign your account to this register."), profile_href)
    invoice_type = frappe.db.get_single_value("POS Settings", "invoice_type") or "Sales Invoice"
    operator_permissions = all(frappe.has_permission(dt, action) for dt, action in (
        ("POS Opening Entry", "create"), ("POS Opening Entry", "submit"),
        (invoice_type, "create"), (invoice_type, "submit")))
    add("permissions", _("Checkout permissions"), operator_permissions,
        _("Ask an administrator to review your opening and invoice permissions."))

    warehouse = frappe.db.get_value("Warehouse", profile.warehouse,
                                    ["company", "is_group", "disabled"], as_dict=True) if profile.warehouse else None
    add("warehouse", _("Stock warehouse"), warehouse and warehouse.company == profile.company
        and not warehouse.is_group and not warehouse.disabled,
        _("Choose an enabled stock warehouse belonging to this company."), profile_href)
    price_list = frappe.db.get_value("Price List", profile.selling_price_list,
                                    ["enabled", "selling", "currency"], as_dict=True) if profile.selling_price_list else None
    add("price_list", _("Selling prices"), price_list and price_list.enabled and price_list.selling,
        _("Choose an enabled selling price list."), profile_href)
    add("currency", _("Checkout currency"), bool(profile.currency),
        _("Choose the currency used at this register."), profile_href)
    add("payment_default", _("Default payment method"), bool(profile.payments)
        and sum(bool(row.default) for row in profile.payments) == 1,
        _("Configure payment methods and select exactly one default."), profile_href)
    for row in profile.payments:
        mode = frappe.db.get_value("Mode of Payment", row.mode_of_payment, ["enabled", "type"], as_dict=True)
        account_name = frappe.db.get_value("Mode of Payment Account", {
            "parent": row.mode_of_payment, "parenttype": "Mode of Payment", "company": profile.company
        }, "default_account")
        account = frappe.db.get_value("Account", account_name,
                                       ["company", "account_type", "is_group", "disabled"], as_dict=True) if account_name else None
        valid = (mode and mode.enabled and account and account.company == profile.company
                 and account.account_type in {"Cash", "Bank"} and not account.is_group and not account.disabled)
        add("payment:" + row.mode_of_payment, row.mode_of_payment, valid,
            _("Set an enabled Cash or Bank account for this company's payment method."),
            desk_link("Mode of Payment", row.mode_of_payment, "write") if manager else None)
    # Default cash change mapping may be inherited from Company, as in native POS.
    if any(frappe.db.get_value("Mode of Payment", p.mode_of_payment, "type") == "Cash" for p in profile.payments):
        change_name = profile.account_for_change_amount or frappe.db.get_value("Company", profile.company, "default_cash_account")
        change = frappe.db.get_value("Account", change_name,
                                     ["company", "account_type", "is_group", "disabled"], as_dict=True) if change_name else None
        add("change", _("Cash change"), change and change.company == profile.company
            and change.account_type == "Cash" and not change.is_group and not change.disabled,
            _("Choose this company's enabled Cash account for change."), profile_href)

    own_sessions = active_sessions(user=user) if own_sessions is None else own_sessions
    register_sessions = active_sessions(pos_profile=profile.name)
    own_here = [s for s in own_sessions if s.pos_profile == profile.name and s.company == profile.company]
    multiple = len(own_sessions) > 1 or len(register_sessions) > 1
    other_register = any(s.pos_profile != profile.name for s in own_sessions)
    other_cashier = any(s.user != user for s in register_sessions)
    add("session", _("Cashier session"), not (multiple or other_register or other_cashier),
        _("Multiple open sessions need a manager's review.") if multiple else
        _("Finish your session at the other register before opening this one.") if other_register else
        _("Another cashier has this register open. Ask your manager to arrange closing or handover."))

    blockers = sum(c["blocking"] for c in checks)
    state = "needs_setup" if blockers else "resume" if own_here else "ready"
    if not multiple and not other_register and other_cashier:
        state = "in_use"
    elif multiple or other_register:
        state = "session_conflict"
    checkout_href = "/desk/point-of-sale?atlas_profile=" + quote(profile.name, safe="") if not blockers else None
    session = own_here[0] if len(own_here) == 1 else None
    return {"name": profile.name, "company": profile.company, "currency": profile.currency,
            "warehouse": profile.warehouse, "price_list": profile.selling_price_list,
            "state": state, "blocker_count": blockers, "checks": checks,
            "checkout_href": checkout_href, "profile_href": profile_href,
            "session": {"name": session.name, "started_at": str(session.period_start_date),
                        "href": desk_link("POS Opening Entry", session.name)} if session else None}


@frappe.whitelist(methods=["GET"])
def overview():
    require_cashier_account()
    profiles = []
    if frappe.has_permission("POS Profile", "read"):
        # get_list applies native query/user permissions before inspecting records.
        for row in frappe.get_list("POS Profile", fields=["name"], order_by="name asc", limit_page_length=500):
            profile = frappe.get_doc("POS Profile", row.name)
            if profile_in_scope(profile):
                profiles.append(profile)
    own = active_sessions(user=frappe.session.user)
    return {"registers": [inspect_register(p, own) for p in profiles],
            "display_name": frappe.get_cached_value("User", frappe.session.user, "first_name"),
            "can_setup": is_admin() or any(s.staff_role == "Owner" for s in assignments()),
            "online_only": True}


@frappe.whitelist(methods=["GET"])
def register_context(pos_profile):
    """Re-check permission and setup on native POS handoff; no client-trusted company."""
    require_cashier_account()
    if not frappe.db.exists("POS Profile", pos_profile):
        frappe.throw(_("This register is not available to your account."), frappe.PermissionError)
    profile = frappe.get_doc("POS Profile", pos_profile)
    if not profile_in_scope(profile):
        frappe.throw(_("This register is not available to your account."), frappe.PermissionError)
    result = inspect_register(profile)
    if result["blocker_count"]:
        frappe.throw(_("This register needs attention. Return to ATLAS POS to review the checks."))
    return {"company": profile.company, "pos_profile": profile.name, "state": result["state"]}
