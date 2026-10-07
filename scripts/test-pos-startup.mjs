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

// The handoff must use the server's company, not a stale global or URL value.
let dialog;
let profileRead;
let handoffRequest;
context.URLSearchParams = URLSearchParams;
context.window = { location: { search: "?atlas_profile=Allowed%20register&company=Forged" } };
context.__ = value => value;
context.frappe.defaults = { get_default: () => "Stale company" };
context.frappe.db = { get_doc: async (doctype, name) => {
	profileRead = name;
	return { payments: [{ mode_of_payment: "Cash" }] };
} };
context.frappe.call = async request => {
	handoffRequest = request;
	return { message: { company: "Server company", pos_profile: "Allowed register" } };
};
context.frappe.ui.Dialog = class {
	constructor(options) {
		dialog = this;
		this.options = options;
		this.fields_dict = {
			pos_profile: { get_value: () => options.fields.find(f => f.fieldname === "pos_profile").default },
			company: { get_value: () => options.fields.find(f => f.fieldname === "company").default },
			balance_details: { df: {}, grid: { refresh() {} } },
		};
	}
	show() { this.shown = true; }
};
await controller.create_opening_voucher();
await Promise.resolve();
assert.equal(handoffRequest.type, "GET");
assert.equal(handoffRequest.args.pos_profile, "Allowed register");
assert.equal(dialog.options.fields.find(f => f.fieldname === "company").default, "Server company");
assert.equal(profileRead, "Allowed register");
assert.equal(dialog.fields_dict.balance_details.df.data[0].mode_of_payment, "Cash");
dialog = undefined;
context.frappe.call = async () => { throw new Error("Not permitted"); };
await controller.create_opening_voucher();
assert.equal(dialog, undefined, "Denied handoff must not open a dialog");
context.window.location.search = "";
await controller.create_opening_voucher();
assert.equal(dialog.options.fields.find(f => f.fieldname === "company").default, "Stale company");
console.log("PASS: ATLAS register handoff uses verified company/profile, rejects denied requests and preserves ordinary native entry");

context.window.location.search = "?atlas_profile=Allowed%20register";
context.frappe.call = async () => ({ message: { company: "Server company", pos_profile: "Allowed register" } });
let resumedSession;
let changedSessionMessage;
controller.prepare_app_defaults = data => { resumedSession = data; };
context.frappe.msgprint = message => { changedSessionMessage = message; };
controller.fetch_opening_entry = async () => ({ message: [{ company: "Server company", pos_profile: "Allowed register" }] });
await controller.check_opening_entry();
await Promise.resolve();
assert.equal(resumedSession.pos_profile, "Allowed register");
resumedSession = undefined;
controller.fetch_opening_entry = async () => ({ message: [{ company: "Other company", pos_profile: "Other register" }] });
await controller.check_opening_entry();
await Promise.resolve();
assert.equal(resumedSession, undefined);
assert.match(changedSessionMessage, /session changed/);
console.log("PASS: resume validates the selected register and rejects a changed session");
