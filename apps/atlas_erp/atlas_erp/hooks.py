app_name = "atlas_erp"
app_title = "ATLASERP"
app_publisher = "ATLASERP"
app_description = "Simple business workflows for Morocco and African markets"
app_email = ""
app_license = "GNU General Public License (v3)"
required_apps = ["erpnext"]
app_logo_url = "/assets/atlas_erp/images/atlas-mark.svg"
app_home = "/atlas"

# The ERP engine supplies the single ATLASERP launcher entry. This companion
# app adds the experience and branding without adding a duplicate product icon.
add_to_apps_screen = []
after_install = ["atlas_erp.branding.apply_branding", "atlas_erp.setup_install.install_roles", "atlas_erp.checkout_install.install_fields"]
before_migrate = "atlas_erp.setup_install.install_roles"
after_migrate = ["atlas_erp.branding.apply_branding", "atlas_erp.setup_install.install_roles", "atlas_erp.checkout_install.install_fields"]
boot_session = "atlas_erp.branding.boot_session"
doc_events = {
    "POS Profile": {"validate": "atlas_erp.pos_api.checkout.validate_profile"},
    "Sales Invoice": {"before_validate": "atlas_erp.pos_api.checkout.prepare_invoice",
                      "validate": "atlas_erp.pos_api.checkout.validate_invoice"},
    "POS Invoice": {"before_validate": "atlas_erp.pos_api.checkout.prepare_invoice",
                    "validate": "atlas_erp.pos_api.checkout.validate_invoice"},
}
update_website_context = "atlas_erp.branding.website_context"
web_include_css = ["/assets/atlas_erp/css/theme-v3.1.css", "/assets/atlas_erp/css/web-v3.1.css"]
web_include_js = ["/assets/atlas_erp/js/web-v3.1.js"]
app_include_css = ["/assets/atlas_erp/css/theme-v3.1.css", "/assets/atlas_erp/css/desk-v3.1.css"]
app_include_js = ["/assets/atlas_erp/js/brand-v3.1.js"]
website_context = {
    "favicon": app_logo_url,
    "splash_image": "/assets/atlas_erp/images/atlas-wordmark.svg",
}
website_route_rules = [
    {"from_route": "/atlas-pos", "to_route": "atlas_pos"},
    {"from_route": "/atlas-portal", "to_route": "atlas_portal"},
    {"from_route": "/atlas-menu", "to_route": "atlas_menu"},
    {"from_route": "/atlas-setup", "to_route": "atlas_setup"},
    {"from_route": "/atlas-about", "to_route": "atlas_about"},
    {"from_route": "/atlas-guide", "to_route": "atlas_guide"},
]

has_permission = {
    "Atlas Business Brand": "atlas_erp.business_access.record_permission",
    "Atlas Business Branch": "atlas_erp.business_access.record_permission",
    "Atlas Team Member": "atlas_erp.business_access.record_permission",
}
permission_query_conditions = {
    "Atlas Business Brand": "atlas_erp.business_access.brand_query",
    "Atlas Business Branch": "atlas_erp.business_access.branch_query",
    "Atlas Team Member": "atlas_erp.business_access.team_query",
}
