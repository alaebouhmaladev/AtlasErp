# ATLASERP VPS deployment

This deploys the current development baseline for evaluation. It is not yet
validated for real retail transactions or Moroccan accounting compliance.

## Layout

- Repository: `https://github.com/alaebouhmaladev/AtlasErp.git`, branch `dev`.
- VPS checkout: `/home/alaebhm/atlaserp/source`.
- Compose project: `atlaserp-vps`, configuration: `compose.vps.yaml`.
- CloudPanel domain: `erp.atlasuse.site`, upstream: `http://127.0.0.1:8085`.
- Nginx serves built assets and forwards HTTP to Gunicorn and realtime requests
  to Socket.IO. Workers and scheduler run in separate containers.
- Database, sites, logs and queue have separate persistent Docker volumes.
- Application containers use built images, with no source bind mounts.
- Frappe build ref for this baseline: `459a849fa6e97510d00f260022419bfd03ca75d4`.

## Initial build

Run from the VPS checkout. Generate a private `.env` with `ATLAS_SITE`,
`ATLAS_HTTP_PORT`, `ATLAS_IMAGE`, `ATLAS_FRONTEND_IMAGE`, `DB_ROOT_PASSWORD`, and
`ADMIN_PASSWORD`. Use unique randomly generated passwords, file mode `0600`.
Do not copy your laptop's credentials.

```sh
docker build --build-arg FRAPPE_REF=459a849fa6e97510d00f260022419bfd03ca75d4 \
  -t "$ATLAS_IMAGE" .
docker build -f deploy/Dockerfile.frontend \
  --build-arg ATLAS_IMAGE="$ATLAS_IMAGE" -t "$ATLAS_FRONTEND_IMAGE" .
docker compose -f compose.vps.yaml up -d
docker compose -f compose.vps.yaml ps -a
```

Export the image variables from your private `.env` before running the build
commands; Compose reads `.env` automatically. Images are tagged with the source
commit. Base images and Python/npm dependency resolution are not yet fully
digest/lock pinned, so rebuilds are not claimed to be byte-for-byte identical.

The one-shot setup container creates the site, installs ERPNext and the ATLASERP
extension, applies migrations, disables developer mode, and enables the scheduler.
Inspect its logs if it exits with an error. Do not delete database/site volumes to
repair a failed installation.

## CloudPanel and verification

Point the domain's A record to the VPS. CloudPanel must forward the original Host,
HTTPS scheme, and websocket upgrade headers. Install a valid TLS certificate
through CloudPanel before entering credentials. Keep port 8085 bound to loopback.

Check `/login`, `/atlas`, the logo/CSS, websocket polling and Administrator login.
Guest access to `/atlas` must redirect to login. Complete company and POS setup
before checking transactions; the launchpad alone does not validate retail flows.

## Updates and backups

Before updating, run a backup including public/private files:

```sh
docker compose -f compose.vps.yaml exec backend \
  bench --site erp.atlasuse.site backup --with-files
```

Backups are inside the sites volume under the site's `private/backups` directory.
Copy them to protected off-server storage along with the site configuration and
encryption key. Verify a restore on an isolated site before relying on backups.
Automated off-server backups remain to be configured.

Build new commit-tagged images, update image names in `.env`, and run Compose to
recreate the services and setup container. Review migration compatibility first;
switching to an older image does not reverse database migrations. Never run
`docker compose down -v` on a site with data.

For extension-only updates with unchanged ERPNext/Frappe and compiled assets, use
`deploy/Dockerfile.release` with the previously verified app image as `BASE_IMAGE`
and `deploy/Dockerfile.frontend-release` with its frontend as `BASE_FRONTEND`.
These replace the ATLASERP extension and its plain public assets. Engine/dependency
or compiled-bundle changes require the full build instead. Record the parent image
and source commit with every release. Run only one Compose update at a time on a
project so competing setup containers cannot interrupt migrations.
