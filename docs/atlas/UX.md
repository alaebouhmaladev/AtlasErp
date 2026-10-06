# UI and UX direction

Principle: make the next daily action obvious. The initial `/atlas` page is a
working launchpad; the operational forms still use ERPNext. A new checkout is a
separate milestone, not represented by a visual mockup as completed software.

## Retail roles

- Cashier: open session, search/scan, sell, print/reprint permitted receipts,
  request approved refunds and close the till.
- Manager: manage catalog/prices, approve exceptions, receive/count stock,
  monitor shop results and reconcile daily cash.
- Owner: company/branch access, finance review and overall operations.
- Accountant: postings, taxes, reconciliation, reporting and close periods.

## Navigation and visual system

Use a calm green palette, neutral surfaces, clear typography, generous spacing
and visible status text. Keep checkout, products, stock, purchasing and daily
closing close to the retail user. Show advanced finance tools by role rather
than overwhelming every cashier with the whole ERP.

The launchpad has responsive cards, keyboard focus, a skip link and RTL layout
support. Next passes need French/Arabic translations, real screen-reader and
tablet verification, and dedicated phone behavior. RTL layout alone does not
mean Arabic translation is complete.

## Checkout design requirements

1. Fast scan/search entry with predictable focus; barcode scanner behaves like a keyboard.
2. Cart shows product, quantity, price, discount and final total clearly.
3. Totals use configured currency precision and taxes from ERPNext.
4. Payment step shows amount due, tendered amount and change where applicable.
5. Duplicate taps/retries cannot post a second invoice or payment.
6. Success shows receipt and next-sale action; failure preserves the unsaved cart.
7. Returns reference the original sale and require the appropriate permissions.
8. Session closing explains expected cash and variance; manager approval is explicit.

## Reusable states

Every custom screen needs loading, empty, no permission, error/retry, saved,
submitted and cancelled states. Label a draft clearly. Explain validation errors
near the relevant field. Hide prohibited actions and enforce them on the server.
Use confirmations for consequential operations such as submit/cancel/return,
while preserving the user's work on errors.

Offline selling is not delivered. The Android-first plan designs local persistence
and synchronization from the outset; the first development checkout can be online.
Offline cash is an explicit user requirement. Tested sale replay, price/tax drift,
permission, stock and reconciliation policies are a first commercial pilot gate. See
[MOBILE_POS.md](MOBILE_POS.md); offline cash and offline multi-device restaurant
collaboration are separate acceptance scopes.

Device setup uses Devices → Add device → Pair → Choose role → Test. Owners name
supported tablets, kitchen/customer screens and printers on the same shop router,
assign destinations and see connection status. Printer adapters are configurable.
A local hub coordinates shared restaurant orders; WAN loss, local-network loss
and hub failure each need an explicit state and safe recovery behavior.

## Usability review

Observe cashiers completing scan → payment → receipt and managers doing a return,
stock receipt and closing. Record completion, time, missteps and assistance; agree
targets after baseline sessions. Test touch targets, keyboard use, barcode focus,
long French/Arabic labels, 360px phones and common tablet sizes.
