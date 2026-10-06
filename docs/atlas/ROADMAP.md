# Product roadmap

The long-term system can serve many industries. The first complete product serves
**Moroccan retail shops and restaurants**, with Android tablets as the first native
POS target and iOS following later. It extends through tested industry and country packs.
No calendar deadline is assumed; phases advance when their exit criteria pass.

The Android/iOS delivery phases, restaurant scope, required offline cash, pilot hardware
and small implementation slices are recorded in [MOBILE_POS.md](MOBILE_POS.md).
This is planned work; the current deployed checkout still uses native ERP screens.

## Complete capability map

| Area | ERPNext reuse | ATLASERP work | Delivery |
| --- | --- | --- | --- |
| Foundation | Users, roles, company, warehouses, APIs | Branding, onboarding, navigation, operator roles | P0–P1 |
| Retail / POS | POS profiles, invoices, sessions and closing | Android tablet checkout, device/scanner/printer support, offline synchronization, iOS later | P2 / mobile phases 0–2, 6 |
| Restaurant | Catalog, customers, invoicing and stock engine | Meal choices, tables, waiters, kitchen workflow, split bills, ingredient/recipe stock | Mobile phases 1, 3–4 |
| Catalog | Items, UOM, variants, barcodes, prices | Fast retail entry, validated import, product search | P1 |
| Inventory | Warehouses, receipts, counts, transfers, batches | Branch workflows, low-stock actions, expiry views | P3 |
| Sales | Quotes, orders, deliveries, invoices, credits | Simplified screens and document templates | P2 / P5 |
| Buying | Suppliers, purchase orders, receipts, invoices | Replenishment and supplier workflows | P3 |
| Finance | Ledger, payments, reconciliation, receivables/payables | Morocco-validated chart/tax setup, accountant handoff | P4 |
| Morocco localization | Currency/country/translations, existing chart candidate | Identifiers, verified print formats, regulatory research | P1 / P4 |
| CRM integration | Customers/contacts and APIs | ATLASUSE mapping, handoff, retries and status | P5 |
| Management reports | Stock, sales and financial reports | Role dashboards, explainable KPIs, shop filters | P3–P5 |
| Projects / services | Projects, tasks, time and service invoicing | Service industry pack | P6 |
| Manufacturing | BOMs, planning, work orders, subcontracting | Industry-specific setup and guided workflows | P6 |
| Assets / maintenance | Fixed assets, depreciation, maintenance | Industry navigation and local accounting validation | P6 |
| HR / payroll | Evaluate separate compatible Frappe HR app | Country-validated HR/payroll pack | P6, separate release |
| Commerce / support | Evaluate available compatible apps | Store/portal/support integrations | P6, demand-led |
| African markets | Multi-currency, country records | Independent packs for named countries | P7 |
| Operations / hosting | Frappe sites, migrations, backups | Tenant onboarding, subscriptions, support operations | Release gate |

## P0 — Development foundation (started)

Deliver extension app, runtime, launchpad, documented roadmap and version audit.
Exit: fresh site boots, apps listed, login works, restricted users cannot open the
launchpad, navigation opens the right workflows, restart preserves data.

## P1 — Guided Moroccan shop setup

Start with one company, one shop, one warehouse and MAD; French first, Arabic and
English support designed from the start. Capture business identifiers as editable
data only after reviewing their definitions. Add shop owner, manager and cashier
roles; import products, prices and barcodes with preview/error reporting. Create
POS profile and session setup guidance. Do not silently choose tax settings.
Exit: a manager can configure a demo shop and a cashier can start a session with
only the permitted shop's products and prices.

## P2 — The retail transaction lifecycle

Build fast product/barcode search, cart, quantity changes, permitted discounts,
customer optionality, configured taxes and payment selection. Reuse ERPNext POS
posting. Include receipts, returns/credit handling and cash session closing;
consider stock accounting timing at POS consolidation. Verify cash first; record
card/mobile payments without claiming actual payment processing integrations.
Exit: sale → receipt → stock/accounting posting → refund → closing balances all
reconcile, including partial payments and rounding cases supported by the design.

## P3 — Stock, purchasing and shop management

Purchase → receive → supplier invoice → payment, stock counts/adjustments,
transfers, price updates and reorder workflow. Add reports by shop and period;
define sales/returns/gross margin/cash variance consistently with posted records.
Exit: retail replenishment and a daily management review work without spreadsheets.

## P4 — Verified Moroccan finance and documents

Work with a Moroccan accountant on charts, TVA configuration, invoice/receipt
fields, credit notes, reporting and exports. Validate applicable requirements for
the actual business regime. Track source/date/reviewer per requirement.
Exit: accountant reviews posted sample transactions and printed/exported documents;
no unresolved critical finance or compliance defects remain for the pilot scope.

## P5 — Pilot and ATLASUSE connection

Pilot with a small group of shops using real cashier tasks, then implement the
agreed CRM customer handoff. Measure task completion, mistakes and support needs.
Complete stable-version selection, staging, restore exercise and support runbook.
Exit: owners and cashiers sign off, accountant signs off, isolation and rollback
are demonstrated, production readiness checklist is complete.

## P6 — Broader business packs

Add wholesale/distribution, services/projects and manufacturing as separate
vertical releases. Evaluate HR/payroll, assets, commerce and support only when
the buyer need and compatible app/version are clear. Each pack gets its own
roles, onboarding, business lifecycle tests and local validation.

## P7 — Country-by-country African expansion

Choose the next countries through customer discovery. Research language,
currencies, fiscal/accounting regime, privacy, hosting and local payment providers.
Build and pilot one country pack at a time. Evaluate OHADA only where applicable;
do not generalize Moroccan tax rules or OHADA rules to all of Africa.

## Working cadence

For each small ticket: define the user task → inspect ERPNext behavior → implement
the thinnest extension → verify the full business path → demonstrate → update
backlog. Hold a milestone review before adding the next module. Prioritize retail
correctness and usability before expanding the feature list.
