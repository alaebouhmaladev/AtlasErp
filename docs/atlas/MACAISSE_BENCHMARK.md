# MaCaisse / LaCaisse benchmark — Android ATLAS POS

Public sources reviewed 2026-10-07; Android verification completed 2026-10-08. Target: comparable business workflows in ATLAS branding,
with **Android as the main till**, takeaway and table service, required offline
cash and configurable devices on the same shop router. This adds a focused
Moroccan restaurant benchmark to [SQUARE_BENCHMARK.md](SQUARE_BENCHMARK.md).
Existing MOB, LAN, REST and POS tickets remain the implementation IDs.

## What the public sources establish

| Primary source | Observed public scope |
| --- | --- |
| [macaisse.ma](https://macaisse.ma/) | Stock, quotations/invoices, online storefront, delivery channel manager, backoffice analytics, franchise, HR, payments; advertised KDS, waiting screen, QR menu/reviews, WhatsApp, kiosk and QR ordering |
| [Official documentation](https://documentation.lacaisse.ma/docs-page) | Catalog/categories/variants/barcodes, bundles/supplements, discounts, cashier roles, customers/loyalty, reports, stock and invoicing; rooms/tables/reservations, held orders, kitchen notes/routing/courses, transfers and cancellations; iPad installation and network printer setup |
| [Developer's Android listing](https://play.google.com/store/apps/details?id=com.lacaisse.app&hl=en_US) | Android phone/tablet order taking and a second payment station; listing title identifies a remote application |

The linked feature subpages returned the homepage during this inspection. No
authenticated till, provider contract or real hardware was tested. Full main-till
Android behavior, outage guarantees, synchronization internals and exact payment
SDK compatibility are **not established** by these sources. Do not infer these
from a screenshot or a warning about unsynchronized data.

The rest of this document specifies **our implementation and acceptance criteria**;
it is not a description of the competitor's internal architecture.

## Coverage and development order

“Engine” means reusable ERPNext records/workflows exist, not a completed ATLAS
cashier experience. “Web delivered” means the existing online ERP workflow.

| Capability | ATLAS status today | Next implementation / acceptance | Ticket / release |
| --- | --- | --- | --- |
| Main Android till | Local native preview 0.1 | Enrolled device and assigned cashier use scoped register | MOB-02–05 / A–B |
| Menu/category/search | 63 public demo items, web menu and Android preview | Authorized register catalog, disabled/expired prices and scanner | MOB-04,06 / B |
| Meal choices | Required choices/counts enforced in Android drafts | Quote modifiers and supplemental prices server-side | MOB-06,07 / B |
| Cart/notes/held tickets | Local Android drafts | Server order identity, operator scopes and shared history | MOB-06, REST-01 / B,D |
| Takeaway/table selection | Local draft association | Branch floor plan, order ownership and table availability | REST-01–03 / D |
| Cash/check/change | Web engine; native app pending | Idempotent native posting, change and receipt reconcile | MOB-05,07 / B |
| Split tenders/equal shares | Web 0.5, one invoice | Android tender UX; separate bill allocation later | MOB-07, REST settlement / B,D |
| Tips/service extras | Web 0.5, optional profile settings | Native quote plus original-sale refund limits | MOB-07,09 / B |
| NAPS card recording | Manual external approval/reference capability on web | Native approved/reference/amount match; provider integration requires SDK/contract | MOB-07 / B, provider track |
| Offline cash | Planned, mandatory pilot gate | Atomic sale/outbox, recovery, bounded authorization, duplicate replay | MOB-10 / C |
| Return/cash closing | Native ERP web lifecycle | Authorized refund and counted variance, pending sync gates | MOB-09 / B–C |
| Network receipts/drawer | Planned adapters | Configured transport/address/role, real print/reprint evidence | MOB-08 / B–D |
| Same-router waiter/till | Planned local hub | Authorized pairing and concurrent order coordination without WAN | LAN-01–07 / D |
| Kitchen printer/KDS | Planned | Durable station routing, added lines/courses, acknowledgement/retry | LAN, REST / D |
| Customer/waiting screens | Planned | Assigned till/order only, reconnect recovery | LAN, REST / D |
| Floor plan/transfers/splits | Planned | Versioned changes, no double settlement or dropped orders | REST / D |
| Reservations/covers | Planned restaurant module | Availability, updates and privacy-reviewed notifications | REST / D–E |
| Discounts/permissions | Engine, web behavior | Cashier action matrix; manager overrides auditable through APIs | POS-01, MOB-07 / B,E |
| Receipts/invoices/quotes | Engine | Morocco-reviewed identifiers, TVA, rounding and credit notes | M01–03 / B,E |
| Clients/loyalty/promotions | CRM/customer engine; loyalty UX pending | Authorized profile, earn/redeem/return reconciliation | Owner operations / E |
| Inventory/counts/transfers | Engine | Simple branch workflows and stock permissions | O01–04 / E |
| Recipes/ingredients/wastage | BOM/stock engine; restaurant UX pending | Sale/recipe consumption, substitutions and waste reconcile | Restaurant stock / E |
| Suppliers/buying | Engine | Receive/invoice/pay lifecycle, partial receipts | O01–02 / E |
| Owner reports/franchise | Reports/brand/branch foundation | Sales/returns/tips/variance by branch match posted records | O05 / E |
| HR/staff | HRMS installed | Shift controls; payroll reviewed separately per country | HR country pack / E–G |
| QR menu/customer portal | Read-only ATLAS menu/portal delivered | Live authorized menu and branch order intake | Customer channels / F |
| Online orders/kiosk | Planned | Order → accept → kitchen → fulfill; timeout/duplicate recovery | Customer channels / F |
| Delivery/channel manager | Planned | Dispatch and authenticated partner connectors | Customer channels / F |
| WhatsApp/reviews | Dependency available; connector pending | Consent, correct branch and authenticated status/events | Customer channels / F |
| Integrated electronic payments | No NAPS SDK or online provider connected | Provider approval, callbacks, reversal and reconciliation | Provider track / F |
| Salon appointments/staff earnings | Future vertical | Staff availability, deposits and payout contracts | Vertical pack / G |
| Independent clients/Africa | Site isolation design, country packs pending | Provision/restore/access tests per client and reviewed country rules | Q tickets, P7 / G |

## Releases with small, reviewable steps

### A — Android preview (this slice)

1. Pin Gradle/Android tooling; create a native Android package separate from a production till.
2. Load the canonical public menu, use MAD minor units and validate meal choices.
3. Add touch cart, notes and local takeaway/table association.
4. Persist active/held drafts atomically; preserve catalog identity on restart.
5. Verify tablet/compact layouts, Arabic direction, tests and a debug APK.

This preview cannot submit sales, print receipts, authenticate a cashier or share
orders. Local drafts are not offline cash sales. See
[mobile README](../../mobile/atlas_pos/README.md) for build and test evidence.

### B — Connected Android counter till

Continue MOB-03–09: device enrollment → scoped catalog/quote → resume/open own
register → durable request identity and cash posting → receipt adapter → return
and closing. Test a restricted cashier end to end on staging before enabling
real tills. Never cancel another cashier's shift as a setup shortcut.

### C — Offline cash gate

MOB-10: approve cached policy/version → atomic local sale/outbox → visible queue
→ idempotent server replay → exception review and reconciled closing. Prove WAN
loss, killed process, repeated replay and upgrade recovery. Complete this before
commercial cash use, as requested.

### D — Shared restaurant and hardware gate

LAN-01–07 plus REST: branch hub/enrollment → table orders/concurrency → kitchen
station routing → KDS/printer acknowledgements → courses/transfers → separate
bill allocation → WAN-off recovery. Test the actual router, Android tablets and
selected Epson/other adapters; do not hardcode one printer model or IP address.

### E — Owner and Moroccan operations

Catalog import/price changes → customers/loyalty → recipe stock/waste → suppliers
and counts → branch reports → accountant-reviewed documents → staff controls.
Existing ERP modules reduce engine work; each simplified workflow still needs
scope enforcement and a complete business example.

### F–G — Customer channels, providers and expansion

Live QR/order intake → kiosk → delivery dispatch → partner connectors → provider
payments. Then salon/service verticals, client provisioning and individual
African country packs. Online fees, stored cards, deposits and payouts require
the relevant provider contract and integration tests; owning a NAPS TPE alone
does not provide these integrations.

No calendar or “exact clone” completion claim is made. Feature parity is measured
by the documented operator tasks and their acceptance evidence. Android is the
current native target; iOS has no implementation commitment in this sequence.

## Live data boundary

This slice makes no ERP database changes and contains no ERP credentials.
POS-OPE-2026-00002 and its existing 301 MAD sale remain unchanged, following the
user's explicit instruction. The menu is the approved public demo snapshot;
legal company identity and tax configuration are not inferred from it.
