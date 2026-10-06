import frappe


def install_roles():
    for title in ("Owner", "Manager", "Cashier", "Waiter", "Staff"):
        name = "ATLAS " + title
        if not frappe.db.exists("Role", name):
            frappe.get_doc({"doctype": "Role", "role_name": name, "desk_access": 1}).insert(ignore_permissions=True)
