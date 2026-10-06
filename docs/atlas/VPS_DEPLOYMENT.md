# Verified VPS deployment

## Installed release

- Public site: `https://erp.atlasuse.site`.
- Server: Debian 12 at `85.190.254.196`; deployment uses the existing `alaebhm`
  SSH account and its Docker access.
- Checkout: `/home/alaebhm/atlaserp/source`, GitHub `origin/dev`.
- Compose configuration includes corrections through commit `f0e6da6b81`.
- App image: `atlaserp:27f4575e30`, extension release from source commit `27f4575e30`.
- Frontend image: `atlaserp-frontend:27f4575e30`.
- Frappe source: `459a849fa6e97510d00f260022419bfd03ca75d4`.
- Engine/extension versions: ERPNext 17 development / ATLASERP 0.2.0.
- Application image identity:
  `sha256:87ab9421b907da883c7fcb9561f1c67511d5a57a3da1b42383b50a2a79502aed`.
- Frontend image identity:
  `sha256:c1dcb9111df591b43dde0cb4b84c8fcea7f2b414d380853c5b3a7c8c640c1de7`.

This extension-only release keeps the verified engine image `atlaserp:bbbded28064e`
and frontend `atlaserp-frontend:7f7cc8c1e2d6` as build parents. Schema migration
completed successfully on staging and production. A new full server-side backup
was taken before migration: `20261006_194557-erp_atlasuse_site-*`.

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
  isolated site. The live site's existing company remains; no demo records were deployed.

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
tests remain to be completed. No Moroccan
accounting certification, custom checkout, payment-provider integration or
ATLASUSE synchronization is claimed. Follow [VPS operations](VPS.md) for updates
and backups, and the [roadmap](ROADMAP.md) for product work.
