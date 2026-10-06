# Verified VPS deployment

## Installed release

- Public site: `https://erp.atlasuse.site`.
- Server: Debian 12 at `85.190.254.196`; deployment uses the existing `alaebhm`
  SSH account and Docker access.
- Checkout: `/home/alaebhm/atlaserp/source`, GitHub `origin/dev`.
- Release source: `cbc6600c94`; subsequent deployment notes are documentation only.
- App image: `atlaserp:cbc6600c94`.
- Frontend image: `atlaserp-frontend:cbc6600c94`.
- Frappe source: `459a849fa6e97510d00f260022419bfd03ca75d4`.
- Engine/extension: ERPNext 17 development / ATLASERP 0.4.0.
- Installed packages: Frappe, ERPNext, ATLAS extension, HRMS, WhatsApp and CRM.
- Application image identity:
  `sha256:6a35e706afda37ebbd90bda1aece700a08bb70d2ba6e5719ad9c9bf5beeedb6e`.
- Frontend image identity:
  `sha256:7809002cc6aa08dd4ef433062d93817646a604508ab657a704a209d6e9762d88`.

HRMS and CRM were installed and migrated on isolated staging before the live
schema installation. Versions, app routes and results are in
[APPLICATIONS.md](APPLICATIONS.md). All active backend, worker, scheduler and
websocket services use the same application image.

A full backup was taken after pausing traffic and background jobs immediately
before installation: `20261006_223215-erp_atlasuse_site-*`. The original environment
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
