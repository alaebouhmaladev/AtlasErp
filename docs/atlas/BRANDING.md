# ATLASERP branding

The product owner requested replacing the visible ERPNext identity with ATLASERP
on 5 October 2026. This is a product rebrand; financial/stock behavior and upstream
application identifiers are preserved.

## Brand surfaces

| Surface | Implementation |
| --- | --- |
| Sign-in name, browser title and logo | Website/System Settings; website context hook |
| Login colors and card | `public/css/brand.css`, scoped to the login page |
| Favicon / splash / website header | ATLASERP mark/wordmark and website settings |
| ERP launcher and sidebar app title | Bounded metadata patch in `erpnext/hooks.py` |
| Companion app | Supplies hooks/assets without a duplicate launcher entry |
| Desk logo and help | Navbar Settings; About ATLASERP and guide routes |
| Framework administration label | Boot display metadata; app ID and permission checks preserved |
| Launchpad footer | Business-tools link and About ATLASERP |
| Existing desktop icons | Presentation fields updated; record IDs/references preserved |
| Shop floor | Branded icon and accessible label |
| Operational help and notification text | Small display-string patches only |
| Standard email footer | ATLASERP product text; sending configuration unchanged |
| Repository front page | ATLASERP README; original README archived separately |
| Open-source credits | `/atlas-about`, source licenses and copyright notices |

`atlas_erp.branding.apply_branding` runs after app install/migration and can be
called explicitly on an existing site:

```bash
bash scripts/dev.sh bench --site atlas.localhost execute atlas_erp.branding.apply_branding
bash scripts/dev.sh bench build --apps erpnext,atlas_erp
bash scripts/dev.sh bench --site atlas.localhost clear-cache
```

The routine deliberately maintains ATLASERP product defaults. It writes only
branding/default-launcher fields and help menu entries; it does not set company,
currency, taxes, system language or timezone. Presentation-only single fields use
the framework database API with cache invalidation, so branding can be applied
before the company wizard supplies mandatory system settings. Navbar documents
still use ordinary validated saves. Re-running does not duplicate product help entries.

## Upstream patches to carry during upgrades

`erpnext/hooks.py`: product title/description/logo/landing route, favicon/splash
and standard email footer. The Python package remains `erpnext`, publisher/license
metadata retain upstream attribution, and source references remain intact.

`erpnext/setup/install.py`, `setup/utils.py`, `startup/__init__.py` and the sample
blog template: initial/fallback product display names. `stock/reorder_item.py`:
notification subject. Item, buying settings, bank-account and shop-floor scripts:
display labels only. Payment-setup template: page title. No ledger logic changes.
Standard icon/sidebar/workspace JSON updates change display titles and labels;
names, module IDs, parent-icon references and `link_to` values remain unchanged.
Item help and employee user-ID labels are updated in both source metadata and
the existing site's DocField records.

Do not run a repository-wide replacement of `erpnext` or `frappe`: these names
identify installed apps, modules, doctypes, API methods, historical patches and
dependencies. Technical/version information and legacy migration warnings may
still mention upstream components. Those references must remain accurate.

## Verification

- `scripts/check-local.py`: guest redirect, administrator login, launchpad and assets.
- `scripts/check-branding.py`: persisted identity, logos, one ATLASERP launcher
  with the preserved engine ID, and product About/help metadata.
- `scripts/check-permissions.py`: guest/internal/website and role restrictions.
- Browser review: live sign-in, responsive launchpad and onboarding branding.

SMTP delivery, real receipt-printer output, translated interface strings and all
industry modules are separate acceptance work. Rebranding does not mean the
complete UI/UX redesign or Moroccan localization is finished.

## Local results

On 5 October 2026, the ERP/ATLASERP asset build passed. The live sign-in page has
the ATLASERP wordmark, favicon, theme and `ATLASERP - Login` browser title with no
upstream sign-in logo. Launcher settings checks passed, showing one ATLASERP
entry with the existing `erpnext` internal ID. Guest redirect, administrator
login, website-user rejection and Sales User access checks passed. About and
guide page rendering are checked separately, including the About version value.
The source licenses and upstream publisher metadata remain preserved.
