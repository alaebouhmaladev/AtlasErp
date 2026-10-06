# Verified VPS deployment

## Installed release

- Public site: `https://erp.atlasuse.site`.
- Server: Debian 12 at `85.190.254.196`; deployment uses the existing `alaebhm`
  SSH account and its Docker access.
- Checkout: `/home/alaebhm/atlaserp/source`, GitHub `origin/dev`.
- Compose configuration includes corrections through commit `f0e6da6b81`.
- App image: `atlaserp:65233c3cf3`, POS repair from source commit `65233c3cf3`.
- Frontend image: `atlaserp-frontend:65233c3cf3`.
- Frappe source: `459a849fa6e97510d00f260022419bfd03ca75d4`.
- Engine/extension versions: ERPNext 17 development / ATLASERP 0.3.0.
- Application image identity:
  `sha256:d0fbd186e568561aeb2062b869c94029c54838b55a332946cfa0286fb210474f`.
- Frontend image identity:
  `sha256:be1d9e77908d63fdef4e66d71c4026d9b349472049a4d513f7077987184e701c`.

This POS repair uses the verified UI release `atlaserp:7b4413e77e` and frontend
`atlaserp-frontend:7b4413e77e` as build parents. No schema migration was needed.
A full server-side backup was taken before rollout:
`20261006_210505-erp_atlasuse_site-*`. The previous environment is saved privately
as `.env.before-pos-65233c3cf3` in the server checkout.

The native POS now initializes new invoices with the company/profile from the
open cashier session before refreshing the form. Server-side profile defaults
also resolve the company before cash/change account lookup. This fixes startup
when the user's default company is ATLAS BITES and the session belongs to Street
Pizza (Demo), while keeping `Street Pizza Demo Cash` mapped only to `Cash - SPD`.

Build the app with `deploy/Dockerfile.pos-release` and its matching frontend with
`deploy/Dockerfile.frontend-pos-release`. After starting both images, run
`env/bin/python apps/erpnext/scripts/publish-pos-assets.py` from the backend bench
directory, then `bench --site erp.atlasuse.site clear-cache`. The helper backs up
the persistent asset manifest and updates only the POS bundle hash. It is safe
to rerun. For rollback, restore the private previous environment and
`sites/assets/assets.json.before-pos-repair`, restart the previous image pair
and clear the site cache.

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
- Socket.IO polling handshake and websocket upgrade succeed through CloudPanel.
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
interface, customer portal and read-only restaurant menu are delivered. Online
ordering, kitchen/table workflows, Moroccan accounting certification, custom
checkout, payment-provider integration and ATLASUSE synchronization remain pending. Follow [VPS operations](VPS.md) for updates
and backups, and the [roadmap](ROADMAP.md) for product work.
