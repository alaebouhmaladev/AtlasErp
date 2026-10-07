"""Staging-only transaction tests. All fixture documents/postings roll back.

Run in the bench: ATLAS_CHECK_SITE=atlas-onboarding.localhost
env/bin/python apps/erpnext/scripts/check-pos-checkout.py
"""
import os
import frappe


def reject(fn, message):
    try:
        fn()
    except frappe.ValidationError:
        return
    raise AssertionError(message() if callable(message) else message)


def main():
    site = os.environ["ATLAS_CHECK_SITE"]
    if site != "atlas-onboarding.localhost":
        raise SystemExit("Transaction fixtures are restricted to the isolated onboarding site.")
    os.chdir("sites")
    frappe.init(site=site)
    frappe.connect()
    frappe.set_user("Administrator")
    tracked = ("Account", "Item", "Item Price", "POS Profile", "Mode of Payment", "Sales Invoice",
               "POS Invoice", "POS Opening Entry", "POS Closing Entry", "GL Entry", "Stock Ledger Entry")
    before = {dt: frappe.db.count(dt) for dt in tracked}
    try:
        from atlas_erp.pos_api import checkout
        from erpnext.controllers.sales_and_purchase_return import make_return_doc
        base = frappe.get_doc("POS Profile", "Street Pizza - Maarif - Demo POS")
        tax_account = frappe.db.get_value("Account", {"company": base.company, "account_type": "Tax",
            "root_type": "Liability", "is_group": 0, "disabled": 0}, "name")
        assert tax_account, "The staging company needs a native tax ledger for the VAT fixture"
        liability_root = frappe.db.get_value("Account", {"company": base.company, "root_type": "Liability", "is_group": 1}, "name")
        asset_root = frappe.db.get_value("Account", {"company": base.company, "root_type": "Asset", "is_group": 1}, "name")
        tip = frappe.get_doc({"doctype": "Account", "account_name": "ATLAS test staff tips", "company": base.company,
            "parent_account": liability_root, "is_group": 0}).insert()
        bank = frappe.get_doc({"doctype": "Account", "account_name": "ATLAS test bank", "company": base.company,
            "parent_account": asset_root, "account_type": "Bank", "is_group": 0}).insert()
        card = frappe.get_doc({"doctype": "Mode of Payment", "mode_of_payment": "ATLAS test external card", "type": "Bank",
            "accounts": [{"company": base.company, "default_account": bank.name}]}).insert()
        group = frappe.get_doc({"doctype": "Item Group", "item_group_name": "ATLAS test service add-ons",
            "parent_item_group": frappe.db.get_value("Item Group", {"lft": 1}, "name")}).insert()
        stock_uom = frappe.db.get_value("Item", {}, "stock_uom")
        item = frappe.get_doc({"doctype": "Item", "item_code": "ATLAS-TEST-SERVICE", "item_name": "Test service",
            "stock_uom": stock_uom, "item_group": group.name, "is_stock_item": 0, "is_sales_item": 1}).insert()
        frappe.get_doc({"doctype": "Item Price", "item_code": item.name, "price_list": base.selling_price_list,
            "price_list_rate": 100, "currency": base.currency}).insert()
        profile = frappe.copy_doc(base)
        profile.name = "ATLAS test checkout register"
        profile.atlas_enable_tips = 1
        profile.atlas_tip_account = tip.name
        profile.atlas_service_addon_group = group.name
        profile.atlas_confirm_external_payments = 1
        profile.set("applicable_for_users", [{"user": "Administrator", "default": 0}])
        profile.append("payments", {"mode_of_payment": card.name, "default": 0})
        profile.insert()
        assert checkout.context(profile.name)["tips_enabled"]
        addons = checkout.service_addons(profile.name)
        assert len(addons) == 1 and addons[0]["item_code"] == item.name and addons[0]["rate"] == 100
        bad = frappe.copy_doc(profile)
        bad.atlas_tip_account = bank.name
        reject(lambda: checkout.validate_profile(bad), "Asset account accepted for staff tips")
        bad.atlas_tip_account = None
        reject(lambda: checkout.validate_profile(bad), "Missing tip account accepted")
        reject(lambda: checkout.presets("5,NaN"), "Non-finite tip preset accepted")
        opening = frappe.get_doc({"doctype": "POS Opening Entry", "company": profile.company,
            "pos_profile": profile.name, "user": "Administrator", "period_start_date": frappe.utils.now_datetime(),
            "balance_details": [{"mode_of_payment": base.payments[0].mode_of_payment, "opening_amount": 0}]}).insert()
        opening.submit()

        def invoice(tip_amount=10, cash_amount=40, card_amount=90, confirmed=True):
            doc = frappe.get_doc({"doctype": "Sales Invoice", "company": profile.company, "pos_profile": profile.name,
                "customer": profile.customer, "is_pos": 1, "update_stock": 0, "disable_rounded_total": 1,
                "posting_date": frappe.utils.today(), "atlas_tip_amount": tip_amount,
                "items": [{"item_code": item.name, "qty": 1, "rate": 100}], "apply_discount_on": "Net Total"})
            doc.set_missing_values()
            doc.set("taxes", [])
            doc.append("taxes", {"charge_type": "On Net Total", "account_head": tax_account,
                "description": "STAGING test VAT 20%", "rate": 20, "cost_center": doc.cost_center})
            for row in doc.payments:
                row.amount = card_amount if row.mode_of_payment == card.name else cash_amount
                if row.mode_of_payment == card.name:
                    row.reference_no = "STAGING-only-approved-001"
                    row.atlas_external_confirmed = int(confirmed)
                    row.atlas_confirmed_amount = card_amount if confirmed else 0
            return doc

        missing = invoice(confirmed=False)
        reject(lambda: missing.insert(), "Unconfirmed external tender accepted")
        mismatch = invoice()
        mismatch.payments[-1].atlas_confirmed_amount = 1
        reject(lambda: mismatch.insert(), "Stale terminal amount confirmation accepted")
        excess = invoice(cash_amount=0, card_amount=131)
        reject(lambda: excess.insert(), lambda: "Non-cash overpayment accepted: " + str({
            "total": excess.grand_total, "rounded": excess.rounded_total,
            "payments": [(r.mode_of_payment, r.amount) for r in excess.payments]}))
        discount = invoice()
        discount.apply_discount_on = "Grand Total"
        discount.discount_amount = 1
        reject(lambda: discount.insert(), "Tip was discounted by a grand-total discount")
        no_tax = invoice()
        no_tax.taxes_and_charges = None
        no_tax.set("taxes", [])
        checkout.prepare_invoice(no_tax)
        assert len(no_tax.taxes) == 1 and no_tax.taxes[0].atlas_is_tip, "Tip introduced an unrelated default VAT template"
        sale = invoice().insert()
        assert float(sale.grand_total) == 130 and float(sale.atlas_tip_amount) == 10
        sale.submit()
        gl = frappe.get_all("GL Entry", filters={"voucher_type": "Sales Invoice", "voucher_no": sale.name, "is_cancelled": 0},
                            fields=["account", "debit", "credit"])
        assert abs(sum(float(r.debit) - float(r.credit) for r in gl)) < .000001
        assert sum(float(r.credit) for r in gl if r.account == tip.name) == 10
        assert sum(float(r.debit) for r in gl if r.account == bank.name) == 90
        assert sale.payments[-1].reference_no == "STAGING-only-approved-001"
        print("PASS: 100 service + 20 VAT + 10 tip = 130; cash 40 + card 90; balanced native ledger credits tips to liability")

        refund = make_return_doc("Sales Invoice", sale.name)
        refund.posting_date = frappe.utils.today()
        refund.update_stock = 0
        for row in refund.payments:
            if row.mode_of_payment == card.name and row.amount:
                row.reference_no = "STAGING-only-refund-001"
                row.atlas_external_confirmed = 1
                row.atlas_confirmed_amount = row.amount
        refund.insert()
        assert float(refund.atlas_tip_amount) == -10
        refund.submit()
        reversal = frappe.get_all("GL Entry", filters={"voucher_type": "Sales Invoice", "voucher_no": refund.name, "is_cancelled": 0},
                                  fields=["account", "debit", "credit"])
        assert sum(float(r.debit) for r in reversal if r.account == tip.name) == 10
        over_refund = make_return_doc("Sales Invoice", sale.name)
        over_refund.atlas_tip_amount = -1
        reject(lambda: checkout.prepare_invoice(over_refund), "Tip refunded more than once")
        print("PASS: native full refund reverses staff-tip liability; repeated tip refund is rejected")

        # Company/role boundaries are enforced on the extension APIs themselves.
        frappe.set_user("Guest")
        try:
            checkout.context(profile.name)
            raise AssertionError("Guest checkout context accepted")
        except frappe.PermissionError:
            pass
        frappe.set_user("Administrator")
    finally:
        frappe.db.rollback()
        assert before == {dt: frappe.db.count(dt) for dt in tracked}, "Staging fixture documents survived rollback"
        frappe.destroy()
    print("PASS: fixture records and ledger postings rolled back; no live financial records touched")


if __name__ == "__main__":
    main()
