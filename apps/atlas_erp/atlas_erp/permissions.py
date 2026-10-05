import frappe


def can_access():
    if frappe.session.user == "Guest":
        return False
    return frappe.get_cached_value("User", frappe.session.user, "user_type") == "System User"
