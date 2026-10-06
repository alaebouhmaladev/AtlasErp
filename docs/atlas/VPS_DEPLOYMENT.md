# Verified VPS deployment

## Installed release

- Public site: `https://erp.atlasuse.site`.
- Server: Debian 12 at `85.190.254.196`; deployment uses the existing `alaebhm`
  SSH account and its Docker access.
- Checkout: `/home/alaebhm/atlaserp/source`, GitHub `origin/dev`.
- Compose configuration includes corrections through commit `f0e6da6b81`.
- App image: `atlaserp:bbbded28064e`, built from source commit `bbbded28064e`.
- Frontend image: `atlaserp-frontend:7f7cc8c1e2d6`.
- Frappe source: `459a849fa6e97510d00f260022419bfd03ca75d4`.
- Engine/extension versions: ERPNext 17 development / ATLASERP 0.1.0.
- Application image identity:
  `sha256:fcb44b9a1f1e82fd5cc7b5d7d4285ab9e814a8617c01cb813e29a0bc30230358`.
- Frontend image identity:
  `sha256:3d59d412dbf09ff3fb2451f8679c39c71a26bc04857e3b7c4672a3b4569d16a3`.

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

## Backup and credentials

An initial backup of the database, public/private files and site configuration
was created under `sites/erp.atlasuse.site/private/backups` in the sites volume.
An off-server copy has not been performed. Automated backups and a restore drill
remain to be configured before relying on this deployment for real shop data.

Server credentials are in the private checkout `.env`. A local Administrator
login reference is saved in ignored `.atlas/vps-login.txt`, file mode `0600`.
Neither credentials nor backups belong in GitHub.

## Product limits

This is the current evaluation build. Company setup, warehouse, cashier roles,
POS profile and retail transaction tests remain to be completed. No Moroccan
accounting certification, custom checkout, payment-provider integration or
ATLASUSE synchronization is claimed. Follow [VPS operations](VPS.md) for updates
and backups, and the [roadmap](ROADMAP.md) for product work.
