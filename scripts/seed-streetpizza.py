"""Populate Street Pizza master data in an explicitly marked demo company.

Run using the bench Python. ATLAS_SEED_SITE, ATLAS_MENU_PATH and
ATLAS_SEED_MODE=demo are required. It creates no sales, stock balances or users.
An existing real company is never renamed or reused by this importer.
"""
import html
import json
import os
from pathlib import Path

import frappe

COMPANY = "Street Pizza (Demo)"
ABBR = "SPD"
ROOT_GROUP = "Street Pizza Menu"
PRICE_LIST = "Street Pizza Website MAD"
PROFILE = "Street Pizza - Maarif - Demo POS"
CUSTOMER = "Street Pizza Walk-in (Demo)"
BRANCH_CODE = "CASA-MAARIF"


def ensure(doctype, filters, values):
    name = frappe.db.get_value(doctype, filters, "name")
    if name:
        return frappe.get_doc(doctype, name), False
    return frappe.get_doc({"doctype": doctype, **values}).insert(), True


def seed(menu):
    from atlas_erp.business_setup import save_brand, save_branch
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

    if os.environ.get("ATLAS_SEED_MODE") != "demo":
        raise RuntimeError("Only explicitly marked demo setup is supported. Real legal/tax data needs review.")
    assert menu["currency"] == "MAD" and len(menu["items"]) == 63
    assert len({x["item_code"] for x in menu["items"]}) == 63
    assert all(x["price_mad"] > 0 and x["detail_verified"] for x in menu["items"])
    if frappe.get_cached_doc("POS Settings").invoice_type != "Sales Invoice":
        frappe.throw("This demo requires the site's existing Sales Invoice POS mode. Do not change an active site's mode automatically.")
    for entry in menu["items"]:
        existing = frappe.db.get_value("Item", entry["item_code"], ["item_name", "item_group"], as_dict=True)
        if existing and (existing.item_name != entry["item_name"] or existing.item_group != "SP · " + entry["category"]):
            frappe.throw("An existing item code conflicts with the captured menu: " + entry["item_code"])
    # Install schema first: MariaDB DDL commits implicitly. Business records below
    # can then roll back together if any validation fails.
    create_custom_fields({"Item": [
        {"fieldname": "atlas_menu_options", "label": "ATLAS menu choices (source data)",
         "fieldtype": "Code", "options": "JSON", "insert_after": "description", "read_only": 1},
        {"fieldname": "atlas_menu_source", "label": "ATLAS menu source", "fieldtype": "Data",
         "insert_after": "atlas_menu_options", "read_only": 1},
    ]})
    business = menu["business"]
    # A country-specific address template is normally created by first-run setup.
    if not frappe.db.exists("Address Template", {"country": "Morocco"}):
        ensure("Address Template", {"country": "Morocco"}, {
            "country": "Morocco", "is_default": not bool(frappe.db.exists("Address Template", {"is_default": 1})),
            "template": "{{ address_line1 | e }}<br>{% if address_line2 %}{{ address_line2 | e }}<br>{% endif %}{{ city | e }}<br>{{ country | e }}",
        })
    # Fresh test sites have not run ERPNext's first-run setup wizard.
    for dt, label, values in [
        ("Warehouse Type", "Transit", {"name": "Transit"}),
        ("UOM", "Nos", {"uom_name": "Nos", "must_be_whole_number": 1}),
        ("Customer Group", "All Customer Groups", {"customer_group_name": "All Customer Groups", "is_group": 1}),
        ("Territory", "All Territories", {"territory_name": "All Territories", "is_group": 1}),
        ("Item Group", "All Item Groups", {"item_group_name": "All Item Groups", "is_group": 1}),
    ]:
        ensure(dt, {"name": label}, values)
    group, _ = ensure("Customer Group", {"name": "Street Pizza Customers"},
                      {"customer_group_name": "Street Pizza Customers", "parent_customer_group": "All Customer Groups"})
    territory, _ = ensure("Territory", {"name": "Street Pizza Casablanca"},
                          {"territory_name": "Street Pizza Casablanca", "parent_territory": "All Territories"})
    other = frappe.db.get_value("Company", {"abbr": ABBR}, "name")
    if other and other != COMPANY:
        frappe.throw("The demo company abbreviation is already used. No existing company will be changed.")
    company, _ = ensure("Company", {"name": COMPANY}, {
        "company_name": COMPANY, "abbr": ABBR, "country": "Morocco", "default_currency": "MAD",
        "create_chart_of_accounts_based_on": "Standard Template", "chart_of_accounts": "Standard",
        "phone_no": business["phone"], "website": business["website"],
    })
    if company.country != "Morocco" or company.default_currency != "MAD":
        frappe.throw("Existing demo company configuration does not match this dataset.")
    from erpnext.accounts.utils import get_fiscal_year
    from frappe.utils import today
    if not get_fiscal_year(today(), company=COMPANY, raise_on_missing=False):
        year = int(today()[:4])
        ensure("Fiscal Year", {"name": f"Street Pizza Demo {year}"}, {
            "year": f"Street Pizza Demo {year}", "year_start_date": f"{year}-01-01",
            "year_end_date": f"{year}-12-31", "companies": [{"company": COMPANY}],
        })
    brand = save_brand(COMPANY, business["display_name"], "Restaurant")["name"]
    branch = save_branch(COMPANY, brand, "Casablanca Maarif", BRANCH_CODE,
                         city=business["city"], address=business["address"])["name"]
    warehouse = frappe.db.get_value("Atlas Business Branch", branch, "warehouse")
    address, _ = ensure("Address", {"address_title": COMPANY, "address_type": "Billing"}, {
        "address_title": COMPANY, "address_type": "Billing", "address_line1": business["address"],
        "city": "Casablanca", "country": "Morocco", "phone": business["phone"], "is_primary_address": 1,
        "links": [{"link_doctype": "Company", "link_name": COMPANY}],
    })
    if not any(row.link_doctype == "Company" and row.link_name == COMPANY for row in address.links):
        frappe.throw("The existing demo address is linked to another business.")
    ensure("Item Group", {"name": ROOT_GROUP}, {
        "item_group_name": ROOT_GROUP, "parent_item_group": "All Item Groups", "is_group": 1,
    })
    category_groups = {}
    for category in dict.fromkeys(x["category"] for x in menu["items"]):
        name = "SP · " + category
        ensure("Item Group", {"name": name}, {"item_group_name": name, "parent_item_group": ROOT_GROUP})
        category_groups[category] = name
    price_list, _ = ensure("Price List", {"name": PRICE_LIST}, {
        "price_list_name": PRICE_LIST, "currency": "MAD", "selling": 1, "buying": 0, "enabled": 1,
    })
    if price_list.currency != "MAD" or not price_list.selling:
        frappe.throw("The Street Pizza price list must be a MAD selling price list.")
    for entry in menu["items"]:
        if frappe.db.exists("Item", entry["item_code"]):
            item = frappe.get_doc("Item", entry["item_code"])
            if item.item_name != entry["item_name"] or item.item_group != category_groups[entry["category"]]:
                frappe.throw("An existing item code conflicts with the captured menu: " + entry["item_code"])
        else:
            item = frappe.new_doc("Item")
            item.item_code = entry["item_code"]
            item.item_name = entry["item_name"]
            item.item_group = category_groups[entry["category"]]
            item.stock_uom = "Nos"
            item.is_stock_item = 0  # Recipes, opening stock and drink units are not supplied.
            item.is_sales_item = 1
            item.is_purchase_item = 0
            item.append("item_defaults", {"company": COMPANY, "default_warehouse": warehouse,
                                          "income_account": company.default_income_account})
        item.description = html.escape(entry["description"])
        if entry["options"]:
            choices = "; ".join(f"{g['label']} ({g['required_count']}): " + ", ".join(g["choices"])
                                for g in entry["options"])
            item.description += "<br>Choix obligatoires: " + html.escape(choices)
        item.atlas_menu_options = json.dumps(entry["options"], ensure_ascii=False)
        item.atlas_menu_source = menu["source_url"] + " · " + menu["captured_on"]
        item.save()
        prices = frappe.get_all("Item Price", filters={"item_code": item.name, "price_list": PRICE_LIST}, pluck="name")
        if len(prices) > 1:
            frappe.throw("Duplicate Street Pizza item prices need review: " + item.name)
        price = frappe.get_doc("Item Price", prices[0]) if prices else frappe.new_doc("Item Price")
        price.item_code = item.name
        price.price_list = PRICE_LIST
        price.uom = "Nos"
        price.price_list_rate = entry["price_mad"]
        price.save()
    customer, _ = ensure("Customer", {"customer_name": CUSTOMER}, {
        "customer_name": CUSTOMER, "customer_type": "Individual", "customer_group": group.name,
        "territory": territory.name, "default_currency": "MAD", "default_price_list": PRICE_LIST,
    })
    cash, _ = ensure("Mode of Payment", {"name": "Street Pizza Demo Cash"}, {
        "mode_of_payment": "Street Pizza Demo Cash", "type": "Cash", "enabled": 1,
        "accounts": [{"company": COMPANY, "default_account": company.default_cash_account}],
    })
    if not company.default_cash_account or not company.default_income_account:
        frappe.throw("The demo chart must provide cash and income accounts before a POS Profile is created.")
    if not any(r.company == COMPANY and r.default_account == company.default_cash_account for r in cash.accounts):
        frappe.throw("The demo cash method has conflicting account configuration.")
    receipt_name = "Street Pizza Demo Receipt"
    ensure("Print Format", {"name": receipt_name}, {
        "name": receipt_name, "doc_type": "Sales Invoice", "standard": "No", "custom_format": 1,
        "print_format_type": "Jinja", "html": """<style>.sp-receipt{font-family:sans-serif;max-width:340px;margin:auto;font-size:12px}.sp-receipt table{width:100%}.sp-receipt td{padding:4px 0}.sp-receipt h2{text-align:center}</style>
<div class="sp-receipt"><h2>Street Pizzeria Napoletana</h2><p>DEMONSTRATION — Non valable pour facturation fiscale</p>
<p>{{ doc.company | e }}<br>Angle Boulevard Roudani et Rue du Louvre, Maarif, Casablanca<br>0657572308 · streetpizza.ma</p>
<p>{{ doc.name | e }} · {{ doc.posting_date | e }}</p><table>{% for row in doc.items %}<tr><td>{{ row.qty }} × {{ row.item_name | e }}</td><td style="text-align:right">{{ row.get_formatted('amount') }}</td></tr>{% endfor %}</table>
<p>Total: {{ doc.get_formatted('grand_total') }}</p><p>Merci ! Les taxes et l'identité légale restent à valider pour l'exploitation réelle.</p></div>""",
    })
    profile, created = ensure("POS Profile", {"name": PROFILE}, {
        "name": PROFILE, "company": COMPANY, "customer": customer.name, "warehouse": warehouse,
        "company_address": address.name,
        "currency": "MAD", "selling_price_list": PRICE_LIST, "disabled": 0,
        "income_account": company.default_income_account, "expense_account": company.default_expense_account,
        "cost_center": company.cost_center, "write_off_account": company.default_expense_account,
        "write_off_cost_center": company.cost_center, "write_off_limit": 0,
        "account_for_change_amount": company.default_cash_account,
        "allow_rate_change": 0, "allow_discount_change": 0, "allow_warehouse_change": 0,
        "allow_partial_payment": 0, "update_stock": 0, "validate_stock_on_save": 0,
        "hide_unavailable_items": 0, "print_format": receipt_name,
        "payments": [{"mode_of_payment": cash.name, "default": 1}],
        "applicable_for_users": [{"user": "Administrator", "default": 1}],
        "item_groups": [{"item_group": ROOT_GROUP}],
    })
    if profile.company != COMPANY or profile.warehouse != warehouse or profile.selling_price_list != PRICE_LIST:
        frappe.throw("Existing demo POS Profile has conflicting business references.")
    if not profile.company_address:
        profile.company_address = address.name
        profile.save()
    return {"company": COMPANY, "brand": brand, "branch": branch, "warehouse": warehouse,
            "pos_profile": profile.name, "profile_created": created, "items": 63,
            "categories": len(category_groups), "price_list": PRICE_LIST, "mode": "demo"}


def main():
    site = os.environ.get("ATLAS_SEED_SITE")
    if not site:
        raise SystemExit("ATLAS_SEED_SITE is required")
    menu = json.loads(Path(os.environ["ATLAS_MENU_PATH"]).read_text())
    os.chdir("sites")
    frappe.init(site=site)
    frappe.connect()
    frappe.set_user("Administrator")
    try:
        result = seed(menu)
        frappe.db.commit()
        print(json.dumps(result))
    except Exception:
        frappe.db.rollback()
        raise
    finally:
        frappe.destroy()


if __name__ == "__main__":
    main()
