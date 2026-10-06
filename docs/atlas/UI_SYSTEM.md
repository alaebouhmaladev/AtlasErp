# ATLASERP UI system — 0.3

The `/atlas` workspace is the visual reference: forest green headings, lime primary highlights, pale green page backgrounds, white cards, subtle borders and rounded controls.

## Surfaces

- **Desk:** `theme-v3.1.css` supplies shared legacy and Espresso semantic tokens. `desk-v3.1.css` styles native navigation, lists, forms, tabs, dialogs, reports and POS. `brand-v3.1.js` adds one workspace shortcut without replacing role-filtered menus.
- **Business customer portal:** `/atlas-portal` requires login. Customer and Supplier cards link to native ERPNext portal routes. Their existing contact/document access checks remain authoritative; the home page does not query or publish financial data. Accounts without these roles see their profile and an access explanation.
- **Native website pages:** login, account, portal document lists and details use shared tokens and `web-v3.1.css`. Native navigation, pagination, document actions and authentication remain in place.
- **Restaurant customer layout:** `/atlas-menu` is a public, read-only Street Pizza demonstration, with 63 verified public dishes, category navigation, ingredient search and meal-deal choices. It uses an explicitly packaged public snapshot, not an unfiltered ERP Item/Item Price query. Its prices are dated; changing POS prices does not silently publish them.

## Boundaries

This release changes the interface and adds entry pages. It does not implement online ordering, payment collection, table orders, kitchen tickets or meal-deal validation at checkout. The restaurant page clearly identifies itself as a demo preview. Production restaurant publishing will need explicit per-brand menu configuration and visibility controls.

Native operational controls, document names, audit trails, accounting calculations and permission hooks are preserved. Status colors remain semantic (red for errors, amber warnings). Dark Desk mode uses corresponding green surfaces and contrasting lime primary controls. Report tables retain native sizing and horizontal scrolling. Print templates retain their existing fiscal/demo behavior.

## Validation

Run `scripts/check-theme-http.py <private-env-path>` on the server. It reads the Administrator password privately and performs HTTP reads/login only: public menu count/prices/options, guest portal protection, authenticated portal, Desk asset registration and static asset availability. Also inspect actual Item lists/forms, reports, POS session dialog, portal and restaurant menu on desktop/mobile. No sale or POS opening is submitted during UI validation.

Asset filenames are versioned so existing year-long nginx cache entries for the old styles do not mask this release. New edits to these files require another filename version or cache invalidation before rollout.
