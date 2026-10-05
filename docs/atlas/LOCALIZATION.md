# Morocco and African country packs

This is a research/implementation checklist, not a statement of current legal
requirements. Do not hard-code tax rates or claim compliance from this document.

## Morocco validation register

| Topic | Candidate scope | Required evidence / acceptance |
| --- | --- | --- |
| Business identity | ICE, IF, RC, registration city and relevant TP data | Accountant confirms meanings, formats and document use |
| Accounting | Moroccan chart of accounts and mappings | Accountant-approved chart and balanced posting examples |
| TVA / taxes | Tax categories, regimes, rounding and effective dates | Applicable DGI sources plus accountant sign-off |
| Invoices / receipts | Identifiers, numbering, language, totals and credit notes | Reviewed source requirements and approved print examples |
| Retail cash | POS opening/closing, variance, refunds and audit trail | Shop process review and reconciled posting tests |
| Payments / banking | Cash, manual card recording, reconciliation, provider integration | Bank/provider documentation and sandbox verification |
| Payroll | Employment, CNSS, income tax and other applicable obligations | Separate qualified payroll review before implementation |
| Privacy / hosting | Customer/employee data, retention, access and transfers | Applicable CNDP guidance and a reviewed deployment policy |
| Electronic invoicing | Applicability, format, reporting, effective dates | Verify current official rules before implementing a connector |
| Language / time | French, Arabic/RTL, English, MAD, Africa/Casablanca | Reviewed translations, currency/date and timezone tests |

The inherited repository includes a Morocco chart under
`erpnext/accounts/doctype/account/chart_of_accounts/unverified/`.
Treat it as a candidate requiring review, not as certified localization.

For each implemented rule record: jurisdiction, business regime, official source
URL, reviewed date, effective date, responsible reviewer, configuration/patch,
regression examples and sign-off. Useful primary-source starting points:
[DGI](https://www.tax.gov.ma/), [CNDP](https://www.cndp.ma/),
[CNSS](https://www.cnss.ma/), [Bank Al-Maghrib](https://www.bkam.ma/).
These links are research entry points; their contents have not yet been evaluated
for this product's compliance requirements.

## Country pack contract

Each pack declares supported countries, currency, languages, timezone, chart,
tax configuration with effective dates, identity fields, document templates,
exports/connectors, migrations and test cases. Company/pack configuration should
be explicit, avoid changing existing posted transactions and avoid overwriting
customer settings during upgrades.

Common UX and ERP engine stay shared. Tax, invoice, accounting and payment rules
belong to named country packs. Start the next-country discovery with real retail
customers and a local accounting reviewer; country order remains undecided.
