<div align="center">
  <img src="apps/atlas_erp/atlas_erp/public/images/atlas-wordmark.svg" alt="ATLASERP" width="228" height="48">
  <h1>ATLASERP</h1>
  <p>Business management for Morocco and African markets.</p>
</div>

ATLASERP brings retail checkout, products, inventory, purchasing, payments and
accounting into one workspace. Our first product scope focuses on Moroccan retail
and restaurants, with an Android tablet POS planned before iOS; later releases
add other industries and country packs.

## Current status

The live evaluation build includes ATLASERP, ATLAS HR (HRMS) and ATLAS CRM, on the
inherited ERPNext/Frappe 17 development baseline. The workspace exposes 21 business
tool categories according to user permissions. Branding, company/branch/team setup,
the customer portal and Street Pizza demo catalog are delivered. Existing ERP
workflows power checkout and accounting. Moroccan localization/payroll configuration,
native mobile checkout and ATLASUSE CRM synchronization remain upcoming milestones.

Open [the live workspace](https://erp.atlasuse.site/atlas) or
[the application launcher](https://erp.atlasuse.site/desk).

## Start locally

With Docker Desktop running:

```bash
bash scripts/dev.sh init
bash scripts/dev.sh up
```

Open [ATLASERP](http://localhost:8000/atlas). Sign in as `Administrator` using
`ADMIN_PASSWORD` from your private `.env`, then complete company and shop setup.
Never commit or publish this file.

See [the setup guide](ATLASERP.md) for commands, prerequisites and development limits.

## Build part by part

- [Complete roadmap](docs/atlas/ROADMAP.md)
- [Small development tickets](docs/atlas/BACKLOG.md)
- [Android/iOS POS product plan and small delivery tasks](docs/atlas/MOBILE_POS.md)
- [Architecture](docs/atlas/ARCHITECTURE.md)
- [Business applications, versions and installation](docs/atlas/APPLICATIONS.md)
- [UI and UX direction](docs/atlas/UX.md)
- [Country localization](docs/atlas/LOCALIZATION.md)
- [Branding implementation and verification](docs/atlas/BRANDING.md)

## Open-source foundation

ATLASERP is an independent product built on [ERPNext](https://github.com/frappe/erpnext)
by Frappe Technologies and contributors, and the [Frappe Framework](https://github.com/frappe/frappe).
ERPNext's GPL v3 license, copyright notices and internal application identifiers
are preserved. See [license.txt](license.txt), [trademark policy](TRADEMARK_POLICY.md)
and the [archived upstream README](docs/upstream/ERPNext_README.md).
