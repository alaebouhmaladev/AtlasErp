// Run with node scripts/test-pos-checkout.mjs.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
const context = { erpnext: { PointOfSale: {} } };
vm.runInNewContext(readFileSync(new URL("../erpnext/selling/page/point_of_sale/pos_checkout_math.js", import.meta.url), "utf8"), context);
const math = context.erpnext.PointOfSale.CheckoutMath;
const modes = [{ mode_of_payment: "Cash", type: "Cash" }, { mode_of_payment: "NAPS card", type: "Bank" }];
const plain = value => JSON.parse(JSON.stringify(value));
assert.deepEqual(plain(math.shares(301, 3)), [100.34, 100.33, 100.33]);
assert.deepEqual(plain(math.shares(1, 3, 0)), [1, 0, 0]);
assert.deepEqual(plain(math.shares(.05, 3)), [.02, .02, .01]);
assert.equal(math.shares(999.99, 17).reduce((sum, n) => sum + math.units(n), 0), 99999);
const allocated = math.allocate(301, [
    { mode_of_payment: "Cash", amount: 100 },
    { mode_of_payment: "NAPS card", amount: 201, reference_no: "NAPS-test-ref", confirmed: 1 },
], modes, 2, true);
assert.equal(allocated[1].amount, 201);
assert.equal(allocated[1].atlas_confirmed_amount, 201);
assert.equal(allocated[1].atlas_external_confirmed, 1);
assert.equal(allocated[1].reference_no, "NAPS-test-ref");
assert.equal(math.allocate(301, [{ mode_of_payment: "Cash", amount: 350 }], modes)[0].amount, 350);
assert.throws(() => math.allocate(301, [{ mode_of_payment: "NAPS card", amount: 302 }], modes), /Overpayment/);
assert.throws(() => math.allocate(301, [{ mode_of_payment: "Cash", amount: 1 }, { mode_of_payment: "NAPS card", amount: 302 }], modes), /Overpayment/);
assert.throws(() => math.allocate(301, [{ mode_of_payment: "Cash", amount: 300 }], modes), /does not cover/);
assert.throws(() => math.allocate(301, [{ mode_of_payment: "NAPS card", amount: 301 }], modes, 2, true), /Confirm/);
assert.throws(() => math.allocate(301, [{ mode_of_payment: "Cash", amount: -301 }], modes), /non-negative/);
assert.throws(() => math.allocate(301, [{ mode_of_payment: "Unknown", amount: 301 }], modes), /Choose/);
assert.throws(() => math.allocate(-301, [], modes), /refund/);
for (const invalid of [NaN, Infinity, "NaN", 1e20]) assert.throws(() => math.units(invalid));
assert.throws(() => math.shares(301, 0));
assert.throws(() => math.shares(301, 2.1));
console.log("PASS: equal/custom splits, currency rounding, cash change, terminal references, invalid and under/overpaid allocations");

// The payment action must not post twice while a save/submit is pending.
context.__ = value => value;
context.cint = value => Number(value || 0);
context.flt = value => Number(value || 0);
let submissions = 0, finish;
context.frappe = { sys_defaults: {}, msgprint: () => {} };
vm.runInNewContext(readFileSync(new URL("../erpnext/selling/page/point_of_sale/pos_payment.js", import.meta.url), "utf8"), context);
const payment = Object.create(context.erpnext.PointOfSale.Payment.prototype);
// A table editor may still hold changes when the operator presses Apply.
const stale = [{ name: "cash", mode_of_payment: "Cash", amount: 100 },
    { name: "card", mode_of_payment: "NAPS card", amount: 201, reference_no: "", confirmed: 0 }];
const grid = { get_data: () => stale, grid_rows: [{ doc: { name: "card" }, on_grid_fields_dict: {
    reference_no: { get_value: () => "approved-ref" }, confirmed: { get_value: () => 1 },
} }] };
const current = payment.split_payment_rows(grid);
assert.equal(math.allocate(301, current, modes, 2, true)[1].reference_no, "approved-ref");
assert.equal(stale[1].confirmed, 0, "Reading active editors must not mutate the original table data");
console.log("PASS: split payment includes active editor reference/confirmation before blur");
payment.checkout_context = { confirm_external: true };
payment.events = { get_frm: () => ({ doc: { payments: [] } }), submit_invoice: () => {
    submissions++; return new Promise(resolve => finish = resolve);
} };
const first = payment.submit_with_external_confirmation();
await payment.submit_with_external_confirmation();
assert.equal(submissions, 1);
finish(); await first;
assert.equal(payment._submitting, false);
payment.events.submit_invoice = async () => { throw new Error("save failed"); };
await assert.rejects(payment.submit_with_external_confirmation(), /save failed/);
assert.equal(payment._submitting, false, "Failed submission must allow a retry");
console.log("PASS: checkout submission blocks double taps, releases its guard on failure; server replay idempotency remains separate");
