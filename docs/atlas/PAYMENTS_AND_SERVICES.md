# ATLAS checkout, NAPS and service businesses

Updated 2026-10-07. The user has a **NAPS TPE** and no online-payment partnership
yet. Retail and restaurants remain supported; barber/salon services extend the
same company, branch, register, catalog and accounting model.

## Release 0.5.0 — checkout software

The native online POS now has **Split payment**: custom portions or 2–20 equal
shares, allocating rounding remainders in currency minor units. Portions are
aggregated into the invoice's native payment rows. Cash overpayment is change;
card/bank overpayment is rejected. This creates **one invoice**, not independent
seat/item checks or separate receipts. Refunds use the native return workflow.
The in-flight submit guard prevents double taps; durable retry/idempotency and
offline cash remain separate release gates in the commerce backlog.

Each POS Profile has an **ATLAS checkout** section:

- **Require external payment confirmation**: an operator confirms the actual
  terminal/bank payment or refund and enters a transaction reference before
  completing the order. Confirmation records its amount; changing that amount
  requires another confirmation. The server checks these fields too. This is an
  audited cashier statement, not cryptographic verification of a NAPS charge.
  Bank-type modes are covered, including a configured external-card mode.
- **Enable staff tips**: optional percentages, custom amount and no tip. Tips
  require an enabled, non-group, non-party liability account of the same legal
  company and currency. They use a final native Actual charge, preserving native
  totals, receipt charge lines and GL posting. Grand Total discounts with tips
  are rejected; use Net Total discounts. Tips initially pool in the company's
  liability account; no barber allocations or payouts occur automatically.
- **Service add-on item group**: the chooser offers up to 50 enabled, priced,
  non-stock sales items from that group and descendants. Items enter the native
  cart with normal price, discount, tax and income-account calculation. This is
  not a required/min-max modifier engine, seat assignment or recipe system.

Tips support direct **POS Sales Invoice** mode only. They stay unavailable in
POS Invoice/consolidation mode until transfer/reversal metadata is tested.
Native returns negate copied tip charges; the operator can review the tip refund.
The server locks the original invoice and prevents cumulative submitted tip
refunds exceeding the original tip. Receipt printing/reprint remains native.
Country-specific tip tax treatment, staff distribution and payroll rules require
the merchant's reviewed accounting configuration; the switch starts off.

The additive installer creates Custom Fields only. It does not create company
accounts, staff payout destinations, payment methods, sales or register sessions,
and it does not turn on these options on existing POS Profiles.

## Using a NAPS terminal today

1. A manager configures a company Bank account and an external-card payment mode
   mapped to that account. Add it alongside Cash on the branch/register profile.
2. Enable **Require external payment confirmation** on that profile. Do not put
   card numbers, PINs or CVVs in a transaction-reference field.
3. On checkout, choose the cash/card portions. Charge each card portion on the
   TPE, then enter the approved receipt reference and confirm it in ATLAS.
4. Complete the invoice only after approval. A decline is not a paid sale. If a
   terminal charge succeeds but invoice submission fails, retain its reference
   and reconcile/retry the invoice; do not charge the customer again.
5. Reconcile card invoices to terminal settlement batches and bank deposits.
   Fees, refunds and settlement timing need reconciliation, rather than equating
   recorded card sales with deposited cash.

NAPS advertises [integrated POS amount/order-reference exchange and terminal
tipping](https://naps.ma/tpe/). Its public pages are not the integration protocol
for this merchant's terminal. Obtain the exact TPE model, supported SDK/protocol,
merchant integration activation, sandbox credentials and settlement/refund docs.
[TKpay publishes developer integration options](https://tkpay.ma/solutions/integrations)
as an agent of NAPS; eligibility for this existing merchant/TPE must be confirmed.
No merchant agreement is accepted or changed by this software release.

## Delivery sequence for the requested feature groups

| Task | Concrete result | Required acceptance evidence / dependency |
| --- | --- | --- |
| PAY-01 | Split tenders, equal shares and external-terminal confirmation | Minor-unit allocation, reference/amount guards, balanced native invoice; implemented in 0.5.0 |
| TIP-01 | Configurable voluntary tips with a liability balance | Tip totals, account/company/currency validation and refund cap; implemented in 0.5.0 for Sales Invoice mode |
| SERVICE-01 | Priced service add-ons | Scoped non-stock catalog and normal item posting; implemented in 0.5.0 |
| PAY-02 | Automatic NAPS terminal payment/refund | Exact terminal protocol/SDK and activated merchant integration; sandbox approve/decline/cancel/timeout; no fake success when device is offline |
| PAY-03 | Safe payment transaction journal | Durable identity per attempted charge, terminal transaction ID, amount/currency/order binding, recover unknown result before retry; webhook signature and replay tests where applicable |
| PAY-04 | Settlement matching | Invoice tenders → terminal batches → bank deposits, fees and refunds; mismatch queue and manager review |
| REST-08 / SQ-19 | Separate equal/item/seat bills | Shared order revision, remaining quantities/taxes/discounts, independent receipts and concurrent settlement; current split tenders alone do not fulfill this |
| TIP-02 | Staff tip allocation | Eligible staff, pooling/direct allocation, effective policy version and reversal tied to original receipt; staff-level liabilities reconcile to collected tips |
| STAFF-01 | Barber commissions and booth rent | Staff/contractor distinction, effective-dated rates, earning statement, rental receivables and deductions; never confuse customer invoice income with staff net earnings |
| PAYOUT-01 | Reviewed payout batches | Reconcile gross/fees/refunds/earnings/tips/rent, manager approval, account verification, exports and reversal; test duplicate/rejected requests |
| PAYOUT-02 | Automatic bank/provider payouts | Partner supports this merchant's subaccounts/beneficiaries and countries; sandbox and production certification before activation; payouts move only approved, eligible funds |
| BOOK-01 | Booking and cancellation policy | Staff/resource availability, reservation state, disclosed deposit/no-show policy and customer consent; preserve policy snapshot and changes |
| PAY-05 | Deposits | Hosted provider checkout, authenticated signed confirmation, refundable customer advance accounting and reconciliation to the final service invoice |
| PAY-06 | Card on file / no-show charge | Provider vault tokens and off-session merchant permissions, explicit customer consent, policy eligibility, notification/refund/dispute path; never store PAN/CVV or call a TPE receipt reference a saved card |

PAY-02, PAY-05, PAY-06 and PAYOUT-02 are **provider dependencies**, not enabled
features. A card-present NAPS contract does not establish online tokenization,
off-session charging or marketplace payouts. Digital wallets/reader support
depends on the exact terminal, acquiring configuration and country. The tablet
and local device hub must treat the terminal as a provider adapter; unsupported
card transactions cannot be accepted by an offline cash fallback.

Build PAY-03 before enabling automatic charging. Offline cash, register scope,
returns, daily/overnight shift policy, close reconciliation and device enrollment
stay prerequisite gates for a commercial Android pilot. Preserve the explicitly
protected live Street Pizza opening POS-OPE-2026-00002 and its 301 MAD sale.

## Verification / rollout

`node scripts/test-pos-checkout.mjs` verifies rounding, split coverage, cash change,
external confirmation, unknown/negative/non-finite tenders and the submit guard.
`scripts/check-pos-checkout.py` is restricted to the isolated onboarding site:
it tests native invoice/GL posting and tip reversal, account/preset validation,
external amount guards and service catalog, then rolls back its fixtures.
Staging/browser and live rollout evidence is recorded after those checks pass.
