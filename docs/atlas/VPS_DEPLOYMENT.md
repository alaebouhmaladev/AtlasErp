# Verified VPS deployment

## Installed release

- Public site: `https://erp.atlasuse.site`.
- Server: Debian 12 at `85.190.254.196`; deployment uses the existing `alaebhm`
  SSH account and Docker access.
- Checkout: `/home/alaebhm/atlaserp/source`, GitHub `origin/dev`.
- Release source: `d71e1f431b`; subsequent deployment notes are documentation only.
- App image: `atlaserp:d71e1f431b`.
- Frontend image: `atlaserp-frontend:d71e1f431b`.
- Frappe source: `459a849fa6e97510d00f260022419bfd03ca75d4`.
- Engine/extension: ERPNext 17 development / ATLASERP 0.4.2.
- Installed packages: Frappe, ERPNext, ATLAS extension, HRMS, WhatsApp and CRM.
- Application OCI image index identity:
  `sha256:6b1403f3417f0e557d8782983c06279f590caa1bc56a308284d74627072f8e2f`.
- Frontend OCI image index identity:
  `sha256:13756eefda49e65a889d5ed8103ff199efc94e53ff433524fd2a11c86dcdf7e6`.

## Shift date guidance — 0.4.2

The engine rejects sales against an opening whose date differs from today in the
site timezone. Version 0.4.1 omitted this from readiness, so it could advertise
Resume while native invoice validation rejected the old shift. Version 0.4.2
adds the date check and an authorized unsaved closing-form link for the shift
owner. It preserves the engine's date validation. Overnight restaurant policy
is planned separately in POS-01D.

Staging passed current-day resume, old/future date rejection through the context
API, closing-link permission checks, existing assignment/scope fixtures and HTTP
gates. The native form URL was browser-verified against the existing Street Pizza
opening: correct company/profile/cashier, one 301 MAD sale and 1,801 MAD expected
cash. The browser form was never saved or submitted. The user explicitly chose
to keep this opening unchanged; no financial closing or cancellation was performed.

Images use the extension-only `deploy/Dockerfile.release` and
`deploy/Dockerfile.frontend-release` recipes. The final build inherits intermediate
`46d2d5b140` images on the previous `f61a96d850` runtime. The ERP/POS engine,
HR/CRM packages and POS bundle `5ER4GZUT` remain unchanged. No schema migration is
required. The prior environment is saved privately as
`.env.before-shift-date-d71e1f431b`; reverting that environment and runtime image
pair plus clearing site cache reverses this guidance-only update.

The full backup completed before rollout:
`20261007_014638-erp_atlasuse_site-*`. Live HTTPS and read-only readiness checks
passed. Private before/after document checksums and business record counts match:
the opening is still submitted/Open and the 301 MAD invoice is still submitted.
No closing entry was created. The live browser shows the old-shift explanation.
All application services run the `d71e1f431b` pair; database and Redis were retained.

## POS entry release — 0.4.1

The new `/atlas-pos` entry and scoped native handoff are documented in
[POS_READINESS.md](POS_READINESS.md). The opening dialog pins the verified
company/profile and uses company currency for the opening float. The new POS
bundle is `point-of-sale.bundle.5ER4GZUT.js`; other app manifest keys remain intact.

Isolated staging passed the readiness/access fixtures, HTTP checks and company
account regressions before rollout. Browser verification confirmed the selected
Street Pizza register, MAD opening amount and Change register navigation without
submitting an opening. Entry layout checks passed at 1024×768 and 390×844.

Live HTTPS guest/authentication/API/assets checks passed, as did both invoice
type/company/account regressions and the existing cashier's register context
with MAD. That readiness context reported Resume; the missing shift-date guard
was subsequently discovered and repaired in 0.4.2. HRMS and CRM HTML/built assets, authenticated realtime
WebSocket/polling and foreign/missing cross-site origin rejection also passed.
The browser confirmed the live register page; Administrator correctly sees the
Street Pizza shift owned by the existing cashier as In use. No assignment or
session ownership was changed by the release.

Live before/after counts matched: Company 2, Item 63, Item Price 63, POS Profile 2,
Sales Invoice 2, POS Invoice 0, POS Opening Entry 2, POS Closing Entry 0, GL Entry 4
and Stock Ledger Entry 0. Those transactions/openings are pre-existing records;
the release checks posted none. All five application/frontend services use the
new image pair; MariaDB and Redis were retained. Docker runtime configuration
identities are `sha256:ac4d2212ba3295a18835c3a6bf2cc7520cf34533d61635001bab549ac2ede8d7`
and `sha256:ba016c6b576a9f3edcc0c95e4bd8ae100330f1c80a76deec6d16764322e34f3c`.

Traffic and background jobs were paused for a fresh full live backup, reported
by the server as `20261007_012957-erp_atlasuse_site-*`. The environment is saved
privately as `.env.before-readiness-f61a96d850`; the persistent POS asset manifest
is saved as `sites/assets/assets.json.before-readiness-f61a96d850`. The rollback
pair is `atlaserp:cbc6600c94` / `atlaserp-frontend:cbc6600c94`. This is a code/assets
release with no new schema or fixture changes. Runtime services were recreated
with `--no-deps`, retaining the completed app-suite setup and existing database,
Redis and site volumes. For this release, restoring the prior environment/image
pair and asset manifest plus clearing site cache reverses the application change.
No database restore was performed; an isolated restore drill remains pending.

The image recipes are `deploy/Dockerfile.pos-release` and
`deploy/Dockerfile.frontend-pos-release`. They build the changed ERP bundle and
extension assets on the installed app suite; no HR/CRM package is reinstalled.
The final build parents were `atlaserp:93711f52db` and
`atlaserp-frontend:93711f52db`, both tested intermediate builds on the
`cbc6600c94` suite. Run `env/bin/python
apps/erpnext/scripts/publish-pos-assets.py`, then clear site cache after switching
the matching pair. Both manifests and all earlier app assets are preserved.

## Existing application suite

HRMS and CRM were installed and migrated on isolated staging before the live
schema installation. Versions, app routes and results are in
[APPLICATIONS.md](APPLICATIONS.md). All active backend, worker, scheduler and
websocket services use the same application image.

A full backup was taken after pausing traffic and background jobs immediately
before the earlier HRMS/CRM installation: `20261006_223215-erp_atlasuse_site-*`. The original environment
is saved privately as `.env.before-app-suite-7488df70fe`. The previous image pair
is `atlaserp:65233c3cf3` / `atlaserp-frontend:65233c3cf3`. App installation changes
schemas and installed-app records: rollback requires the matching pre-install
site database/files/config backup, old asset manifests and original environment;
reverting only images is insufficient. A restore drill remains pending.

Build optional apps with `deploy/Dockerfile.app-suite` and matching assets with
`deploy/Dockerfile.frontend`; use `deploy/compose.app-suite.yaml` for installation
in HRMS, WhatsApp, CRM dependency order. The current frontend inherits the full
suite asset image and applies `deploy/Dockerfile.frontend-config` to update only
proxy configuration. Run `env/bin/python
apps/erpnext/scripts/publish-app-suite-assets.py` from the backend bench to publish
optional LTR/RTL bundle keys, then clear the site cache. It preserves ERP/POS
entries and backs up both manifests with `.before-app-suite` suffixes.

The native POS company/account repair from `65233c3cf3` remains in this release.
Invoices initialize with the session profile's company before form refresh;
cash/change/receivable accounts resolve against that company. Street Pizza Demo
Cash remains mapped to Cash - SPD. Read-only regressions pass for both invoice
types; all company, menu, profile and transaction counts match the rollout
snapshot. No live invoices, openings, closings or ledger entries were posted by
this application installation.

Realtime authentication calls the internal `backend:8000` service with the site
header. The proxy preserves supplied Origin headers and fills an absent one only
when `Sec-Fetch-Site` says `same-origin`. This browser-generated metadata is
[documented by MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Sec-Fetch-Site).
Authenticated WebSocket and polling namespace checks pass through the public
HTTPS domain; foreign origins and absent cross-site origins are rejected.
The verifier is `scripts/check-realtime.mjs`, run from a runtime bench with a
private JSON file containing an existing session cookie. Do not commit that file.

The GitHub repository is readable over HTTPS without a token. No GitHub account
credentials or private deploy keys are needed for the server to pull this public
repository. Update configuration and verification scripts are in the checkout;
the application containers run immutable images rather than mounted source.

## Passed checks

- CloudPanel TLS certificate validates without bypassing verification.
- Only the ERP frontend publishes a host port: `127.0.0.1:8085`.
- Site setup exits successfully; database health check passes.
- Gunicorn, Nginx, websocket, scheduler, Redis services and worker stay running.
- Administrator login through the public HTTPS domain succeeds.
- Guest `/atlas` requests redirect to login; retail navigation renders for admin.
- CSS and SVG assets are served; login, guide and About pages show ATLASERP.
- Database branding and launcher metadata checks pass.
- Guest, Website User and Sales User access checks pass; temporary users are
  rolled back and caches cleared.
- Authenticated Socket.IO polling and WebSocket namespaces succeed through CloudPanel;
  foreign-origin requests are rejected. Live employee-list browser checks report no new errors.
- `bench doctor` reports one online worker; worker logs show scheduled jobs
  completing successfully.
- Business setup page and assets work through public HTTPS; guest access is
  denied; authenticated overview and CSRF enforcement pass.
- Company/branch scope, duplicate saves and staff disable/re-enable pass on the
  isolated site. The existing ATLAS BITES company remains. The user-approved
  Street Pizza (Demo) company, branch, 63 public menu items/prices and POS profile
  are present. The demo import posted no sales, POS openings or GL entries.
  The user's existing POS opening is preserved by the POS repair.
- Shared Desk and website theme assets are registered and served through HTTPS.
- `/atlas-portal` requires login and links to native scoped document pages.
- `/atlas-menu` renders the verified public menu and meal-deal choice counts.
- Desktop Item lists/forms, report controls and POS opening dialog inspected;
  portal and restaurant menu checked at 390px with no document overflow.
- `node scripts/test-pos-startup.mjs` checks session defaults before form refresh
  for new/reused forms. `ATLAS_CHECK_SITE=SITE env/bin/python
  apps/erpnext/scripts/check-pos-company.py` verifies cash/change/receivable
  accounts for Sales Invoice and POS Invoice, plus validation preservation.
  The account regression reproduced the original error before the fix and
  passed on staging and production without inserting or submitting documents.

## Backup and credentials

An initial backup of the database, public/private files and site configuration
was created under `sites/erp.atlasuse.site/private/backups` in the sites volume.
An off-server copy has not been performed. Automated backups and a restore drill
remain to be configured before relying on this deployment for real shop data.

Server credentials are in the private checkout `.env`. A local Administrator
login reference is saved in ignored `.atlas/vps-login.txt`, file mode `0600`.
Neither credentials nor backups belong in GitHub.

## Product limits

This is the current evaluation build. Company selection, brands, branches,
dedicated warehouses and scoped business-structure roles are delivered; account
activation uses administrator User management. POS profile and retail transaction
posting was tested on the isolated site (invoice, change, balanced GL and no
stock movement for menu services), with transactions rolled back. The shared
interface, customer portal, read-only restaurant menu and HR/CRM applications are delivered.
Moroccan payroll rules, employee configuration and ATLASUSE data synchronization remain pending. Online
ordering, kitchen/table workflows, Moroccan accounting certification, custom
checkout, payment-provider integration and ATLASUSE synchronization remain pending. Follow [VPS operations](VPS.md) for updates
and backups, and the [roadmap](ROADMAP.md) for product work.
