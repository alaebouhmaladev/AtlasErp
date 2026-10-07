# ATLAS POS — Android tablet first

Prepared 2026-10-06. This is a product and implementation plan, not a released
mobile application. Android tablets are the first delivery target; iPad/iPhone
follow after the Android restaurant workflow is proven. The user confirmed that
**offline cash sales are essential** and wants tablets, screens, printers and
other supported devices connected through **the same shop Wi-Fi router**.
Printing must be configurable rather than tied to one printer model. Epson is
the initial preference, not an exclusive requirement. Hardware suggestions below
are optional; exact interfaces and physical compatibility remain to be tested.

## Product direction

Build a dedicated ATLAS POS application with the ATLASERP green/lime design.
ERPNext remains responsible for submitted invoices, stock and accounting;
ATLASERP supplies the restaurant workflows, device APIs and owner backoffice.
Use Street Pizza (Demo) as a development dataset, not evidence of a commercial
partnership or a fiscally approved restaurant setup.

The competitive goal is a complete, dependable business system: fast checkout,
clear cashier setup, restaurant service, receipts, stock and owner visibility.
Success must be measured through real cashier tasks and reconciled transactions,
not the number of settings or menu entries.

## Public LaCaisse benchmark

Reviewed on 2026-10-06. Its public documentation lists catalog, privileges,
customers, loyalty, discounts, reporting, payments, stock, invoicing, online
orders and restaurant operations. Its Android app listing specifically describes
table order taking and a second checkout station. These are public feature
references; main-register Android support, offline behavior and exact hardware
compatibility have not been verified here.

- [LaCaisse documentation](https://documentation.lacaisse.ma/)
- [LaCaisse public site](https://caisse.ma/fr/homepage)
- [LaCaisse Android listing](https://play.google.com/store/apps/details?id=com.lacaisse.app&hl=en_US)

The following architecture and delivery order are our proposed ATLAS design.

## Architecture decision

Recommend **Flutter** for a shared Android/iOS interface and application logic,
with native Kotlin/Swift adapters where hardware requires a vendor SDK. Validate
this choice on the actual tablet and printer before committing to those devices.
An embedded ERP web page alone will not supply the required local storage,
hardware behavior or restaurant workflows.

```mermaid
flowchart LR
  subgraph Shop[Same shop router: local Wi-Fi and LAN]
    Tablet[Android tablet: ATLAS POS] <--> Hub[ATLAS shop hub: shared orders and device routing]
    Waiter[Waiter tablet] <--> Hub
    Kitchen[Kitchen screen] <--> Hub
    Display[Customer screen] <--> Hub
    Hub --> Printer[Configured receipt and kitchen printers]
    Tablet --> Local[Local catalog, cart and durable sale outbox]
  end
  Hub <--> API[Authenticated ATLAS POS API and cloud sync]
  API --> ERP[ERPNext document validation and posting]
  ERP --> Office[ATLASERP owner backoffice]
  API --> Restaurant[Restaurant orders and kitchen tickets]
  Later[iOS app: later release] --> API
```

| Component | Responsibility |
| --- | --- |
| Planned `mobile/atlas_pos/` | Flutter screens, application state, API client, local database, hardware adapters |
| `apps/atlas_erp/atlas_erp/pos_api/` | Delivered read-only register readiness/context; versioned transaction operations, request deduplication and device authorization remain planned |
| Planned shop hub | Branch-local shared order authority, paired device registry, durable kitchen/print routing and cloud synchronization; deployment/runtime chosen in a tested prototype |
| Existing ERPNext | Financial and stock document lifecycle; no direct ledger writes from the app |
| Restaurant extension | Unpaid orders, tables, modifiers, kitchen tickets and settlement links |
| Existing ATLASERP web backoffice | Company/brand/branch, products, prices, purchasing and management workflows |

Use authenticated HTTPS requests. Evaluate OAuth authorization code with PKCE
against the pinned Frappe version before adopting it; native-client support and
revocation need an integration test. Store device tokens in OS protected storage.
Do not embed an Administrator key, store the user's password, or treat a short
cashier PIN as sufficient server authentication. A PIN may unlock an already
authorized local cashier session under a reviewed policy.

One business customer normally receives its own Frappe site/database. Brand,
branch and register are operational scopes inside that customer. Company records
alone are not tenant isolation. Device enrollment and every server operation must
enforce the allowed site, company, branch, register and actual cashier identity.
Audit generic ERP APIs and existing whitelisted POS helpers as well as new APIs.

## Delivery phases

| Phase | Delivered behavior | Exit evidence |
| --- | --- | --- |
| 0 — Register readiness | Company, cashier assignment, price list, warehouse and payment mappings checked before opening; resume own shift or explain another cashier's open shift | A restricted cashier opens the correct register without developer help; wrong scope and concurrent opening are rejected |
| 1 — Android counter POS | Sign-in/enrollment, menu/categories/search, cart, validated modifiers, cash payment/change, receipt, return and cash closing | Open → sell → print → return → close reconciles with ERPNext on the selected tablet/printer |
| 2 — Offline cash | Cached approved catalog, durable local cash sales, recovery and visible synchronization queue | Network loss, app restart, server timeout and repeated replay lose no sales and create no duplicate invoice |
| 3 — Connected restaurant service | Paired devices on one router, local shop hub, tables, takeaway/delivery orders, waiter orders, kitchen routing/display, statuses, table transfer and split settlement | With WAN disconnected, waiter → till → kitchen updates agree; concurrent edits, kitchen retries and settlement retries preserve orders and produce the correct invoice(s) after sync |
| 4 — Owner operations | Brands/branches, ingredient recipes and wastage, buying, counts, transfers, staff controls, reports, loyalty and promotions | Branch reports match posted records; ingredients and purchasing reconcile; operator permissions tested through APIs |
| 5 — Customer channels and payments | QR menu/order flow, delivery dispatch, online storefront and country/provider payment integrations | Orders reach the right branch; payment callbacks are authenticated, deduplicated and reconciled |
| 6 — iOS and expansion | iPad POS, iPhone waiter/owner layouts, onboarding/billing/support and country packs | Real iOS hardware checks and store release requirements pass; each country pack has its own pilot and local review |

An online development build may precede phase 2. **Phase 2 is mandatory before
the first commercial pilot**, following the user's offline cash requirement.
Phase 1 includes basic meal modifiers; full table/kitchen operations follow in
phase 3. Card/transfer recording and actual electronic payment processing are
separate capabilities.
For a restaurant pilot using shared waiter/kitchen screens, phase 3's local
coordination and outage checks are also required before commercial use.

## Small tasks, in order

| ID | Bounded task | Acceptance |
| --- | --- | --- |
| MOB-01 | Specify register readiness and action permissions | Missing cashier/account/profile and existing-shift cases have actionable owner/cashier messages; no automatic cancellations |
| MOB-02 | Install/pin Flutter toolchain and create Android app | Debug APK installs on a named device; green/lime tablet layout, French foundation and Arabic RTL direction verified |
| MOB-03 | Device enrollment and cashier authentication | Tokens protected/revocable; restricted user cannot access another site/branch; Administrator credentials not used at the till |
| MOB-04 | Scoped bootstrap API and catalog cache | Correct brand/branch/register, 63 demo menu prices and required meal choices load; setup blockers identified before checkout |
| MOB-05 | Session resume/open flow | Own session resumes; another cashier's session explains the block; one profile per register; duplicate opening requests return the same result |
| MOB-06 | Touch catalog, search and cart | Large touch targets, quantities and required modifier limits; interrupted cart survives restart; scanner focus demonstrated |
| MOB-07 | Server quotation and idempotent cash sale | Server validates prices/taxes/discount authority; double tap, timeout and retry produce one submitted invoice with correct change |
| MOB-08 | Configurable network receipt adapters | Owner pairs a supported printer by connection/protocol and assigns its role; correct totals print; failure does not repost a sale; uncertain delivery/reprints are explicit |
| MOB-09 | Return and closing | Authorized original-sale refunds and counted cash variance reconcile; no silent cancellation of another cashier's shift |
| MOB-10 | Offline outbox and synchronization | Local sale plus outbox written atomically; duplicate replay, crash recovery, stale catalog and rejected records tested |
| MOB-11 | Android pilot hardening | Real-device lifecycle, backup/restore, tenant isolation, app upgrade and support diagnostics pass |
| LAN-01–LAN-07 | Shared-router device coordination | Complete the local-network tasks below before claiming offline shared restaurant operation |
| REST-01 onward | Unpaid table orders → kitchen → shared settlement | Build on the local hub and continue POS_WORKFLOW.md, then add transfer/split-bill cases |

MOB-01A's read-only web register readiness and native handoff are implemented in
0.4.1. Its checks do not complete native endpoint guards, safe concurrent opening
or register provisioning. Next: **POS-01A–C and MOB-02–04**, then the transaction
and offline path. [SQUARE_BENCHMARK.md](SQUARE_BENCHMARK.md) expands the platform
scope without duplicating these tickets. Do not describe a cart mockup or
unconnected APK as a working POS.

## Prevent the setup failures already observed

The opening screen must show a human-readable restaurant/branch/register name,
not require cashiers to understand payment ledgers or configure POS Profiles.

- Only offer profiles assigned to the authenticated cashier and allowed branch.
- Select a permitted register's company explicitly; never retain another company
  from global defaults while using that profile's payments or menu.
- Before opening, validate every configured payment method's company account.
  Owners get links to the missing setup; cashiers see who can resolve it.
- Resume the current cashier's open session. For another cashier's open session,
  show the register and cashier with a manager handover/closing route. Cancel an
  unused opening only through an explicit authorized operation.
- Each simultaneous physical till gets its own POS Profile. Multiple assigned
  users do not make one profile support multiple simultaneous open shifts.
- Cash, card, transfer and cheque mappings are deliberately configured. Never
  hide an account error by mapping another company's money to the demo cash till.

## Offline correctness

SQLite is the proposed local store. A completed local cash sale and its outgoing
event must be durable in one transaction before showing local success. Each sale
has a device-generated request identity, catalog/tax policy version, cashier,
register, session and business event timestamp. Amounts use currency minor units
or decimal values, not binary floating-point cart arithmetic.

Delivery is retryable; a server-side unique request identity and transactional
posting prevent duplicate invoices. The server verifies permissions and uses
ERPNext's normal document operations. A repeated request returns its original
result. Sync states are visible: pending, syncing, synchronized and needs review.
A rejected event is retained with its cash/receipt evidence; it is never silently
discarded or repriced after the customer has paid.

Agree policies for stale prices/taxes, stock overselling, expired authorization,
closed accounting periods and server-side session changes before permitting
offline selling. Offline authorization is bounded to an enrolled device/cashier
and an established register/session; it does not allow arbitrary new users or
companies. Final closing waits for reconciliation of pending sales.

Offline receipt numbering and its relationship to final fiscal invoices need
local accountant review. An unsynchronized local sale must remain distinguishable
from a server-posted invoice. Offline cash acceptance does not prove offline card
or mobile-money processing: those depend on the provider and certified terminal.

Initial offline support is for one till and its local printing. The shared
restaurant target adds a tested shop hub to coordinate waiter/till/kitchen
devices on the same router during internet outages. Connecting to the router
provides network reachability; the hub and applications provide shared state.
Standalone offline cash and offline shared restaurant operation have separate
acceptance checks, and both required scopes must pass for the intended pilot.

## Shared-router device design

Each branch has its own paired device registry and routing rules. Devices join
the shop network through Wi-Fi, or Ethernet to the same router where appropriate.
The router remains the network connection; a separately running ATLAS shop hub
coordinates devices. Do not assume a normal router can host the application.
Select the hub host/runtime after prototyping unattended startup, storage and
power recovery; possible hosts include a dedicated small computer or a validated
always-on Android host. This architecture is planned, not currently deployed.

The owner-facing flow is **Devices → Add device → Pair → Choose role → Test**.
Use names such as "Counter receipt", "Kitchen pizza" and "Customer display",
with connection status and a clear retry action. Network discovery is optional;
allow QR/manual pairing and address entry for devices that do not advertise
themselves. Use stable device identities and reserve addresses where needed.
Sharing Wi-Fi is not authorization: approve pairing and enforce branch, device
and operator permissions on local and cloud operations.

| Device role | Planned behavior |
| --- | --- |
| Cashier tablet | Catalog/cart, cash checkout, own till/session, receipts and visible sync status |
| Waiter tablet/phone | Permitted tables/orders and send-to-kitchen; tender/refund actions require cashier/manager permission |
| Kitchen screen | Queue by preparation station, new additions, acknowledged/ready status and reconnect recovery |
| Customer display | Only the assigned till's permitted cart/total/order status; no management or other customer data |
| Receipt printer | Configured destination for an assigned till; supported network protocol/vendor adapter and tested paper/characters |
| Kitchen printer | Category/station routing, durable ticket identity, job status and explicit reprint handling |
| Scanner/drawer/other peripheral | Supported interface and adapter; USB-only devices attach through a compatible host/bridge and do not join Wi-Fi by themselves |

Keep receipt content and kitchen ticket data independent of the printer adapter.
Persist model, transport, address, capabilities and routing in configuration;
do not hardcode one brand/model/address into checkout. Epson adapters can be the
first supported family. Add other protocols/models through a published tested
compatibility list; being connected to the router alone does not establish a
device's printing or display protocol. Network-only discovery must not silently
register every device or expose the printer/hub on the public internet.

The local hub serializes shared order changes, stores accepted commands and
routes kitchen/display/print updates. Assign command identities and order
revisions; reject conflicting edits visibly instead of overwriting a paid or
changed table. A screen reconnects from the last acknowledged revision. Outgoing
cloud events remain durable and deduplicated; cloud ERPNext still validates and
posts financial/stock documents. Settle an order only once across local and
cloud retry paths. Keep internal kitchen commands separate from invoice posting.

If the WAN fails but the LAN/hub remains available, the intended restaurant
workflow continues locally and shows pending cloud synchronization. If the hub
or LAN fails, shared table changes cannot be confirmed: show the outage and
retain queued work. Permit only a tested isolated-till cash fallback under the
offline policy, block conflicting shared settlements, and reconcile before
resuming shared work. Do not automatically create a second order authority.

### Small local-network tasks

| ID | Deliverable | Acceptance |
| --- | --- | --- |
| LAN-01 | Hub topology and runtime prototype | A named host starts unattended and recovers its durable state after restart; no router-hosting assumption |
| LAN-02 | Pairing and device registry | Owner adds/revokes named devices by branch; unpaired/wrong-branch operations are rejected; QR/manual fallback works |
| LAN-03 | Configurable device adapters and routing | Two supported printer configurations use the same receipt API; station/till routing and test jobs reach only the assigned destination |
| LAN-04 | Shared order command log | Concurrent edits, retries and hub restart preserve order revisions and prevent duplicate settlement |
| LAN-05 | Kitchen/customer screen clients | Correct station/till scope, restricted display data, acknowledged updates and reconnect replay demonstrated |
| LAN-06 | WAN-outage synchronization | Waiter → till → kitchen works with internet disconnected; restoring internet posts each accepted cash sale once |
| LAN-07 | Local failure and restore | Hub/LAN loss clearly blocks unconfirmed shared actions; queued events, fallback reconciliation and backup/restore tested |

Exercise at least two POS/waiter clients, one kitchen screen and a supported
network printer on the same router. Test WAN unplugged separately from Wi-Fi
loss, hub failure and power loss. Declare supported capacity only after measuring
the actual host/network/device combination; do not promise unlimited devices.

## Restaurant and hardware requirements

Plan menu sizes/variants, extras, required combo choices, notes/allergens,
available/sold-out state, table ownership, additions sent as new kitchen tickets,
prep/ready/served statuses, bill preview, transfer and split-by-item/amount.
Unpaid orders do not submit accounting sales. Settlement links paid orders to
validated invoices, and repeated kitchen sends/settlement cannot duplicate them.

Record exact tablet/terminal and printer models, Android version, paper width,
USB/Bluetooth/LAN connection, scanner input, cash drawer and customer display.
Use vendor SDKs where needed. A cash drawer connected through a printer is a
different integration from a standalone USB device. Arabic receipt rendering and
French accents must be tested on paper; UI RTL alone does not establish support.
iOS printer transport/SDK compatibility needs its own check.

Print jobs have their own retry history. A lost printer acknowledgement can mean
the receipt already printed; display that uncertainty and label reprints rather
than guaranteeing one physical print. Tablet sleep/restart, cable loss, printer
paper-out and app updates must be part of hardware testing.

### Optional pilot hardware reference

The tablet suggestion prioritizes daily restaurant use and support life. It is
an optional pilot choice. Printing and screen routing use configurable devices;
the product does not require a fixed printer model or an already certified pair.

| Part | Proposed choice | Reason and purchase check |
| --- | --- | --- |
| Android tablet | Samsung Galaxy Tab Active5 Pro, 10.1-inch; Moroccan 6 GB / 128 GB model SM-X356BZGAMWD | IP68, replaceable batteries and security support listed through 31 May 2033; get a local warranty/service quote |
| Receipt printer | Owner-selected supported Wi-Fi/LAN printer; Epson is the initial adapter preference | Confirm protocol, model/interfaces, paper width and power supply; run a test receipt before assigning the till |
| Counter mount and power | Secure tablet stand, dedicated Samsung-compatible charger or approved dock | Validate continuous charging, thermal behavior and secure cable routing |
| Shop network and hub | One shop router for tablets/screens/network printers, plus a tested local hub host | Keep permitted POS devices reachable without the internet; configure the intended POS network and device addresses |
| Cash drawer | Drawer explicitly compatible with the printer's kick connector | Check electrical requirements and connector; a matching-looking plug alone is insufficient |

Optional hardware references: [Samsung Morocco tablet specifications](https://www.samsung.com/n_africa/business/tablets/galaxy-tab-active/galaxy-tab-active5-pro-sm-x356bzgamwd/),
[Epson printer specifications](https://download4.epson.biz/sec_pubs/bs/html/m001464/en/chap07_1.html)
and [Epson connectors](https://download4.epson.biz/sec_pubs/bs/html/m001464/en/chap02_3.html).
Prices, local stock and warranty terms have not been verified; request a Moroccan
supplier quote before purchasing. Buy/test one pilot kit before ordering a fleet.

For compatible Epson models, evaluate the ePOS SDK behind the common network
printer interface; other supported families receive their own adapters. Pin a
tested SDK/firmware combination after model confirmation. [Epson's TM-m30III software list](https://support.epson.net/setupnavi/index.php?LG2=EN&MKN=TM-m30III&OSC=ARD&PINF=swlist)
lists the Android SDK; [Epson's SDK documentation](https://download4.epson.biz/sec_pubs/pos/reference_en/technology/epson_epos_sdk.html)
describes Android/iOS interfaces and model-dependent transports.

Device power is independent of network transport. Validate each tablet, screen,
hub and printer with its appropriate charger/power supply. The product must not
depend on a particular printer charging the tablet. For the optional Samsung
tablet, verify charging and any No Battery Mode requirements against its manual
and test the actual mount/charger combination.

An internet outage and a power outage are separate cases. Local cash checkout and
LAN printing must work with the WAN disconnected while local equipment is powered.
If the shop requires printing during a power cut, size and test a UPS for the
printer, hub and network; running the tablet on its battery alone cannot power them.
No Battery Mode depends on continuous external power.

Hardware acceptance on the named kit: all-day charging/temperature test; WAN
unplugged receipt; French accents/Arabic rendering on paper; paper-out/recovery;
tablet restart with a pending sale; lost printer acknowledgement; drawer action;
and restoration of synchronization without a second invoice. A kitchen printer
is a separate later selection based on heat, grease and ticket-routing needs.

## Morocco and African market packs

Start with MAD, French and Arabic, familiar receipt terminology, clear cashier
training and owner reporting. Validate identity fields, tax configurations,
invoice/credit/receipt requirements and numbering with a Moroccan accountant for
the actual business regime. The demo is not a compliance certification.

Expand by named country: language/currency/precision, time zone, accounting/tax
rules, payment providers, receipts, hosting/privacy needs, hardware availability
and local support. Apply OHADA only where relevant. Country-specific mobile money
and card integrations need provider agreements and reconciliation tests. Offer
one country pack at a time, with independent customer data isolation.

## Pilot release gate and current readiness

Before taking real shop data, choose and test a supported stable ERPNext/Frappe
pair, enforce operational cashier permissions, demonstrate restore, validate
fiscal examples, pin dependencies and record the actual tablet/printer matrix.
Test regular cashiers, waiters and managers; success as Administrator alone is
insufficient. Test two tenants/registers and simultaneous operators.

No lost cart/sale after a supported restart, no duplicate financial posting under
retry, no cross-customer access and matching cash/stock/ledger examples are release
gates. Measure catalog search, scan-to-payment task time, support interventions and
print reliability on real hardware before agreeing performance targets.

Local check on 2026-10-06 found Android Studio and Android SDK platforms 35/36 and
build tools installed. Flutter/Dart were not found on PATH; an iOS/Xcode toolchain
was not found at /Applications/Xcode.app. No Flutter SDK was installed, no APK was
built, and no app-store publication or live POS changes were performed by creating
this plan. Toolchain versions and package dependencies must be pinned during MOB-02.

## Technical references

- [Flutter platform channels: Android Kotlin/Java and iOS Swift/Objective-C adapters](https://docs.flutter.dev/platform-integration/platform-channels)
- [Flutter offline-first architecture](https://docs.flutter.dev/app-architecture/design-patterns/offline-first)
- [Frappe REST authentication and document APIs](https://docs.frappe.io/framework/user/en/api/rest)
- [Existing ATLASERP POS workflow and posting findings](POS_WORKFLOW.md)
- [Operational architecture and tenant isolation](ARCHITECTURE.md)
