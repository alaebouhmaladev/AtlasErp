# Street Pizza menu dataset

Source: [streetpizza.ma](https://streetpizza.ma/), retrieved 2026-10-06. All nine
category lists and all 63 product detail dialogs were inspected. Names,
descriptions and displayed MAD prices are preserved in `menu.json`.

| Website category | Items |
| --- | ---: |
| STREET FORMULES | 3 |
| NOS PIZZAS NAPOLITAINES — AU FEU DE BOIS — | 21 |
| NOS PÂTES | 5 |
| NOS CRÉATIONS & SANDWICHS | 6 |
| NOS BURGERS | 4 |
| NOS SALADES FRAÎCHES | 6 |
| NOS DESSERTS | 4 |
| NOS BOISSONS | 9 |
| JUS FRAIS | 5 |
| Total | 63 |

Public business details: Street Pizzeria Napoletana; Angle Boulevard Roudani et
Rue du Louvre, Maarif, Casablanca; phone 0657572308; displayed hours 12:00–23:55.
Opening days are not specified. Legal company name, ICE, IF, RC, tax regime,
recipes with quantities, actual opening stock and staff identities are unknown.
No values are invented for those fields.

The three formulas retain nine required-choice groups. The Trio includes a
Frutti di Mare Premium choice which the Duo does not offer. Source spelling
differences such as “LA DIAVOLA PEPERONI” in deals and “LA DIAVOLA PEPPERONI” in
the catalog are retained. “Eau Gazeuse” and “Frites” are choices without a
separate public item price; they are not invented as separately priced items.

## ERP import

`scripts/seed-streetpizza.py` accepts this JSON and creates a **Street Pizza (Demo)**
company, restaurant brand, Casablanca Maarif branch, dedicated warehouse, nine
child item groups under Street Pizza Menu, 63 non-stock selling items and their
MAD Item Prices. It also creates a walk-in demo customer, a separate company-linked
cash payment method and an Administrator-only demo POS Profile and receipt.

The importer is restricted to explicit `ATLAS_SEED_MODE=demo`. Its legal-company
name cannot be mistaken for a verified legal identity. It does not rename ATLAS
BITES, grant new staff permissions, change global POS posting mode, import tax
rates, create opening cash, post sales, or fabricate inventory. The generic chart
is for demonstration and has not been validated for this business's legal regime.
If no active fiscal year applies, it creates a calendar-year fiscal period linked
only to the demo company. That period is an explicit demo assumption.

Displayed prices are copied exactly; the website does not establish a verified
tax-inclusive/exclusive breakdown. Demo receipts explicitly state that they are
not valid fiscal invoices. All products use Nos and no stock posting, pending
real portion/pack sizes, recipes and inventory inputs.

Required choices are preserved both as structured JSON in the read-only Item
field `atlas_menu_options` and readable Item descriptions. Native POS currently
does not render or enforce a meal-deal selector: the custom restaurant checkout
must use this data to enforce selections. Counter/table/kitchen workflows are
still separate development tasks.

Repeat imports check record identities and update only this catalog's descriptions,
source metadata and prices. Conflicting item codes, company configuration,
price lists or POS references abort the import. Existing real businesses remain
outside its scope. The public catalog can be committed to Git; future private
legal/account or employee data must stay out of this dataset.

## Verification

Run `scripts/check-streetpizza.py` only on an isolated
`atlas-onboarding*.localhost` site. It checks repeat-import counts, all 63 native
POS item prices/names, option groups, a fictional cash sale and its balanced
ledger, and the demo receipt. Transaction checks roll back; no sales or till
openings are added to the live site by verification.

Verified 2026-10-06: native POS returned all 63 exact prices/names; a repeated import
did not add duplicate records. One Margherita (69 MAD) and one Coca Cola (15 MAD)
produced a demo total of 84 MAD, tender 100 MAD and change 16 MAD, with zero
outstanding balance, balanced GL entries, no stock ledger posting and a correctly
labelled demo receipt. The test opening, sale and GL entries were rolled back.

## Approved live demo import

The user explicitly approved the live demo import on 2026-10-06. The same
master data is now saved at `erp.atlasuse.site`; ATLAS BITES remains separate.
Live native POS catalog verification returned all 63 exact names/prices and
required-choice metadata. No Street Pizza Sales Invoice, POS Invoice, POS Opening
Entry or GL Entry was created. The existing site timezone is Africa/Casablanca.
The demo POS profile links the published company address and remains assigned
only to Administrator. Its till must be opened explicitly before checkout use.

Public application routes:
- Company: `/desk/company/Street%20Pizza%20%28Demo%29`
- POS profile: `/desk/pos-profile/Street%20Pizza%20-%20Maarif%20-%20Demo%20POS`
- POS: `/desk/selling/point-of-sale`

Before real operations, replace the demo configuration with verified legal company
identity, approved tax treatment and receipts, actual cash/stock and staff setup.
