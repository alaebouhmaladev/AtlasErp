# ATLAS POS register entry — 0.4.1

The first Square benchmark delivery is a guided **online** register entry screen
at `/atlas-pos`. It improves the existing ERP checkout; it is not an Android
application or an offline checkout. It implements MOB-01A, part of the larger
register-readiness milestone in [MOBILE_POS.md](MOBILE_POS.md).

## Cashier workflow

1. Sign in with the internal account assigned to the register, then open
   [ATLAS POS](https://erp.atlasuse.site/atlas-pos).
2. Choose the register for the correct company and branch warehouse.
3. **Open checkout** starts the native opening dialog. **Resume checkout** opens
   the cashier's existing session. Neither link posts an opening balance or sale.
4. Check the opening float, then submit it yourself when starting a shift.
   In the ATLAS handoff, company and profile stay fixed; **Change register**
   returns to register selection. Opening amounts use the company's accounting
   currency, including MAD for Street Pizza, rather than the global default.

A register used by another cashier requires normal closing or manager handover.
The entry page explains this and never cancels somebody's session. Multiple open
sessions and a cashier already using a different register require review.

For the current Street Pizza demo, the existing ATLAS cashier account
`alae@atlasbites-maroc.com` has a resumable shift. Administrator sees **In use**
while that other account owns the shift. Sign in with the assigned cashier to
resume it; changing accounts does not transfer ownership of an opening entry.

## Checks and access

The screen checks profile enablement, explicit cashier assignment, native opening
and invoice create/submit permissions, company warehouse, enabled selling price
list, configured currency, exactly one default tender, each tender's enabled
company Cash/Bank account, the cash change account and open sessions.

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
  own-session resume, busy/conflicting sessions and guest denial. Optional staging
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
