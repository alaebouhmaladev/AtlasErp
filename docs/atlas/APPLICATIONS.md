# Installed business application suite

Requested on 2026-10-06: add applications beyond the ERP engine, beginning with
HRMS and CRM. Exact upstream revisions and install order are recorded in
[deploy/app-suite.json](../../deploy/app-suite.json). Deployment verification will
be recorded below after staging checks and live installation finish.

## Verification

Staging passed on 2026-10-06 with ATLASERP 0.4.0:

- Installation and full migration of HRMS, WhatsApp and CRM completed.
- Native launcher exposes ATLASERP, ATLAS HR, ATLAS CRM and Administration;
  the workspace exposes 21 permitted operational categories for Administrator.
- Employee lists and the CRM leads interface render; HR and CRM built assets
  return successfully. The temporary SSH tunnel has a different browser origin
  from the configured staging domain, so realtime is checked on the live domain.
- Guest private-record access is denied; Website User and Sales User launchpad
  checks pass. Existing roles and document access checks are preserved.
- POS company/cash/change/receivable defaults pass for both invoice types.
- Company, menu, price, POS profile and transaction counts are unchanged.
  Existing customer portal, shared Desk assets and the 63-item menu checks pass.

Live installation and verification are pending.

## Applications and tools

| Application | User destination | Scope |
| --- | --- | --- |
| ATLASERP | `/atlas`, with native Desk operations | POS, sales, customers, purchasing, stock, payments, accounting, projects, assets, manufacturing, quality, support, maintenance and subscriptions |
| ATLAS HR (Frappe HRMS) | App launcher, HR setup and employee workflows | Employees, attendance, leave, recruitment, expenses and payroll |
| ATLAS CRM (Frappe CRM) | `/crm` | Leads, deals, organizations, contacts and sales activities |
| WhatsApp integration dependency | CRM integration settings | Package required by this CRM revision; no provider account is connected by installation alone |

The native launcher gets its entries from installed apps and their permission
checks. ATLAS labels preserve internal package IDs and access gates. The `/atlas`
workspace also lists permitted installed applications and operational tools.
CRM's supported branding settings receive the ATLAS CRM name, logo and favicon;
currency, provider credentials and permission settings are separate.
Missing optional doctypes are omitted; links do not grant users new roles or
document access. The companion extension remains a single product experience.

Installation does not migrate ATLASUSE CRM customers/deals, configure provider
credentials, import employees, send messages, or run payroll. Moroccan payroll,
tax/social contribution rules and actual employee structures require a separate
configuration and validation task. Mobile POS and kitchen/customer-screen apps
remain separate development projects described in [MOBILE_POS.md](MOBILE_POS.md).

## Image and installation process

Build the app image with `deploy/Dockerfile.app-suite`, then the matching frontend
with `deploy/Dockerfile.frontend`. The image fetches pinned official upstream
revisions, installs their declared dependencies and builds the app frontends.
Use `deploy/compose.app-suite.yaml` with `compose.vps.yaml` to opt into schema
installation in dependency order: HRMS, WhatsApp, CRM. The ordinary setup script
preserves all app packages present on the bench in `sites/apps.txt`.

After setup completes, publish the optional bundle keys with
`env/bin/python apps/erpnext/scripts/publish-app-suite-assets.py` and clear the
site cache. Existing ERP/POS asset keys are preserved. All backend, worker,
scheduler and websocket services must run the same candidate image.

Before a live schema install, take database/public/private/config backups, save
the previous environment privately, and test installation/migration on the
isolated staging site. App installation adds doctypes, roles, defaults and hooks.
Rollback of a schema installation requires the matching pre-install site backup
and old image pair; reverting only the image is insufficient.

Check `scripts/check-app-suite.py`, launchpad guest/website/sales-role access,
existing POS company/payment defaults, new app HTTP/assets and real launcher/app
screens. Do not treat a successful Docker build as a successful app install.

## Upstream references

- [Frappe HRMS source](https://github.com/frappe/hrms)
- [Frappe CRM compatibility and installation](https://github.com/frappe/crm#compatibility)
- [Frappe WhatsApp source](https://github.com/frappe/whatsapp)

Upstream source identifiers, licenses and copyright notices remain intact.
Additional ecosystem apps such as Helpdesk, Insights, Drive, Learning and Builder
need their own dependency, shared-site compatibility, storage and access checks
before installation; they are not included or represented as installed here.
