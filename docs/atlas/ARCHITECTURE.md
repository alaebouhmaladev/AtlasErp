# Architecture decision record — 5 October 2026

Status: development baseline; production version decision still open.

## Extend the ERP engine

Frappe owns authentication, roles, permissions, database access, background jobs,
files and APIs. ERPNext owns customers, suppliers, stock, POS, invoices, payments
and accounting. ATLASERP owns product experience, guided retail setup, validated
localization and integrations. Keep accounting and stock posting inside ERPNext.

```text
Browser / tablet
  ├─ ATLASERP /atlas (launchpad now, guided workflows later)
  └─ ERPNext Desk / POS (existing operational workflows)
             ↓ authenticated Frappe requests and permission checks
      ERPNext + atlas_erp extensions
             ↓
      MariaDB / Redis / workers / persisted files

ATLASUSE CRM ↔ future authenticated integration adapter ↔ ATLASERP
```

Planned native POS adds a Flutter Android/iOS client, local catalog/cart/outbox,
hardware adapters and versioned authenticated POS operations in `atlas_erp`.
Tablets, kitchen/customer screens and supported network printers connect through
the same shop router. A planned local hub coordinates shared orders and device
routing during WAN outages; printer models/transports are configurable adapters.
ERPNext retains financial posting authority. See [MOBILE_POS.md](MOBILE_POS.md)
for the Android-first decision, offline boundaries and hardware acceptance gates.

## Repository boundaries

| Location | Purpose |
| --- | --- |
| `erpnext/`, `banking/` | Existing upstream ERP engine and assets |
| `apps/atlas_erp/atlas_erp/` | Product hooks, controllers, pages, assets, future doctypes and patches |
| `compose.yaml`, `scripts/` | Development runtime and commands |
| `docs/atlas/` | Product decisions, backlog and release evidence |

Use custom fields, fixtures, supported hooks, country configuration and separate
controllers before changing core files. Record unavoidable core patches with an
upstream comparison and regression test. Do not fork ledger arithmetic or write
stock/ledger tables directly. Custom UI must call the same validated document
operations as ERPNext and honor submit/cancel/amend behavior.

## Baseline and upgrades

The inherited snapshot is ERPNext 17 development (repository commit
`20a82b8bd9` before this setup). The inherited Dockerfile uses Frappe `develop`.
This permits exploration but is not a reproducible production baseline. Capture
the fetched Frappe commit and image digest in the setup log. Compatibility must be
tested; matching major labels alone do not prove matching development snapshots.

Before pilot data becomes real business data:
1. Evaluate a supported stable ERPNext/Frappe pair and dependency versions.
2. Port this extension to that pair in a separate branch; do not downgrade a populated database.
3. Pin commits/images and dependency artifacts, build staging and execute the retail lifecycle suite.
4. Record the upgrade procedure, take backups and prove restore before release.

## Companies and customer isolation

For a pilot, one Frappe site can contain one company and multiple shops/warehouses.
Multiple companies in one site serve a single related business group only after
company restrictions are tested. Independent customer businesses should have
separate sites/databases, backups and credentials by default. A Company record
alone is not a complete isolation boundary. Hosting/billing/site provisioning is
a later platform workstream, not part of a cashier checkout request.

## ATLASUSE integration contract

Keep ATLASUSE as the source of CRM leads/opportunities. ATLASERP owns products,
stock, invoices, accounting and posted payments. Confirm which system owns
customers/contacts before implementing synchronization. First integration should
be an explicit customer handoff with external IDs, idempotency keys and a visible
sync status. Follow with an outbox/retry/dead-letter flow; do not use shared database
writes or synchronous two-way edits without conflict rules. Map one CRM tenant to
the correct ERP site/company and test isolation. No CRM files are changed here.

## Production requirements

TLS/reverse proxy, production application workers, scheduler, queue monitoring,
health/readiness checks, secrets rotation, restricted DB access, encrypted backups,
restore drills, audit logs, monitoring and staged migrations. Cashier accounts must
have minimum privileges; administrators must not be shared at tills. Evaluate MFA,
retention, data location and incident handling before onboarding customers.
