# ATLAS POS register entry — 0.4.2

The first Square benchmark delivery is a guided **online** register entry screen
at `/atlas-pos`. It improves the existing ERP checkout; it is not an Android
application or an offline checkout. It implements MOB-01A, part of the larger
register-readiness milestone in [MOBILE_POS.md](MOBILE_POS.md).

## Cashier workflow

1. Sign in with the internal account assigned to the register, then open
   [ATLAS POS](https://erp.atlasuse.site/atlas-pos).
2. Choose the register for the correct company and branch warehouse.
3. **Open checkout** starts the native opening dialog. **Resume checkout** opens
   the cashier's existing current-day session. Neither link posts an opening balance or sale.
4. Check the opening float, then submit it yourself when starting a shift.
   In the ATLAS handoff, company and profile stay fixed; **Change register**
   returns to register selection. Opening amounts use the company's accounting
   currency, including MAD for Street Pizza, rather than the global default.

A register used by another cashier requires normal closing or manager handover.
The entry page explains this and never cancels somebody's session. Multiple open
sessions and a cashier already using a different register require review.

The engine currently requires an opening dated today in the site's timezone.
Version 0.4.2 checks this before offering checkout: an old or future-dated shift
blocks resume and shows **Shift needs closing** for its owner. An authorized
operator can choose **Review shift closing**, which opens an unsaved native form
for that opening, company/profile and cashier. It does not save or submit it.
Review linked sales and enter the actual counted cash before submitting yourself.
Operators without opening-read and closing-read/create access get no closing link.

The current Street Pizza demo shift `POS-OPE-2026-00002`, owned by
`alae@atlasbites-maroc.com`, opened on 6 October at 21:32. It contains one submitted
301 MAD sale and 1,500 MAD opening cash; expected cash is 1,801 MAD. On 7 October
the user explicitly chose to keep the shift unchanged. It remains open and its
sale is preserved. Administrator sees **In use** while the cashier owns it.
Changing accounts does not transfer ownership of an opening entry.

Restaurant overnight shifts need a separately specified business-day policy and
matching invoice validation. This fix follows the existing engine date rule; it
does not bypass it, alter posting dates or automatically close a shift at midnight.

## Checks and access

The screen checks profile enablement, explicit cashier assignment, native opening
and invoice create/submit permissions, company warehouse, enabled selling price
list, configured currency, exactly one default tender, each tender's enabled
company Cash/Bank account, the cash change account, open sessions and their dates.

Guests, Website Users and disabled accounts are rejected. Non-administrators need
native POS Profile record access and explicit cashier assignment. Accounts using
ATLAS staff roles also need an enabled matching company/branch/brand assignment
with an Owner, Manager or Cashier role. Existing explicitly assigned native ERP
operators keep their native permission rules. Administrators can inspect profiles
but still need cashier assignment to enter checkout.

Repair links appear only for authorized managers with native record write access.
The response does not expose another cashier's identity or raw accounting rows.
The GET register-context endpoint rechecks these rules at checkout and returns
the company from the profile. URL parameters cannot choose a different company.

This is an entry guard, not a replacement for native transaction authorization.
Concurrent opening protection and company/branch enforcement through every
existing ERP API remain release gates. The UI check cannot guarantee that setup
or another cashier's session will not change before the user submits.

## Verification

- `node scripts/test-pos-startup.mjs`: native defaults, verified handoff, rejected
  handoff, changed-session guard, constructor-time Link lookup, fixed register and
  opening currency/amount payload.
- `scripts/check-pos-readiness.py`: read-only checks, missing payment mapping,
  current-day resume, old/future shift rejection through the context API, scoped
  closing links, busy/conflicting sessions and guest denial. Optional staging
  fixtures test Website User, unassigned/assigned native users and wrong ATLAS
  scopes; writes are rolled back and caches cleared.
- `scripts/check-pos-readiness-http.py`: guest gates, authenticated HTML/API/CSS
  and forged register rejection, using credentials from a private environment.
- `scripts/check-pos-company.py`: both native invoice types initialize the
  profile's company and cash/change/receivable accounts without posting.
- Browser checks: tablet and phone entry layout without horizontal overflow;
  selected Street Pizza company/profile, MAD opening amount and Change register.

Tests do not submit live financial documents. Deployment evidence, backup and
image identities are recorded in [VPS_DEPLOYMENT.md](VPS_DEPLOYMENT.md).

## Next work

Complete scoped register provisioning, native endpoint authorization and opening
concurrency before declaring phase 0 complete. Then deliver the Android online
cash workflow with idempotent posting, receipts, returns and closing. Durable
offline cash is mandatory before a commercial pilot; the same-router shop hub,
table/waiter/kitchen devices and provider payments follow their separate gates in
[SQUARE_BENCHMARK.md](SQUARE_BENCHMARK.md).
