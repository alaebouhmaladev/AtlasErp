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

Local development foundation, built on the inherited ERPNext/Frappe 17 development
baseline. ATLASERP branding covers sign-in, the launcher, navigation, website
identity and email footer text. Existing ERP workflows power the operational
screens. Moroccan localization, a redesigned checkout and ATLASUSE CRM integration
are upcoming milestones, not completed features.

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
