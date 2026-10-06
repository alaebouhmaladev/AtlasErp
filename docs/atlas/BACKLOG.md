# Small development backlog

Status: **Development foundation deployed; business setup milestone verified on staging**.
The company/brand/branch/team implementation is documented in `ONBOARDING.md`.
Catalog, POS profiles and transaction workflows remain future tickets.
First vertical: retail and POS. Each ID is a bounded, independently reviewable task.

## Foundation tickets

| ID | Deliverable | Acceptance | Dependency / status |
| --- | --- | --- | --- |
| F01 | Inventory inherited fork/version/toolchain | Version, Python requirement and existing changes recorded | Done in architecture notes |
| F02 | Extension app with hooks/assets | App installs after ERPNext and registers app-launcher metadata | Done: installed apps and asset delivery verified |
| F03 | Local environment and setup commands | Fresh boot, login, restart persistence; no external DB port | Done for development site; business-data restore remains Q02 |
| F04 | Role-aware retail launchpad | Guest redirects; website user denied; responsive navigation reflects roles | Access/HTTP/desktop/phone checks passed; operational destinations await shop setup |
| F05 | Stable baseline assessment | Recorded supported pair, pinned versions and compatibility results | Before real pilot data |
| F06 | ATLASERP product branding | Sign-in/launcher/logos/settings/credits branded; authentication and roles preserved | Implemented; verification recorded in BRANDING.md |

## P1 — Shop setup, one piece at a time

### R01 — Retail process and permission specification
Interview/observe one shop owner and cashier. Document shop count, devices,
scanner/printer models, receipts, payments, connectivity and returns.
Acceptance: agreed sale/return/closing examples and an action-by-role matrix.
Depends on: none. Next product ticket.

### R02 — Company/shop onboarding
Guide company, country, currency, timezone, Retail domain, warehouse and POS profile setup using
existing documents. Show missing steps and resume progress.
Acceptance: fresh demo company configured without developer assistance; repeated
steps create no duplicates; setup never changes another company's configuration.
Depends on: F03, R01.

Implemented part: company selection/native Company creation, brands, branches,
dedicated warehouses and resumable team setup. POS profiles and country/accounting
review remain separate work; R02 is not yet the full cashier-ready onboarding gate.

### R03 — Retail roles and branch restrictions
Create reviewed role/permission fixtures for cashier, manager, owner and accountant.
Acceptance: cashier cannot access restricted ledgers, edit prices or another shop's
records through UI **or API**; manager exceptions are demonstrated.
Depends on: R01–R02.

Implemented part: ATLAS Owner/Manager/Cashier/Waiter business-metadata roles and
company/branch scope hooks. Operational ledger/price/POS permissions remain pending.

### R04 — Small catalog entry
Simple create/edit workflow for item, UOM, barcode and selling price.
Acceptance: unique barcode rules, disabled items, duplicate records and precision
are handled; items are searchable in the correct shop's POS profile.
Depends on: R02–R03.

### R05 — Catalog import
CSV template, dry-run preview, row errors and explicit import confirmation.
Acceptance: duplicate barcode, invalid UOM and missing prices do not silently
produce wrong records; retries do not create duplicate items.
Depends on: R04.

### R06 — POS profile and opening session
Guide cashier, warehouse, payment modes and opening cash.
Acceptance: correct session opened; unauthorized profile/shop rejected; open
sessions are handled predictably without duplicate openings.
Depends on: R02–R04.

## P2 — Checkout lifecycle

| ID | Small deliverable | Acceptance | Depends on |
| --- | --- | --- | --- |
| P01 | Inspect existing ERPNext POS behavior | Document posting/consolidation timing and extension points | R06 |
| P02 | Search/scan and cart | Barcode focus, quantities, unavailable product and price-list rules tested | P01, R04 |
| P03 | Discounts and totals | Role restrictions, tax rounding and currency precision reconcile with ERPNext | P02 |
| P04 | Cash payment and sale submission | Correct change; double-tap/retry does not duplicate sale; failure preserves cart | P03 |
| P05 | Receipt print/reprint | Approved layout on agreed printer/browser; correct totals and sale identity | P04, localization review |
| P06 | Return / credit path | Original-sale link, quantity limits, correct payment/ledger/stock outcomes | P04–P05 |
| P07 | Till closing and variance | Cash and other tenders reconcile; exceptions visible; approval enforced | P04, P06 |
| P08 | Retail lifecycle verification | Open → sell → return → close produces reviewed stock and ledger effects | P01–P07 |

## P3–P5 — Operational completeness

| ID | Deliverable | Acceptance |
| --- | --- | --- |
| O01 | Purchase order / receiving | Partial receipts and warehouse access produce correct stock |
| O02 | Supplier invoice / payment | Accounts payable and payment reconciliation agree |
| O03 | Stock count and transfer | Differences and transfers are authorized and traceable |
| O04 | Reorder suggestions | Defined thresholds generate reviewable replenishment requests |
| O05 | Daily sales and stock views | Defined totals match ERPNext reports; shop/period/role filters enforced |
| M01 | Reviewed identity fields | Definitions, document placements and migrations approved |
| M02 | Reviewed chart and tax setup | Accountant-approved examples balance; effective dates recorded |
| M03 | Localized receipts / invoices / credits | Approved print/export examples and correct totals |
| M04 | French then Arabic translation pass | Cashier journey translated and RTL/touch/keyboard reviewed |
| C01 | ATLASUSE ownership/mapping specification | Tenant/company mapping, source of truth and conflict policy agreed |
| C02 | Explicit CRM customer handoff | Idempotent mapping; no cross-tenant data access |
| C03 | Durable sync retries | Failure/recovery demonstrated with visible operator status |
| Q01 | Staging and pinned production baseline | Upgrade rehearsal and full retail suite pass |
| Q02 | Backup and restore | Restore measured against agreed recovery objectives |
| Q03 | Pilot usability review | Owner/cashier/accountant feedback resolved or explicitly deferred |
| Q04 | Production operations runbook | Deployment, rollback, monitoring, support and incident handling exercised |

## Ticket completion record

For each ticket record changed files, user-visible behavior, verification commands
and results, screenshots where UI matters, data/migration implications and known
limits. Financial/stock behavior requires business-level examples that reconcile
against ERPNext records. Simple styling changes need visual checks, not invented
unit tests. Never mark planned localization or runtime checks complete by inference.
