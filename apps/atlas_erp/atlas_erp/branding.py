"""Product identity configuration; never rename ERP schema or package IDs."""

import frappe

NAME = "ATLASERP"
MARK = "/assets/atlas_erp/images/atlas-mark.svg"
WORDMARK = "/assets/atlas_erp/images/atlas-wordmark.svg"


def apply_branding():
    """Apply product identity on install/migration and when called explicitly.

    Intentional product defaults, not business/company settings. Write only
    presentation fields: the setup wizard may not have supplied the mandatory
    system language/timezone yet. Cache invalidation follows below.
    """
    for doctype, values in {
        "System Settings": {"app_name": NAME, "default_app": "erpnext"},
        "Website Settings": {
            "app_name": NAME, "app_logo": WORDMARK, "splash_image": WORDMARK,
            "favicon": MARK, "title_prefix": NAME,
            "brand_html": '<img src="' + WORDMARK + '" alt="ATLASERP" width="180" height="40">',
            "footer_powered": '<a href="/atlas-about">ATLASERP</a>',
        },
    }.items():
        frappe.db.set_single_value(doctype, values)

    navbar = frappe.get_single("Navbar Settings")
    navbar.app_logo = WORDMARK
    # Keep business/admin actions and custom help entries. Put upstream credits
    # in the product About page instead of the framework's default About dialog.
    for item in navbar.help_dropdown:
        if item.item_label in {"About", "Frappe Support"}:
            item.hidden = 1
    for label, route in [("About ATLASERP", "/atlas-about"), ("ATLASERP guide", "/atlas-guide")]:
        if not any(item.item_label == label for item in navbar.help_dropdown):
            navbar.append("help_dropdown", {
                "item_label": label, "item_type": "Route", "route": route,
                "is_standard": 0,
            })
    navbar.save(ignore_permissions=True)

    # The companion's old launcher entry was removed; preserve the same product
    # landing page for users who had selected it as their personal default.
    frappe.db.set_value("User", {"default_app": "atlas_erp"}, "default_app", "erpnext")

    # Existing v17 sites may already have generated Desktop Icon records.
    # Preserve their IDs/references, updating only presentation fields.
    for icon in frappe.get_all("Desktop Icon", filters={"icon_type": "App"}, fields=["name", "app"]):
        if icon.app == "erpnext":
            frappe.db.set_value("Desktop Icon", icon.name, {
                "label": NAME, "logo_url": MARK, "link": "/atlas", "hidden": 0,
            })
        elif icon.app == "atlas_erp":
            frappe.db.set_value("Desktop Icon", icon.name, "hidden", 1)
        elif icon.app == "frappe":
            frappe.db.set_value("Desktop Icon", icon.name, {
                "label": "ATLASERP Administration", "logo_url": MARK,
            })
    if frappe.db.exists("Desktop Icon", "ERPNext Settings"):
        frappe.db.set_value("Desktop Icon", "ERPNext Settings", "label", "ATLASERP Settings")
    for doctype, name, title in [
        ("Sidebar", "ERPNext Integrations", "Business integrations"),
        ("Workspace Sidebar", "ERPNext Settings", "ATLASERP Settings"),
        ("Workspace", "ERPNext Settings", "ATLASERP Settings"),
    ]:
        if frappe.db.exists("DocType", doctype) and frappe.db.exists(doctype, name):
            frappe.db.set_value(doctype, name, "title", title)
    for doctype, fieldname, attribute, value in [
        ("Item", "is_stock_item", "description", "ATLASERP will make a stock ledger entry for each transaction of this item. Keep unchecked for non-stock or service items."),
        ("Employee Group Table", "user_id", "label", "ATLASERP User ID"),
    ]:
        if frappe.db.exists("DocType", doctype):
            frappe.db.set_value("DocField", {"parent": doctype, "fieldname": fieldname}, attribute, value)
            frappe.clear_cache(doctype=doctype)
    frappe.clear_cache()


def boot_session(bootinfo):
    """Brand display metadata while keeping app IDs, permissions and docks."""
    for app in bootinfo.get("app_data", []):
        if app.get("app_name") == "frappe":
            app["app_title"] = "ATLASERP Administration"
            app["app_logo_url"] = MARK
        elif app.get("app_name") == "atlas_erp":
            app["on_apps_screen"] = False
    bootinfo.atlas_brand = {"name": NAME, "mark": MARK, "home": "/atlas"}


def website_context(context):
    context.app_name = NAME
    context.favicon = MARK
    context.splash_image = WORDMARK
    # Login's controller sets context.logo separately from website defaults.
    if context.get("for_test") == "login.html":
        context.logo = WORDMARK
        context.login_name_placeholder = "Email or Administrator"
