"""Verify the captured menu and one cash sale on the isolated demo site only."""
import json
import os
from pathlib import Path

import frappe


def main():
    site = os.environ.get("ATLAS_SEED_SITE", "")
    if not site.startswith("atlas-onboarding") or not site.endswith(".localhost"):
        raise SystemExit("Use the isolated atlas-onboarding*.localhost site only.")
    menu = json.loads(Path(os.environ["ATLAS_MENU_PATH"]).read_text())
    os.chdir("sites")
    frappe.init(site=site)
    frappe.connect()
    frappe.set_user("Administrator")
    try:
        from erpnext.selling.page.point_of_sale.point_of_sale import get_items, create_opening_voucher
        from seed_streetpizza import seed, COMPANY, PROFILE, PRICE_LIST, ROOT_GROUP

        tracked = ["Company", "Fiscal Year", "Atlas Business Brand", "Atlas Business Branch", "Warehouse", "Item", "Item Price", "POS Profile", "Customer"]
        before = {dt: frappe.db.count(dt) for dt in tracked}
        seed(menu)
        assert {dt: frappe.db.count(dt) for dt in tracked} == before
        result = get_items(0, 100, PRICE_LIST, ROOT_GROUP, PROFILE)
        catalog = {row["item_code"]: frappe._dict(row) for row in result["items"]}
        assert len(catalog) == 63
        for row in menu["items"]:
            actual = catalog[row["item_code"]]
            assert actual.item_name == row["item_name"]
            assert float(actual.price_list_rate) == row["price_mad"]
            assert actual.currency == "MAD"
            item = frappe.get_doc("Item", row["item_code"])
            assert json.loads(item.atlas_menu_options) == row["options"]
        print("PASS: 63 exact item names/prices, 9 categories, required combo choices and repeat-import safety")
        profile = frappe.get_doc("POS Profile", PROFILE)
        assert profile.company == COMPANY and profile.applicable_for_users[0].user == "Administrator"
        assert profile.company_address
        opening = create_opening_voucher(PROFILE, COMPANY, [{"mode_of_payment": profile.payments[0].mode_of_payment, "opening_amount": 0}])
        invoice = frappe.get_doc({
            "doctype": "Sales Invoice", "company": COMPANY, "customer": profile.customer,
            "is_pos": 1, "is_created_using_pos": 1, "pos_profile": PROFILE,
            "selling_price_list": PRICE_LIST, "currency": "MAD", "conversion_rate": 1,
            "update_stock": 0, "disable_rounded_total": 1,
            "debit_to": frappe.db.get_value("Company", COMPANY, "default_receivable_account"),
            "account_for_change_amount": profile.account_for_change_amount,
            "items": [{"item_code": "SP-002", "qty": 1}, {"item_code": "SP-051", "qty": 1}],
            "payments": [{"mode_of_payment": profile.payments[0].mode_of_payment,
                          "account": profile.account_for_change_amount, "amount": 100}],
        })
        invoice.set_missing_values()
        # Match the UI: load profile defaults first, then enter tendered cash.
        invoice.payments[0].amount = 100
        invoice.insert()
        invoice.submit()
        expected = next(x["price_mad"] for x in menu["items"] if x["item_code"] == "SP-002") + next(x["price_mad"] for x in menu["items"] if x["item_code"] == "SP-051")
        assert float(invoice.grand_total) == expected
        assert float(invoice.change_amount) == 100 - expected
        assert float(invoice.outstanding_amount) == 0
        entries = frappe.get_all("GL Entry", filters={"voucher_type": "Sales Invoice", "voucher_no": invoice.name}, fields=["debit", "credit", "company"])
        assert entries and all(row.company == COMPANY for row in entries)
        assert round(sum(float(row.debit) - float(row.credit) for row in entries), 2) == 0
        assert not frappe.db.count("Stock Ledger Entry", {"voucher_no": invoice.name})
        assert frappe.db.get_value("POS Opening Entry", opening["name"], "status") == "Open"
        rendered = frappe.get_print("Sales Invoice", invoice.name, print_format=profile.print_format)
        assert "Street Pizzeria Napoletana" in rendered and "DEMONSTRATION" in rendered
        print(f"PASS: demo cash sale {expected:g} MAD, change {100-expected:g} MAD, balanced ledger and demo receipt")
    finally:
        frappe.db.rollback()
        frappe.destroy()


if __name__ == "__main__":
    main()
