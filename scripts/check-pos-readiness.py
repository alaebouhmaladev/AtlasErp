"""Read-only live regression; optional rolled-back access fixtures on staging only."""
import os
from unittest.mock import patch

import frappe

from atlas_erp.pos_api.readiness import inspect_register, overview, register_context
from atlas_erp.www.atlas_pos import get_context


def denied(fn):
    try:
        fn()
    except frappe.PermissionError:
        return
    raise AssertionError("Expected permission denial")


def main():
    site = os.environ["ATLAS_CHECK_SITE"]
    os.chdir("sites")
    frappe.init(site=site)
    frappe.connect()
    temporary_users = []
    counts = {dt: frappe.db.count(dt) for dt in (
        "Company", "Item", "Item Price", "POS Profile", "Sales Invoice", "POS Invoice",
        "POS Opening Entry", "POS Closing Entry", "GL Entry", "Stock Ledger Entry")}
    try:
        frappe.set_user("Guest")
        denied(overview)
        denied(lambda: register_context("Street Pizza - Maarif - Demo POS"))
        try:
            get_context(frappe._dict())
        except frappe.Redirect:
            assert "atlas-pos" in frappe.local.flags.redirect_location
        else:
            raise AssertionError("Guest page must redirect")
        frappe.set_user("Administrator")
        profile = frappe.get_doc("POS Profile", "Street Pizza - Maarif - Demo POS")
        result = inspect_register(profile)
        assert any(c["code"] == "payment:Street Pizza Demo Cash" and c["passed"] for c in result["checks"])
        assert "default_account" not in str(result)  # raw accounting rows never returned
        assert any(r["name"] == profile.name for r in overview()["registers"])
        denied(lambda: register_context("Does not exist"))

        # In-memory cases exercise the exact same live checks without posting.
        original_get_value = frappe.db.get_value
        def missing_mapping(doctype, *args, **kwargs):
            if doctype == "Mode of Payment Account":
                return None
            return original_get_value(doctype, *args, **kwargs)
        with patch.object(frappe.db, "get_value", side_effect=missing_mapping):
            broken = inspect_register(profile, [])
        assert not broken["checkout_href"]
        assert any(c["code"].startswith("payment:") and c["blocking"] for c in broken["checks"])

        assigned_profile = frappe.copy_doc(profile)
        assigned_profile.name = profile.name
        assigned_profile.set("applicable_for_users", [{"user": "Administrator", "default": 1}])
        own = frappe._dict(name="read-only-fixture", user="Administrator", company=profile.company,
                           pos_profile=profile.name, period_start_date=frappe.utils.now_datetime())
        with patch("atlas_erp.pos_api.readiness.active_sessions", return_value=[]):
            ready = inspect_register(assigned_profile, [])
        assert ready["state"] == "ready", ready
        with patch("atlas_erp.pos_api.readiness.active_sessions", return_value=[own]):
            resumed = inspect_register(assigned_profile, [own])
        assert resumed["state"] == "resume" and resumed["checkout_href"]
        for days in (-1, 1):
            dated = frappe._dict(own)
            dated.period_start_date = frappe.utils.add_to_date(own.period_start_date, days=days)
            with patch("atlas_erp.pos_api.readiness.active_sessions", return_value=[dated]):
                stale = inspect_register(assigned_profile, [dated])
            assert stale["state"] == "needs_closing" and not stale["checkout_href"]
            assert any(c["code"] == "session_date" and c["blocking"] for c in stale["checks"])
            assert "pos_opening_entry=read-only-fixture" in stale["closing_href"]
            original_get_doc = frappe.get_doc
            def selected_profile(*args, **kwargs):
                if args[:2] == ("POS Profile", profile.name):
                    return assigned_profile
                return original_get_doc(*args, **kwargs)
            with patch("atlas_erp.pos_api.readiness.active_sessions", return_value=[dated]), patch(
                    "frappe.get_doc", side_effect=selected_profile):
                try:
                    register_context(profile.name)
                except frappe.ValidationError:
                    pass
                else:
                    raise AssertionError("Outdated shift must not reach checkout through the context API")
            with patch("atlas_erp.pos_api.readiness.active_sessions", return_value=[dated]), patch(
                    "frappe.has_permission", return_value=False):
                restricted = inspect_register(assigned_profile, [dated])
            assert restricted["closing_href"] is None
        other = frappe._dict(own)
        other.user = "another-cashier@example.invalid"
        with patch("atlas_erp.pos_api.readiness.active_sessions", return_value=[other]):
            in_use = inspect_register(assigned_profile, [])
        assert in_use["state"] == "in_use" and not in_use["checkout_href"]
        assert other.user not in str(in_use)
        elsewhere = frappe._dict(own)
        elsewhere.pos_profile = "Other register"
        with patch("atlas_erp.pos_api.readiness.active_sessions", return_value=[]):
            conflict = inspect_register(assigned_profile, [elsewhere])
        assert conflict["state"] == "session_conflict" and not conflict["checkout_href"]
        with patch("atlas_erp.pos_api.readiness.active_sessions", return_value=[own, own]):
            conflict = inspect_register(assigned_profile, [own, own])
        assert conflict["state"] == "session_conflict"

        if os.environ.get("ATLAS_READINESS_FIXTURES") == "1":
            assert site == "atlas-onboarding.localhost", "Fixture writes are staging-only"
            for user_type in ("Website User", "System User"):
                frappe.set_user("Administrator")
                email = "atlas-register-" + frappe.generate_hash(length=12) + "@example.invalid"
                frappe.get_doc({"doctype": "User", "email": email, "first_name": "Register test",
                    "user_type": user_type, "send_welcome_email": 0,
                    "roles": [] if user_type == "Website User" else [{"role": "Accounts User"}]}).insert(ignore_permissions=True)
                temporary_users.append(email)
                frappe.set_user(email)
                if user_type == "Website User":
                    denied(overview)
                else:
                    assert overview()["registers"] == []  # broad native read alone is insufficient
                    denied(lambda: register_context(profile.name))
                    frappe.set_user("Administrator")
                    profile.append("applicable_for_users", {"user": email, "default": 1})
                    profile.save(ignore_permissions=True)
                    frappe.set_user(email)
                    permitted = overview()["registers"]
                    assert len(permitted) == 1 and permitted[0]["name"] == profile.name
                    assert permitted[0]["profile_href"] is None
                    assert not any(c["href"] for c in permitted[0]["checks"])
                    # A forged branch/company assignment cannot extend native access.
                    with patch("atlas_erp.pos_api.readiness.assignments", return_value=[
                        frappe._dict(company="Other company", branch="Other branch", staff_role="Cashier")]):
                        assert overview()["registers"] == []
                        denied(lambda: register_context(profile.name))
                    with patch("atlas_erp.pos_api.readiness.assignments", return_value=[]), patch(
                        "atlas_erp.pos_api.readiness.frappe.get_roles", return_value=["Sales User", "ATLAS Cashier"]):
                        assert overview()["registers"] == []  # disabled/unassigned ATLAS staff
            frappe.set_user("Administrator")
            frappe.db.rollback()
        assert counts == {dt: frappe.db.count(dt) for dt in counts}
        print("PASS: register checks, missing cash mapping, current-day resume, old/future shift blocking and scoped closing link, busy/conflicting sessions, guest denial; no business records posted")
        if temporary_users:
            print("PASS: website/unassigned/assigned native users and ATLAS branch/company denials; fixtures rolled back")
    finally:
        frappe.set_user("Administrator")
        frappe.db.rollback()
        for user in temporary_users:
            frappe.clear_cache(user=user)
        frappe.destroy()


if __name__ == "__main__":
    main()
