"""Checkout extensions use native invoice totals and ledger posting.

External confirmation records a cashier's statement, never a processor receipt.
Tips are voluntary charges payable to staff; this module never pays out funds.
"""
import math

import frappe
from frappe import _
from frappe.utils import cint, flt

from atlas_erp.pos_api.readiness import profile_in_scope, require_cashier_account


def checked_profile(name):
    require_cashier_account()
    profile = frappe.get_doc("POS Profile", name)
    if profile.disabled or not profile_in_scope(profile):
        frappe.throw(_("You cannot use this register."), frappe.PermissionError)
    return profile


def tip_account(profile):
    if not profile.get("atlas_tip_account"):
        frappe.throw(_("Choose the company's staff-tip liability account before enabling tips."))
    account = frappe.db.get_value("Account", profile.get("atlas_tip_account"),
        ["name", "company", "root_type", "is_group", "disabled", "account_type", "account_currency"], as_dict=True)
    currency = frappe.get_cached_value("Company", profile.company, "default_currency")
    if (not account or account.company != profile.company or account.root_type != "Liability"
            or account.is_group or account.disabled or account.account_type in {"Payable", "Receivable"}
            or (account.account_currency or currency) != currency or profile.currency != currency):
        frappe.throw(_("Choose an enabled staff-tip liability account in this company's currency."
                       " It must be a ledger account without a required party."))
    return account.name


def presets(value):
    try:
        values = [float(v.strip()) for v in (value or "5,10,15").split(",")]
        if len(values) > 5 or any(not math.isfinite(v) or v <= 0 or v > 100 for v in values):
            raise ValueError
    except (ValueError, TypeError):
        frappe.throw(_("Enter up to five tip percentages between 0 and 100, separated by commas."))
    return list(dict.fromkeys(values))


def validate_profile(doc, method=None):
    presets(doc.get("atlas_tip_presets"))
    if doc.get("atlas_enable_tips"):
        tip_account(doc)


@frappe.whitelist(methods=["GET"])
def context(pos_profile):
    profile = checked_profile(pos_profile)
    invoice_type = frappe.db.get_single_value("POS Settings", "invoice_type") or "Sales Invoice"
    enabled = bool(profile.get("atlas_enable_tips")) and invoice_type == "Sales Invoice"
    return {
        "pos_profile": profile.name, "company": profile.company, "currency": profile.currency,
        "tips_enabled": enabled, "tip_account": tip_account(profile) if enabled else None,
        "tip_presets": presets(profile.get("atlas_tip_presets")),
        "addons_enabled": bool(profile.get("atlas_service_addon_group")),
        "confirm_external": bool(profile.get("atlas_confirm_external_payments")),
    }


@frappe.whitelist(methods=["GET"])
def service_addons(pos_profile, search=""):
    profile = checked_profile(pos_profile)
    group = profile.get("atlas_service_addon_group")
    if not group:
        return []
    from frappe.utils.nestedset import get_descendants_of
    from erpnext.stock.get_item_details import get_item_details

    groups = [group, *get_descendants_of("Item Group", group)]
    items = frappe.get_list("Item", filters={"disabled": 0, "is_sales_item": 1,
        "is_stock_item": 0, "has_variants": 0, "item_group": ["in", groups]},
        or_filters={"item_code": ["like", "%" + str(search)[:80] + "%"],
                    "item_name": ["like", "%" + str(search)[:80] + "%"]},
        fields=["item_code", "item_name", "stock_uom"], order_by="item_name", limit_page_length=50)
    result = []
    for item in items:
        price = get_item_details({"doctype": "Sales Invoice", "company": profile.company,
            "currency": profile.currency, "selling_price_list": profile.selling_price_list,
            "price_list_currency": profile.currency, "conversion_rate": 1, "plc_conversion_rate": 1,
            "customer": profile.customer, "pos_profile": profile.name, "is_pos": 1,
            "item_code": item.item_code, "qty": 1, "uom": item.stock_uom,
            "transaction_date": frappe.utils.today(), "ignore_pricing_rule": 1})
        if flt(price.get("price_list_rate")) > 0:
            result.append({**item, "uom": item.stock_uom,
                "rate": price.price_list_rate, "currency": profile.currency})
    return result


def prepare_invoice(doc, method=None):
    marked = [row for row in doc.get("taxes", []) if row.get("atlas_is_tip")]
    amount = flt(doc.get("atlas_tip_amount"),
                 (doc.precision("atlas_tip_amount") or 2) if doc.doctype == "Sales Invoice" else 2)
    if not math.isfinite(amount):
        frappe.throw(_("Enter a valid tip amount."))
    if not amount and not marked:
        return
    if doc.doctype != "Sales Invoice" or not doc.is_pos or doc.is_consolidated:
        frappe.throw(_("ATLAS tips currently require a direct POS Sales Invoice."))
    profile = checked_profile(doc.pos_profile)
    if doc.company != profile.company or doc.currency != profile.currency:
        frappe.throw(_("The invoice must use the register's company and currency."))
    # Native returns copy the original metadata and negate Actual charge rows.
    if doc.is_return and amount > 0 and len(marked) == 1 and marked[0].tax_amount < 0:
        amount = flt(marked[0].tax_amount, doc.precision("atlas_tip_amount") or 2)
    if doc.is_return:
        account = return_tip_account(doc, amount)
    else:
        if amount < 0 or (amount and not profile.get("atlas_enable_tips")):
            frappe.throw(_("Tips must be enabled for this register and cannot be negative."))
        account = tip_account(profile) if amount else None
    if amount and doc.apply_discount_on == "Grand Total" and (
            flt(doc.discount_amount) or flt(doc.additional_discount_percentage)):
        frappe.throw(_("Apply the discount to Net Total before adding a tip. Staff tips cannot be discounted."))
    doc.atlas_tip_amount = amount
    doc.set("taxes", [row for row in doc.get("taxes", []) if not row.get("atlas_is_tip")])
    if not amount:
        return
    # Preserve normal tax-template rows before appending the last, non-taxable tip.
    if not doc.get("taxes") and (doc.taxes_and_charges or profile.taxes_and_charges):
        from erpnext.accounts.services.taxes import TaxService
        doc.taxes_and_charges = doc.taxes_and_charges or profile.taxes_and_charges
        TaxService(doc).set_taxes()
    doc.append("taxes", {"charge_type": "Actual", "account_head": account,
        "description": _("Staff tip"), "tax_amount": amount, "cost_center": doc.cost_center,
        "included_in_print_rate": 0, "atlas_is_tip": 1})


def return_tip_account(doc, amount):
    if not doc.return_against or amount > 0:
        frappe.throw(_("A tip refund must refer to its original sale and use a negative amount."))
    # Serialize tip refunds against the original sale, including concurrent requests.
    frappe.db.sql("select name from `tabSales Invoice` where name=%s for update", doc.return_against)
    original = frappe.get_doc("Sales Invoice", doc.return_against)
    rows = [r for r in original.taxes if r.get("atlas_is_tip")]
    if (original.docstatus != 1 or original.is_return or original.company != doc.company
            or original.currency != doc.currency or len(rows) != 1):
        frappe.throw(_("The original sale has no refundable ATLAS tip."))
    returned = frappe.db.sql("""select coalesce(sum(atlas_tip_amount), 0) from `tabSales Invoice`
        where docstatus=1 and is_return=1 and return_against=%s and name!=%s for update""",
        (original.name, doc.name or ""))[0][0]
    if abs(amount) + abs(flt(returned)) > flt(original.atlas_tip_amount) + 0.000001:
        frappe.throw(_("The tip refund exceeds the original sale's remaining tip."))
    return rows[0].account_head


def validate_invoice(doc, method=None):
    rows = [r for r in doc.get("taxes", []) if r.get("atlas_is_tip")]
    amount = flt(doc.get("atlas_tip_amount"))
    if amount and (len(rows) != 1 or rows[0] != doc.taxes[-1]
            or abs(flt(rows[0].tax_amount_after_discount_amount) - amount) > 0.000001):
        frappe.throw(_("The staff-tip charge must match the tip amount and remain the last charge."))
    if not doc.get("is_pos") or not doc.get("pos_profile") or doc.get("is_consolidated"):
        return
    profile = frappe.get_cached_doc("POS Profile", doc.pos_profile)
    if not doc.is_return:
        if any(flt(row.amount) < 0 for row in doc.payments):
            frappe.throw(_("Sale payment amounts cannot be negative. Use a return invoice for refunds."))
        total = flt(doc.grand_total if cint(doc.disable_rounded_total) else doc.rounded_total or doc.grand_total)
        loyalty = flt(doc.get("loyalty_amount")) / (flt(doc.conversion_rate) or 1)
        due = total - loyalty - flt(doc.write_off_amount) - flt(doc.total_advance)
        non_cash = sum(flt(row.amount) for row in doc.payments if
                       frappe.get_cached_value("Mode of Payment", row.mode_of_payment, "type") != "Cash")
        if non_cash > due + 0.000001:
            frappe.throw(_("Card and bank payments cannot exceed the amount due. Return overpayment as cash change only."))
    if profile.get("atlas_confirm_external_payments"):
        checked_profile(profile.name)
        for payment in doc.get("payments", []):
            payment_type = frappe.get_cached_value("Mode of Payment", payment.mode_of_payment, "type")
            if payment_type == "Bank" and flt(payment.amount):
                if (not payment.get("atlas_external_confirmed") or not (payment.reference_no or "").strip()
                        or abs(flt(payment.get("atlas_confirmed_amount")) - flt(payment.amount)) > 0.000001):
                    frappe.throw(_("Confirm the external payment/refund and enter its transaction reference for {0}.")
                                 .format(payment.mode_of_payment))
