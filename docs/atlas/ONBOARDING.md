# Milestone 1 — Companies, brands, branches and staff

ATLASERP 0.2 adds `/atlas-setup`, linked from the launchpad. A legal Company owns
brands; each brand has branches; each branch has a dedicated ERPNext Warehouse.
This records the business structure without creating POS profiles or changing taxes.

## User journey

1. An administrator completes ERPNext's initial setup and creates a legal Company
   through Company management. Select Morocco and MAD for a Moroccan business;
   the chart and taxes still need accountant review.
2. Select that company in Business & team. Create a Restaurant or Retail brand.
   Set its colour; upload/edit its logo through the saved brand's Desk form.
3. Create a branch with a unique company-wide code, city and address. The setup
   endpoint creates a separate warehouse automatically. Saved branch codes,
   brands and warehouses cannot be reassigned through an edit.
4. Assign an email account to a branch as Owner, Manager, Cashier or Waiter.
   Reusing an email/branch updates the assignment rather than duplicating it.
5. An administrator sets the new account's password through User management.
   Welcome email is disabled until mail delivery is configured. Creating an
   assignment does not send an invitation or automatically sign the staff member in.
6. Disable/re-enable an assignment to remove/restore its business access. Accounts
   retain a permission-free ATLAS Staff role so reactivation remains possible.

The page resumes from saved records. Existing branches and brands can be opened
in Desk. The interface currently uses English; French/Arabic translation remains
in the localization milestone.

## Access delivered in this milestone

| Account | Setup visibility | Changes |
| --- | --- | --- |
| System Manager | All companies and records | Legal company, brands, branches, team and account activation |
| ATLAS Owner | All brands, branches and team in assigned company | Brands, branches and team in that company |
| ATLAS Manager | Assigned branches and their brands; own assignments | Read only |
| ATLAS Cashier / Waiter | Assigned branches and their brands; own assignments | Read only |
| Guest / Website User | No setup access | None |

Record and list permission hooks enforce these scopes through UI and API. A role
alone does not grant access to every branch. One staff account belongs to one legal
company, including disabled assignments. Administrator/System Manager accounts
remain trusted site administrators. Existing broader ERP roles are not silently
converted into restricted staff accounts. Owners cannot disable their own final
owner assignment.

These roles grant business-structure permissions only. Checkout, stock operations,
prices, refunds, restaurant orders and financial ledgers need separate permissions
and lifecycle verification in the next milestone. Customer tenant provisioning and
country accounting compliance are not implemented by this setup feature.

## Verification

`scripts/check-onboarding.py` is restricted to disposable
`atlas-onboarding*.localhost` sites. It creates two Moroccan demo companies,
brands, branches, warehouses and staff in a rolled-back transaction. It checks
duplicate retries, invalid company/warehouse references, owner versus staff scope,
API mutation restrictions, guest denial and staff disable/re-enable behavior.

The test Compose project uses separate database, Redis and sites volumes and a
loopback-only frontend on port 8086. Desktop and 390px phone layouts were inspected;
the phone page has no horizontal overflow. Production receives schema and role
migrations only; test companies and staff are not inserted into the live site.

On 2026-10-06, the integration suite passed on the final candidate, including
direct Frappe client API read denial, protection of the final owner assignment,
and cross-company assignment rejection after disabling a user. Real HTTP checks
passed guest redirect/denial, Administrator login, template/asset delivery,
overview, missing-token rejection and validation with a valid CSRF token.

## Next bounded task

Configure a branch's catalog, selling price list, payment modes and POS Profile;
bind permitted cashiers and the branch warehouse. Then verify opening cash,
cash sale, receipt, return and closing against ERPNext's stock and ledger records.
Restaurant tables, kitchen tickets and ingredient recipes follow that cash-sale
foundation.
