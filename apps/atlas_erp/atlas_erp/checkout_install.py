"""Additive checkout schema. No accounts, payment modes or invoices are created."""
def install_fields():
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

    create_custom_fields({
        "POS Profile": [
            dict(fieldname="atlas_checkout_section", label="ATLAS checkout", fieldtype="Section Break", insert_after="payments"),
            dict(fieldname="atlas_enable_tips", label="Enable staff tips", fieldtype="Check", default="0", insert_after="atlas_checkout_section"),
            dict(fieldname="atlas_tip_account", label="Staff-tip liability account", fieldtype="Link", options="Account", insert_after="atlas_enable_tips", depends_on="atlas_enable_tips", mandatory_depends_on="atlas_enable_tips"),
            dict(fieldname="atlas_tip_presets", label="Tip percentages", fieldtype="Data", default="5,10,15", insert_after="atlas_tip_account", description="Optional customer prompts, separated by commas. A custom amount and no tip are always available."),
            dict(fieldname="atlas_service_addon_group", label="Service add-on item group", fieldtype="Link", options="Item Group", insert_after="atlas_tip_presets", description="Only enabled, priced, non-stock sales items appear in the add-on chooser."),
            dict(fieldname="atlas_confirm_external_payments", label="Require external payment confirmation", fieldtype="Check", default="0", insert_after="atlas_service_addon_group", description="Cashiers confirm terminal/bank approval and enter a transaction reference. This does not connect to a payment processor."),
        ],
        "Sales Invoice": [dict(fieldname="atlas_tip_amount", label="Staff tip", fieldtype="Currency", options="currency", read_only=1, default="0", insert_after="payments")],
        "Sales Taxes and Charges": [dict(fieldname="atlas_is_tip", label="ATLAS staff tip", fieldtype="Check", read_only=1, hidden=1, default="0", insert_after="description")],
        "Sales Invoice Payment": [
            dict(fieldname="atlas_external_confirmed", label="External payment confirmed by cashier", fieldtype="Check", read_only=1, no_copy=1, default="0", insert_after="reference_no"),
            dict(fieldname="atlas_confirmed_amount", label="Externally confirmed amount", fieldtype="Currency", options="currency", read_only=1, no_copy=1, default="0", insert_after="atlas_external_confirmed"),
        ],
    }, update=True)
