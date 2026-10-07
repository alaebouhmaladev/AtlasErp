# ATLASERP

An ERPNext-based business system for Morocco, with country-specific expansion to
African markets. **First pilot: retail shops and point of sale**, selected by the
product owner on 5 October 2026. ATLASUSE remains the existing CRM product.

## Current foundation

- This repository already is an ERPNext fork; upstream Python packages remain `erpnext`.
- The existing code reports `17.0.0-dev` and requires Python 3.14 and matching Frappe 17.
- `apps/atlas_erp/` contains the new ATLASERP Frappe extension and an authenticated,
  responsive `/atlas` launchpad. It opens existing ERPNext tools according to user permissions.
- `compose.yaml` provides a local development bench, MariaDB and two Redis services.
- Country localization, custom checkout and CRM synchronization are **planned**, not implemented.

## Run locally

Install/start Docker Desktop, then from this repository:

```bash
bash scripts/dev.sh init
bash scripts/dev.sh up
bash scripts/dev.sh logs
```

The first image build downloads Frappe and dependencies and can take several minutes.
Wait until logs show the web server running; site creation and ERPNext installation
run before the server starts. Open <http://atlas.localhost:8000/atlas> (or
<http://localhost:8000/atlas> with the default site). Sign in as `Administrator`
using `ADMIN_PASSWORD` from the private local `.env`. Never commit this file.

Complete ERPNext's company setup wizard in <http://atlas.localhost:8000/desk> before
creating business transactions. Select Morocco and MAD during company setup.
Enable the Retail domain and configure a POS profile before using checkout.
The launchpad does not set company defaults, install tax rates, or certify accounting compliance.

```bash
bash scripts/dev.sh status
bash scripts/dev.sh stop
bash scripts/dev.sh bench --site atlas.localhost migrate
bash scripts/dev.sh bench build --app atlas_erp
bash scripts/dev.sh bench --site atlas.localhost clear-cache
python3 scripts/check-local.py
docker compose exec app env/bin/python /workspace/scripts/check-permissions.py
```

The `erpnext/` package and ATLASERP app are mounted from this folder; root package
metadata and the existing banking SPA are copied into the image and need an image
rebuild after edits. CSS/template changes can be reloaded;
clear the site cache when necessary. Use `migrate` after schema/fixture changes.
The development process deliberately omits an asset watcher; run `bench build`
after bundle changes. Rebuild the image after dependency changes.

Named volumes preserve database, sites and logs across stops. Do not remove
volumes to fix an installation failure: inspect logs and rerun startup first.
Passwords in `.env` must stay consistent with the initialized database; changing
an environment value alone does not rotate an existing MariaDB password.

This configuration is for a developer's machine. Ports bind to localhost. It is
not a production server: development mode, moving Frappe branch and development
server processes are intentional. Production deployment has its own roadmap gate.

## Work part by part

1. [Roadmap and complete module scope](docs/atlas/ROADMAP.md)
2. [Architecture and upgrade strategy](docs/atlas/ARCHITECTURE.md)
3. [Small development tickets and acceptance criteria](docs/atlas/BACKLOG.md)
4. [UI and UX direction](docs/atlas/UX.md)
5. [Morocco research and African country packs](docs/atlas/LOCALIZATION.md)
6. [Local setup verification and known limits](docs/atlas/SETUP_LOG.md)
7. [ATLASERP branding](docs/atlas/BRANDING.md)
8. [Square capability benchmark and seven delivery releases](docs/atlas/SQUARE_BENCHMARK.md)
9. [Delivered POS register entry and cashier guide](docs/atlas/POS_READINESS.md)

Keep one small workflow in development at a time. Every completed ticket needs a
demonstrable outcome, appropriate verification and updated notes before the next.

## Upstream and attribution

ERPNext is provided by Frappe Technologies. Preserve `license.txt`, upstream
copyright notices and `TRADEMARK_POLICY.md`. ATLASERP is our product identity;
upstream project/package identities stay intact. Review distribution obligations
and branding policy before a public product release.

Primary technical references: [Frappe apps](https://docs.frappe.io/framework/user/en/basics/apps),
[Frappe hooks](https://docs.frappe.io/framework/user/en/python-api/hooks),
[official Frappe Docker](https://github.com/frappe/frappe_docker).
