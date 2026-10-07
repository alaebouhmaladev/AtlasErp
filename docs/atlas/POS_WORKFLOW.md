# Next milestone — Shared checkout for counter and table service

Started 2026-10-06 after business setup release `27f4575e30`. The user selected
both counter/takeaway sales and restaurant table service. This document records
the source inspection and the bounded implementation sequence. Checkout is not
yet delivered as the Android/offline/table workflow. Release 0.5.0 adds guided
split tenders, configured tips and non-stock service add-ons to the native online
checkout; see [payments and service workflows](PAYMENTS_AND_SERVICES.md).

## Findings from the checked-in ERPNext engine

- `POS Settings.invoice_type` is site-wide and defaults to **Sales Invoice**.
  `erpnext/accounts/doctype/pos_settings/pos_settings.json` also offers POS Invoice.
  Do not change this silently for an existing site or assume it is branch-specific.
- Sales Invoice submission calls `update_stock_ledger()` when `update_stock=1`
  and `make_gl_entries()` in `sales_invoice.py:on_submit`. This is the initial
  candidate for a small pilot because the posting path is directly inspectable.
- POS Invoice mode consolidates through POS Invoice Merge Log and POS Closing
  Entry. `consolidate_pos_invoices` queues closing batches of ten or more invoices;
  smaller batches execute directly. The interface must distinguish submitted
  receipts from completed consolidation and expose failures/retry status.
- POS Opening Entry rejects an already-open profile and an already-assigned
  cashier. Use a POS Profile per register, rather than assuming every cashier in
  one branch can simultaneously open the same profile.
- POS Profile validates company links, requires payment methods with company cash
  or bank accounts, and requires exactly one default payment method. It provides
  price list, warehouse, stock validation and rate/discount/warehouse-change flags.
- Native opening validation checks profile company and enabled user, but does not
  enforce the new ATLAS branch assignment. ATLAS validation and read/query scopes
  must cover profiles, openings, invoices, returns and closing entries.
- Some native whitelisted POS helpers, including `get_pos_profile_data`, retrieve
  documents without an explicit record permission check. Audit and guard these
  endpoints as well as generic document APIs before enabling operational staff
  access; hiding a link or adding a DocType role alone is insufficient.

These are source findings, not a substitute for ledger/stock transaction tests.
The installed development engine remains the recorded evaluation baseline.

## Small tasks in delivery order

| Task | User result | Completion evidence |
| --- | --- | --- |
| POS-01 — Branch/register configuration | Owner selects branch, register, catalog, MAD price list, payment accounts and allowed cashiers | Repeat saves stable; cross-company references rejected; native POS API guards verified |
| POS-02 — Small catalog | Owner adds a product/menu item, unit, barcode and selling price | Uniqueness, disabled items, precision and branch price-list checks |
| POS-03 — Opening | Cashier opens an allowed register with starting cash | Concurrent/repeated opening cannot create another session; disabled staff denied |
| POS-04 — Shared cash checkout | Search/scan, cart, quantities, server totals, payment and change | Durable request identity prevents duplicate sales; failure retains cart; restricted rates/discounts enforced |
| POS-05 — Receipt and returns | Print/reprint and manager-approved partial/full refund | Original-sale link; quantity/tender limits; stock and ledger reconcile |
| POS-06 — Closing | Cashier counts cash; manager reviews variance | Opening + cash sales − cash refunds = expected till balance; consolidation failures visible |
| REST-01 — Tables and open orders | Waiter opens a table, adds items and sends to kitchen | Branch/table ownership, concurrent edits and repeated sends tested; unpaid order does not post a sale |
| REST-02 — Kitchen workflow | Kitchen sees new tickets and marks preparation/ready status | Each send creates one ticket; later additions and cancellations remain traceable |
| REST-03 — Settle table | Cashier brings the open order into the shared checkout | One completed invoice per settlement; settled table released; failed payment keeps order open |

Counter mode enters the shared cart directly. Table mode maintains an unpaid order
before entering that same checkout. Existing ERPNext calculations and posting
remain the financial source of truth. Recipe/ingredient consumption, separate bills,
table transfers, staff tip allocation and automatic payment-provider integrations follow as separate
tasks after the basic counter and table paths pass.

## Initial permission contract

Owners configure their company. Managers review branch sales, approve exceptions,
refunds and closing. Cashiers operate only assigned registers and permitted
payments; they cannot edit unrestricted prices or browse financial ledgers.
Waiters manage table orders in assigned branches and cannot settle/refund sales
unless separately assigned as a cashier. Kitchen access will need its own role.
Enforce every restriction on the server, including native ERP endpoints.

## Business checks before claiming this milestone complete

Run on the isolated staging site with fictional data and reviewed tax examples:

1. Two companies, two branches, distinct cashiers and registers; UI and direct API
   requests cannot select another scope or impersonate another cashier.
2. Opening cash 100 MAD; one 50 MAD cash sale with tender 100/change 50; partial
   refund 20 MAD; expected closing cash 130 MAD, with matching invoice/payment
   records and reviewed stock/ledger effects.
3. Same sale request twice produces one invoice; invalid/failed submission leaves
   no partial ledger/stock posting and allows a safe retry.
4. Closing with fewer than ten and at least ten POS Invoices exercises direct and
   queued consolidation if that mode is selected. Do not declare closing finished
   while the background job is queued or failed.
5. Two waiters editing one table cannot overwrite each other's orders; repeated
   kitchen send and repeated settlement produce no duplicate ticket or invoice.
6. Desktop/touch/keyboard checks, then receipt printing on the chosen hardware.

Printer/scanner models, connectivity needs, accountant-approved taxes and receipt
requirements still need pilot input. They do not block configuration and server
permission work, but they are required for the corresponding acceptance checks.
