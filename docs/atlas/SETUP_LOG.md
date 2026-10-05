# Foundation verification — 5 October 2026

## Installed local environment

- Inherited ERPNext fork: `17.0.0-dev`, baseline repository commit `20a82b8bd9`.
- Frappe: `17.x.x-develop`, fetched commit `459a849fa6e97510d00f260022419bfd03ca75d4`.
- ATLASERP extension: `0.1.0`.
- Image built during setup: `atlaserp-dev:local` (initial digest
  `sha256:32e3cd94a6c9f3b47bf832ea7022e617814e086eba6179518f0d035e92ac84fa`).
- Runtime assets built successfully for `frappe,erpnext,atlas_erp` after source mounts.
- Site: `atlas.localhost`; MariaDB 11.8 and Redis 7; app/DB/cache/queue running.
- Host ports: `127.0.0.1:8000` and `127.0.0.1:9000`; no database/cache host ports.
- `.env` generated privately with file permissions `0600`; credentials excluded
  from source control and image context.

## Checks passed

| Check | Result |
| --- | --- |
| Python syntax / Bash syntax / `git diff --check` | Passed |
| Template rendering for en/fr/ar language direction | Passed; translations themselves remain future work |
| User-name escaping and no-access empty state | Passed in template checks |
| Guest request to `/atlas` | Redirects to login |
| Administrator login and `/atlas` response | HTTP 200 with POS and item navigation |
| CSS and SVG | Served successfully |
| Website User | Denied the internal launchpad |
| Sales User | Customer navigation available; journal-entry navigation absent; setup action absent |
| Service restart | Existing site/apps remain installed; login/HTTP checks pass afterward |
| Desktop visual check | Rendered launchpad reviewed at the browser's default viewport |
| Phone layout | Rendered launchpad checked at 390px; document width equals viewport width |

HTTP checks use `scripts/check-local.py`. Database permission checks use
`scripts/check-permissions.py`; temporary test users are rolled back and their
caches cleared. Visual checks used an exact captured authenticated HTML response
with actual local assets, served temporarily on localhost. This avoids passing
credentials into the UI automation. Screenshot: `.atlas/launchpad.jpg` (ignored
local artifact). The temporary preview server is stopped after verification.

## Changes needed during setup

Fixed copied Node image's broken Yarn symlinks, installed Yarn explicitly,
corrected multi-app asset selection to `--apps frappe,erpnext,atlas_erp`, kept
dependency directories in the image while mounting ERPNext source, and bound the
container's web server to `0.0.0.0` while retaining localhost-only host ports.

The image above predates the final Dockerfile multi-app build correction; its
runtime startup executed the corrected full asset build successfully. Future
image builds use the corrected Dockerfile command. Neither that image nor this
moving development baseline is a pinned production artifact.

## Limits and next work

Company setup, Retail domain, warehouse, POS profile and cashier configuration
still need the pilot shop's details. No business transactions were created or
retail posting correctness claimed. No custom checkout, Moroccan tax rules,
accounting certification or ATLASUSE sync has been implemented.

The initial Frappe site leaves the scheduler disabled. The schedule process and
queue worker run, but scheduled site jobs need an explicit development decision
to enable them. Email and external payment providers are not configured.
Tablet task usability, full translation, screen-reader review, transaction
lifecycle tests, stable baseline and backup/restore are later acceptance gates.
