"""Exercise launchpad access against the local Frappe database.

Run in the development container only:
docker compose exec app env/bin/python /workspace/scripts/check-permissions.py
Temporary users are rolled back; no business transactions are created.
"""

import os

import frappe

from atlas_erp.permissions import can_access
from atlas_erp.www.atlas import get_context


def main():
    os.chdir("sites")
    frappe.init(site=os.environ.get("ATLAS_SITE", "atlas.localhost"))
    frappe.connect()
    created_users = []
    try:
        frappe.set_user("Guest")
        assert not can_access()
        try:
            get_context(frappe._dict())
        except frappe.Redirect:
            assert frappe.local.flags.redirect_location.startswith("/login?")
        else:
            raise AssertionError("Guest could open launchpad")

        frappe.set_user("Administrator")
        admin_context = get_context(frappe._dict())
        assert admin_context.can_setup
        assert any(module["href"] == "/atlas-pos" for module in admin_context.modules)

        for user_type, roles in [("Website User", []), ("System User", ["Sales User"])]:
            frappe.set_user("Administrator")
            email = f"atlas-access-{frappe.generate_hash(length=10)}@example.invalid"
            frappe.get_doc({
                "doctype": "User", "email": email, "first_name": "ATLAS access check",
                "user_type": user_type, "send_welcome_email": 0,
                "roles": [{"role": role} for role in roles],
            }).insert(ignore_permissions=True)
            created_users.append(email)
            frappe.set_user(email)
            if user_type == "Website User":
                assert not can_access()
                try:
                    get_context(frappe._dict())
                except frappe.PermissionError:
                    pass
                else:
                    raise AssertionError("Website user could open internal workspace")
            else:
                assert can_access()
                context = get_context(frappe._dict())
                assert not context.can_setup
                assert any(module["href"] == "/desk/customer" for module in context.modules)
                assert not any(module["href"] == "/desk/journal-entry" for module in context.modules)
        print("PASS: guest, website user, administrator and sales-role access")
    finally:
        frappe.set_user("Administrator")
        frappe.db.rollback()
        for email in created_users:
            frappe.clear_cache(user=email)
        frappe.destroy()


if __name__ == "__main__":
    main()
