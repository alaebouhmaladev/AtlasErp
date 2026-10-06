import hashlib
import re

import frappe
from frappe.model.document import Document
from atlas_erp.business_access import BRAND, BRANCH, TEAM, ROLES, check_manage


def identity(*parts):
    return hashlib.sha256("\0".join(str(p).strip().casefold() for p in parts).encode()).hexdigest()


class BusinessRecord(Document):
    def validate(self):
        check_manage(self.company)
        old = self.get_doc_before_save()
        if old and old.company != self.company:
            frappe.throw("A saved record cannot move to another legal company.")
        if self.doctype == BRAND:
            if self.business_type not in {"Restaurant", "Retail"}:
                frappe.throw("Choose Restaurant or Retail.")
            self.brand_name = (self.brand_name or "").strip()
            if not self.brand_name:
                frappe.throw("Enter a brand name.")
            if not re.fullmatch(r"#[0-9a-fA-F]{6}", self.accent_color or ""):
                frappe.throw("Choose a six-digit hex brand colour.")
            if self.logo and not self.logo.startswith(("/files/", "/private/files/")):
                frappe.throw("Upload the logo through the file picker.")
            self.identity_key = identity(self.company, self.brand_name)
        elif self.doctype == BRANCH:
            self.branch_name = (self.branch_name or "").strip()
            self.code = (self.code or "").strip().upper()
            if not self.branch_name or not re.fullmatch(r"[A-Z0-9-]{2,20}", self.code):
                frappe.throw("Enter a branch name and a 2–20 character code using letters, digits or hyphens.")
            brand = frappe.get_doc(BRAND, self.brand)
            if brand.company != self.company or brand.disabled:
                frappe.throw("Choose an enabled brand belonging to this company.")
            warehouse = frappe.get_doc("Warehouse", self.warehouse)
            if warehouse.company != self.company or warehouse.is_group or warehouse.disabled:
                frappe.throw("Choose an enabled stock warehouse belonging to this company.")
            other = frappe.db.get_value(BRANCH, {"warehouse": self.warehouse, "name": ["!=", self.name or ""]})
            if other:
                frappe.throw("This warehouse already belongs to another branch.")
            if old and (old.brand != self.brand or old.warehouse != self.warehouse or old.code != self.code):
                frappe.throw("A saved branch cannot change brand, warehouse or branch code.")
            self.identity_key = identity(self.company, self.code)
        else:
            branch = frappe.get_doc(BRANCH, self.branch)
            if branch.company != self.company or (branch.disabled and self.enabled):
                frappe.throw("Choose an enabled branch belonging to this company.")
            user = frappe.get_doc("User", self.user)
            if user.name in {"Guest", "Administrator"} or user.user_type != "System User" or not user.enabled:
                frappe.throw("Choose an enabled internal staff account.")
            if self.staff_role not in ROLES:
                frappe.throw("Choose a supported staff role.")
            if frappe.db.exists(TEAM, {"user": self.user, "company": ["!=", self.company]}):
                frappe.throw("Use a separate staff account for another legal company.")
            if old and (old.user != self.user or old.branch != self.branch):
                frappe.throw("A saved assignment cannot change its account or branch.")
            self.identity_key = identity(self.branch, self.user)

    def on_update(self):
        if self.doctype == TEAM:
            self.sync_roles()

    def on_trash(self):
        if self.doctype == TEAM:
            frappe.throw("Disable a staff assignment instead of deleting it.")

    def sync_roles(self):
        user = frappe.get_doc("User", self.user)
        wanted = {"ATLAS " + r.staff_role for r in frappe.get_all(
            TEAM, filters={"user": self.user, "enabled": 1}, fields=["staff_role"])}
        # Keep an internal account without granting business-data permissions.
        # Frappe otherwise converts it to a Website User when access is disabled.
        wanted.add("ATLAS Staff")
        user.roles = [r for r in user.roles if not r.role.startswith("ATLAS ") or r.role in wanted]
        existing = {r.role for r in user.roles}
        for role in wanted - existing:
            user.append("roles", {"role": role})
        user.save(ignore_permissions=True)
        frappe.clear_cache(user=self.user)
