// Run with node scripts/test-pos-startup.mjs. No browser or ERP database needed.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

let draft;
let refreshed;
const context = {
	erpnext: { PointOfSale: {} },
	$: () => ({}),
	frappe: {
		ui: { form: { Form: class { refresh(name) { refreshed = { ...draft, name }; } } } },
		model: {
			make_new_doc_and_get_name: () => {
				draft = { company: "Other company", pos_profile: "Other profile" };
				return "new-invoice";
			},
		},
		get_doc: () => draft,
	},
};
vm.runInNewContext(
	readFileSync(new URL("../erpnext/selling/page/point_of_sale/pos_controller.js", import.meta.url), "utf8"),
	context
);
const controller = Object.create(context.erpnext.PointOfSale.Controller.prototype);
controller.settings = { frm_doctype: "Sales Invoice" };
controller.company = "Session company";
controller.pos_profile = "Session profile";
const form = controller.get_new_frm();
assert.equal(refreshed.company, "Session company");
assert.equal(refreshed.pos_profile, "Session profile");
controller.company = "Next session company";
controller.pos_profile = "Next session profile";
assert.equal(controller.get_new_frm(form), form);
assert.equal(refreshed.company, "Next session company");
assert.equal(refreshed.pos_profile, "Next session profile");
console.log("PASS: new and reused POS forms use the open session before form refresh");

