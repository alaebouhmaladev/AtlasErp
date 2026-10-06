"""Read-only regression against the demo POS profile; never inserts or submits documents."""
import os
from unittest.mock import patch

import frappe


def main():
    site = os.environ["ATLAS_CHECK_SITE"]
    os.chdir("sites")
    frappe.init(site=site)
    frappe.connect()
    frappe.set_user("Administrator")
    try:
        from erpnext.accounts.doctype.sales_invoice.services.pos import POSService

        profile = frappe.get_doc("POS Profile", "Street Pizza - Maarif - Demo POS")
        account = frappe.db.get_value(
            "Mode of Payment Account",
            {"parent": "Street Pizza Demo Cash", "company": profile.company},
            "default_account",
        )
        assert account == "Cash - SPD"
        assert frappe.db.get_value("Account", account, "company") == profile.company
        before = {dt: frappe.db.count(dt) for dt in (
            "Sales Invoice", "POS Invoice", "POS Opening Entry", "POS Closing Entry", "GL Entry"
        )}

        for doctype in ("Sales Invoice", "POS Invoice"):
            invoice = frappe.get_doc({
                "doctype": doctype, "company": "ATLAS BITES", "is_pos": 1,
                "pos_profile": profile.name, "items": [],
                "account_for_change_amount": account,
            })
            invoice.set_missing_values()
            assert invoice.company == profile.company
            assert invoice.payments[0].account == account
            assert invoice.customer == profile.customer
            assert invoice.currency == "MAD"
            assert frappe.db.get_value("Account", invoice.debit_to, "company") == profile.company

        # A profile without an explicit change account must use its own company's cash default.
        profile.account_for_change_amount = None
        original_get_doc = frappe.get_doc

        def get_doc(*args, **kwargs):
            if args and args[0] == "POS Profile":
                return profile
            return original_get_doc(*args, **kwargs)

        invoice = frappe.get_doc({
            "doctype": "Sales Invoice", "company": "ATLAS BITES", "is_pos": 1,
            "pos_profile": profile.name, "items": [],
        })
        with patch("frappe.get_doc", side_effect=get_doc):
            POSService(invoice).set_pos_fields()
        assert invoice.company == profile.company
        assert invoice.account_for_change_amount == account
        assert invoice.payments[0].account == account

        # Validation preserves user-entered values and does not rebuild the payment rows.
        invoice.apply_discount_on = "Net Total"
        payment_rows = [row.as_dict() for row in invoice.payments]
        with patch("frappe.get_doc", side_effect=get_doc):
            POSService(invoice).set_pos_fields(for_validate=True)
        assert invoice.apply_discount_on == "Net Total"
        assert [row.as_dict() for row in invoice.payments] == payment_rows
        assert before == {dt: frappe.db.count(dt) for dt in before}
        print("PASS: profile company, cash/change/receivable accounts, both invoice types and validation; no documents posted")
    finally:
        frappe.db.rollback()
        frappe.destroy()


if __name__ == "__main__":
    main()
