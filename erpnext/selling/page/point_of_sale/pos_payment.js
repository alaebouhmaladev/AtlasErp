/* eslint-disable no-unused-vars */
erpnext.PointOfSale.Payment = class {
	constructor({ events, wrapper, settings }) {
		this.wrapper = wrapper;
		this.events = events;
		this.set_gt_to_default_mop = settings.set_grand_total_to_default_mop;
		this.invoice_fields = settings.invoice_fields;
		this.allow_partial_payment = settings.allow_partial_payment;

		this.init_component();
	}

	init_component() {
		this.prepare_dom();
		this.initialize_numpad();
		this.bind_events();
		this.attach_shortcuts();
	}

	prepare_dom() {
		this.wrapper.append(
			`<section class="payment-container">
				<div class="payment-split-container">
					<div class="payment-container-left">
						<div class="section-label payment-section">${__("Payment Method")}</div>
						<div class="payment-modes"></div>
						<div class="atlas-checkout-tools">
							<button type="button" class="btn btn-default atlas-split">${__("Split payment")}</button>
							<button type="button" class="btn btn-default atlas-tip hidden">${__("Add tip")}</button>
							<button type="button" class="btn btn-default atlas-addons hidden">${__("Service add-ons")}</button>
						</div>
						<div class="atlas-checkout-note text-muted"></div>
					</div>
					<div class="payment-container-right">
						<div class="fields-numpad-container">
							<div class="fields-section">
								<div class="invoice-fields">
									<button class="btn btn-default btn-sm btn-shadow addl-fields hidden">${__(
										"Update Additional Information"
									)}</button>
								</div>
							</div>
							<div class="number-pad"></div>
						</div>
					</div>
				</div>
				<div class="totals-section">
					<div class="totals"></div>
				</div>
				<div class="submit-order-btn">${__("Complete Order")}</div>
			</section>`
		);
		this.$component = this.wrapper.find(".payment-container");
		this.$payment_modes = this.$component.find(".payment-modes");
		this.$totals_section = this.$component.find(".totals-section");
		this.$totals = this.$component.find(".totals");
		this.$numpad = this.$component.find(".number-pad");
		this.$invoice_fields_section = this.$component.find(".fields-section");
	}

	make_invoice_field_dialog() {
		const me = this;
		if (!me.invoice_fields.length) return;
		me.addl_dlg = new frappe.ui.Dialog({
			title: __("Additional Information"),
			fields: me.invoice_fields,
			size: "small",
			primary_action_label: __("Save"),
			primary_action(values) {
				me.set_values_to_frm(values);
				if (this.complete_order) {
					me.submit_with_external_confirmation();
				}
				this.hide();
			},
		});
		me.addl_dlg.$wrapper.on("hide.bs.modal", function () {
			me.addl_dlg.complete_order = false;
		});
		me.add_btn_field_click_listener();
		me.set_value_on_dialog_fields();
		me.make_addl_info_dialog_btn_visible();
	}

	set_values_to_frm(values) {
		const frm = this.events.get_frm();
		this.addl_dlg.fields.forEach((df) => {
			frm.set_value(df.fieldname, values[df.fieldname]);
		});
		frappe.show_alert({
			message: __("Additional Information updated successfully."),
			indicator: "green",
		});
	}

	add_btn_field_click_listener() {
		const frm = this.events.get_frm();
		this.addl_dlg.fields.forEach((df) => {
			if (df.fieldtype === "Button") {
				this.addl_dlg.fields_dict[df.fieldname].$input.on("click", function () {
					if (frm.script_manager.has_handlers(df.fieldname, frm.doc.doctype)) {
						frm.script_manager.trigger(df.fieldname, frm.doc.doctype, frm.doc.docname);
					}
				});
			}
		});
	}

	set_value_on_dialog_fields() {
		const doc = this.events.get_frm().doc;
		this.addl_dlg.fields.forEach((df) => {
			if (doc[df.fieldname] || df.default_value) {
				this.addl_dlg.set_value(df.fieldname, doc[df.fieldname] || df.default_value);
			}
		});
	}

	make_addl_info_dialog_btn_visible() {
		this.$invoice_fields_section.find(".addl-fields").removeClass("hidden");
		this.$invoice_fields_section.find(".addl-fields").on("click", () => {
			this.addl_dlg.show();
		});
	}

	initialize_numpad() {
		const me = this;
		this.number_pad = new erpnext.PointOfSale.NumberPad({
			wrapper: this.$numpad,
			events: {
				numpad_event: function ($btn) {
					me.on_numpad_clicked($btn);
				},
			},
			cols: 3,
			keys: [
				[1, 2, 3],
				[4, 5, 6],
				[7, 8, 9],
				["+/-", 0, "Delete"],
			],
		});

		this.numpad_value = "";
	}

	on_numpad_clicked($btn, from_numpad = true) {
		const button_value = from_numpad ? $btn.attr("data-button-value") : $btn;

		from_numpad && highlight_numpad_btn($btn);
		if (!this.selected_mode) {
			frappe.show_alert({
				message: __("Select a Payment Method."),
				indicator: "yellow",
			});
			return;
		}

		const number_format_details = get_number_format_info(frappe.sys_defaults.number_format);
		const precision = frappe.sys_defaults.currency_precision || number_format_details.precision;
		this.numpad_value = "0";
		if (this.selected_mode.get_value()) {
			this.numpad_value = (this.selected_mode.get_value() * 10 ** precision).toFixed(0).toString();
		}

		let valid_input = true;
		if (button_value === "delete" || button_value === "Backspace") {
			this.numpad_value = this.numpad_value.slice(0, -1);
		} else if (button_value === "+/-") {
			this.numpad_value = `${this.numpad_value * -1}`;
		} else if (button_value === "+") {
			this.numpad_value =
				Number(this.numpad_value) >= 0 ? this.numpad_value : `${this.numpad_value * -1}`;
		} else if (button_value === "-") {
			this.numpad_value =
				Number(this.numpad_value) <= 0 ? this.numpad_value : `${this.numpad_value * -1}`;
		} else if (!isNaN(button_value)) {
			this.numpad_value = this.numpad_value + button_value;
		} else {
			valid_input = false;
		}
		valid_input && frappe.utils.play_sound("numpad-touch");

		this.selected_mode.set_value(this.numpad_value / 10 ** precision);

		function highlight_numpad_btn($btn) {
			$btn.addClass("shadow-base-inner bg-selected");
			setTimeout(() => {
				$btn.removeClass("shadow-base-inner bg-selected");
			}, 100);
		}
	}

	bind_events() {
		const me = this;
		this.$component.on("click", ".atlas-split", () => this.show_split_payment());
		this.$component.on("click", ".atlas-tip", () => this.show_tip_dialog());
		this.$component.on("click", ".atlas-addons", () => this.show_service_addons());

		this.$payment_modes.on("click", ".mode-of-payment", function (e) {
			const mode_clicked = $(this);
			// if clicked element doesn't have .mode-of-payment class then return
			if (!$(e.target).is(mode_clicked)) return;

			const mode = mode_clicked.attr("data-mode");

			// hide all control fields and shortcuts
			$(`.mode-of-payment-control`).css("display", "none");
			me.$payment_modes.find(`.pay-amount`).css("display", "inline");
			me.$payment_modes.find(`.loyalty-amount-name`).css("display", "none");

			// remove highlight from all mode-of-payments
			$(".mode-of-payment").removeClass("border-primary");

			me.hide_zero_amount();

			if (me.selected_mode?._label === me[`${mode}_control`]?._label) {
				// clicked one is selected then unselect it
				mode_clicked.removeClass("border-primary");
				me.selected_mode = "";
			} else {
				// clicked one is not selected then select it
				mode_clicked.addClass("border-primary");

				me.selected_mode = me[`${mode}_control`];
				const mode_clicked_amount = mode_clicked.find(`.${mode}-amount`).get(0);
				if (!mode_clicked_amount.innerHTML) {
					mode_clicked_amount.innerHTML = format_currency(0, me.events.get_frm().doc.currency);
				}
				me.auto_set_remaining_amount();
			}
		});

		// change payment amount for selected mode on key press from keyboard
		$(document).on("keydown", function (e) {
			if ($(e.target).closest(".modal").length || !me.$component.is(":visible")) return;
			if (me.selected_mode) {
				me.on_numpad_clicked(e.key, false);
			}
		});

		// deselect payment method if mode of payment or numpad is not clicked
		$(document).on("click", function (e) {
			const mode_of_payment_click = $(e.target).closest(".mode-of-payment").length;
			const numpad_btn_click = $(e.target).closest(".numpad-btn").length;

			if (!mode_of_payment_click && !numpad_btn_click && me.selected_mode) {
				me.selected_mode = "";
				me.hide_zero_amount();
				$(".mode-of-payment").removeClass("border-primary");
			}
		});

		frappe.ui.form.on("POS Invoice", "contact_mobile", (frm) => {
			const contact = frm.doc.contact_mobile;
			const request_button = $(this.request_for_payment_field?.$input[0]);
			if (contact) {
				request_button.removeClass("btn-default").addClass("btn-primary");
			} else {
				request_button.removeClass("btn-primary").addClass("btn-default");
			}
		});

		frappe.ui.form.on("POS Invoice", "coupon_code", (frm) => {
			this.bind_coupon_code_event(frm);
		});

		frappe.ui.form.on("Sales Invoice", "coupon_code", (frm) => {
			this.bind_coupon_code_event(frm);
		});

		this.setup_listener_for_payments();

		this.$payment_modes.on("click", ".shortcut", function () {
			const value = $(this).attr("data-value");
			me.selected_mode.set_value(value);
		});

		this.$component.on("click", ".submit-order-btn", async () => {
			const doc = this.events.get_frm().doc;
			const paid_amount = doc.paid_amount;
			const items = doc.items;

			if (
				!items.length ||
				(paid_amount == 0 &&
					doc.additional_discount_percentage != 100 &&
					this.allow_partial_payment === 0)
			) {
				const message = items.length
					? __("You cannot submit the order without payment.")
					: __("You cannot submit an empty order.");
				frappe.show_alert({ message, indicator: "orange" });
				frappe.utils.play_sound("error");
				return;
			}

			if (!this.validate_reqd_invoice_fields()) {
				return;
			}

			await this.submit_with_external_confirmation();
		});

		frappe.ui.form.on("POS Invoice", "paid_amount", (frm) => {
			this.bind_paid_amount_event(frm);
		});

		frappe.ui.form.on("POS Invoice", "loyalty_amount", (frm) => {
			this.bind_loyalty_amount_event(frm);
		});

		frappe.ui.form.on("Sales Invoice", "paid_amount", (frm) => {
			this.bind_paid_amount_event(frm);
		});

		frappe.ui.form.on("Sales Invoice", "loyalty_amount", (frm) => {
			this.bind_loyalty_amount_event(frm);
		});

		frappe.ui.form.on("Sales Invoice Payment", "amount", (frm, cdt, cdn) => {
			// for setting correct amount after loyalty points are redeemed
			const default_mop = locals[cdt][cdn];
			const mode = this.sanitize_mode_of_payment(default_mop.mode_of_payment);
			if (this[`${mode}_control`] && this[`${mode}_control`].get_value() != default_mop.amount) {
				this[`${mode}_control`].set_value(default_mop.amount);
			}
		});
	}

	bind_coupon_code_event(frm) {
		if (frm.doc.coupon_code && !frm.applying_pos_coupon_code) {
			if (!frm.doc.ignore_pricing_rule) {
				frm.applying_pos_coupon_code = true;
				frappe.run_serially([
					() => (frm.doc.ignore_pricing_rule = 1),
					() => frm.trigger("ignore_pricing_rule"),
					() => (frm.doc.ignore_pricing_rule = 0),
					() => frm.trigger("apply_pricing_rule"),
					() => frm.save(),
					() => this.update_totals_section(frm.doc),
					() => (frm.applying_pos_coupon_code = false),
				]);
			} else if (frm.doc.ignore_pricing_rule) {
				frappe.show_alert({
					message: __("Ignore Pricing Rule is enabled. Cannot apply coupon code."),
					indicator: "orange",
				});
			}
		}
	}

	bind_paid_amount_event(frm) {
		this.update_totals_section(frm.doc);
		this.render_payment_mode_dom();
	}

	bind_loyalty_amount_event(frm) {
		const formatted_currency = format_currency(frm.doc.loyalty_amount, frm.doc.currency);
		this.$payment_modes.find(`.loyalty-amount-amount`).html(formatted_currency);
	}

	setup_listener_for_payments() {
		frappe.realtime.on("process_phone_payment", (data) => {
			const doc = this.events.get_frm().doc;
			const { response, amount, success, failure_message } = data;
			let message, title;

			if (success) {
				title = __("Payment Received");
				const grand_total = cint(frappe.sys_defaults.disable_rounded_total)
					? doc.grand_total
					: doc.rounded_total;
				if (amount >= grand_total) {
					frappe.dom.unfreeze();
					message = __("Payment of {0} received successfully.", [
						format_currency(amount, doc.currency, 0),
					]);
					this.submit_with_external_confirmation();
					cur_frm.reload_doc();
				} else {
					message = __(
						"Payment of {0} received successfully. Waiting for other requests to complete...",
						[format_currency(amount, doc.currency, 0)]
					);
				}
			} else if (failure_message) {
				message = failure_message;
				title = __("Payment Failed");
			}

			frappe.msgprint({ message: message, title: title });
		});
	}

	hide_zero_amount() {
		const payment_methods = this.$payment_modes.find(`.mode-of-payment`);
		for (let i = 0; i < payment_methods.length; i++) {
			const mode = payment_methods.get(i).getAttribute("data-mode");
			if (this[`${mode}_control`]?.value === 0) {
				this.$payment_modes.find(`.${mode}-amount`).get(0).innerHTML = "";
			}
		}
	}

	auto_set_remaining_amount() {
		const doc = this.events.get_frm().doc;
		const grand_total = this.invoice_total(doc);
		const remaining_amount = grand_total - doc.paid_amount;
		const current_value = this.selected_mode ? this.selected_mode.get_value() : undefined;
		if (!current_value && remaining_amount > 0 && this.selected_mode) {
			this.selected_mode.set_value(remaining_amount);
		}
	}

	attach_shortcuts() {
		const ctrl_label = frappe.utils.is_mac() ? "⌘" : "Ctrl";
		this.$component.find(".submit-order-btn").attr("title", `${ctrl_label}+Enter`);
		frappe.ui.keys.on("ctrl+enter", () => {
			const payment_is_visible = this.$component.is(":visible");
			const active_mode = this.$payment_modes.find(".border-primary");
			if (payment_is_visible && active_mode.length) {
				this.$component.find(".submit-order-btn").click();
			}
		});

		frappe.ui.keys.add_shortcut({
			shortcut: "tab",
			action: () => {
				const payment_is_visible = this.$component.is(":visible");
				let active_mode = this.$payment_modes.find(".border-primary");
				active_mode = active_mode.length ? active_mode.attr("data-mode") : undefined;

				if (!active_mode) return;

				const mode_of_payments = Array.from(this.$payment_modes.find(".mode-of-payment")).map((m) =>
					$(m).attr("data-mode")
				);
				const mode_index = mode_of_payments.indexOf(active_mode);
				const next_mode_index = (mode_index + 1) % mode_of_payments.length;
				const next_mode_to_be_clicked = this.$payment_modes.find(
					`.mode-of-payment[data-mode="${mode_of_payments[next_mode_index]}"]`
				);

				if (payment_is_visible && mode_index != next_mode_index) {
					next_mode_to_be_clicked.click();
				}
			},
			condition: () =>
				this.$component.is(":visible") && this.$payment_modes.find(".border-primary").length,
			description: __("Switch Between Payment Modes"),
			ignore_inputs: true,
			page: cur_page.page.page,
		});
	}

	toggle_numpad() {
		// pass
	}

	render_payment_section() {
		this.render_payment_mode_dom();
		this.make_invoice_field_dialog();
		this.update_totals_section();
		this.focus_on_default_mop();
		this.load_checkout_context();
	}

	after_render() {
		const frm = this.events.get_frm();
		frm.script_manager.trigger("after_payment_render", frm.doc.doctype, frm.doc.docname);
	}

	edit_cart() {
		this.events.toggle_other_sections(false);
		this.toggle_component(false);
	}

	checkout() {
		const frm = this.events.get_frm();
		frm.cscript.calculate_outstanding_amount();
		frm.refresh_field("outstanding_amount");
		frm.refresh_field("paid_amount");
		frm.refresh_field("base_paid_amount");
		this.events.toggle_other_sections(true);
		this.toggle_component(true);

		this.render_payment_section();
		this.after_render();
	}

	toggle_remarks_control() {
		if (this.$remarks.find(".frappe-control").length) {
			this.$remarks.html("+ Add Remark");
		} else {
			this.$remarks.html("");
			this[`remark_control`] = frappe.ui.form.make_control({
				df: {
					label: __("Remark"),
					fieldtype: "Data",
					onchange: function () {},
				},
				parent: this.$totals_section.find(`.remarks`),
				render_input: true,
			});
			this[`remark_control`].set_value("");
		}
	}

	render_payment_mode_dom() {
		const doc = this.events.get_frm().doc;
		const payments = doc.payments;
		const currency = doc.currency;

		if (!this.$payment_modes.is(":visible")) {
			return;
		}

		this.$payment_modes.html(
			`${payments
				.map((p, i) => {
					const mode = this.sanitize_mode_of_payment(p.mode_of_payment);
					const payment_type = p.type;
					const amount =
						p.mode_of_payment === this.selected_mode?._label || p.amount !== 0
							? format_currency(p.amount, currency)
							: "";

					return `
					<div class="payment-mode-wrapper">
						<div class="mode-of-payment" data-mode="${mode}" data-payment-type="${payment_type}">
							${frappe.utils.escape_html(p.mode_of_payment)}
							<div class="${mode}-amount pay-amount">${amount}</div>
							<div class="${mode} mode-of-payment-control"></div>
						</div>
					</div>
				`;
				})
				.join("")}`
		);

		payments.forEach((p) => {
			const mode = this.sanitize_mode_of_payment(p.mode_of_payment);
			const me = this;
			this[`${mode}_control`] = frappe.ui.form.make_control({
				df: {
					label: p.mode_of_payment,
					fieldtype: "Currency",
					options: "currency",
					placeholder: __("Enter {0} amount.", [__(p.mode_of_payment)]),
					onchange: function () {
						const current_value = frappe.model.get_value(p.doctype, p.name, "amount");
						if (current_value != this.value) {
							frappe.model
								.set_value(p.doctype, p.name, "amount", flt(this.value))
								.then(() => me.update_totals_section());

							const formatted_currency = format_currency(this.value, currency);
							me.$payment_modes.find(`.${mode}-amount`).html(formatted_currency);
						}
					},
				},
				doc: { currency },
				parent: this.$payment_modes.find(`.${mode}.mode-of-payment-control`),
				render_input: true,
			});
			this[`${mode}_control`].toggle_label(false);
			this[`${mode}_control`].set_value(p.amount);
		});
		this.highlight_selected_mode();

		this.render_loyalty_points_payment_mode();
	}

	focus_on_default_mop() {
		if (!this.set_gt_to_default_mop) return;
		const doc = this.events.get_frm().doc;
		const payments = doc.payments;
		payments.forEach((p) => {
			const mode = this.sanitize_mode_of_payment(p.mode_of_payment);
			if (p.default) {
				setTimeout(() => {
					this.$payment_modes.find(`.${mode}.mode-of-payment-control`).parent().click();
				}, 500);
			}
		});
	}

	render_loyalty_points_payment_mode() {
		const me = this;
		const doc = this.events.get_frm().doc;
		const { loyalty_program, loyalty_points, conversion_factor } = this.events.get_customer_details();

		this.$payment_modes.find(`.mode-of-payment[data-mode="loyalty-amount"]`).parent().remove();

		if (!loyalty_program) return;

		let description, read_only, max_redeemable_amount;
		if (!loyalty_points) {
			description = __("You don't have enough points to redeem.");
			read_only = true;
		} else {
			max_redeemable_amount = flt(
				flt(loyalty_points) * flt(conversion_factor),
				precision("loyalty_amount", doc)
			);
			description = __("You can redeem up to {0}.", [format_currency(max_redeemable_amount)]);
			read_only = false;
		}

		const margin = this.$payment_modes.children().length % 2 === 0 ? "pr-2" : "pl-2";
		const amount = doc.loyalty_amount > 0 ? format_currency(doc.loyalty_amount, doc.currency) : "";
		this.$payment_modes.append(
			`<div class="payment-mode-wrapper">
				<div class="mode-of-payment loyalty-card" data-mode="loyalty-amount" data-payment-type="loyalty-amount">
					Redeem Loyalty Points
					<div class="loyalty-amount-amount pay-amount">${amount}</div>
					<div class="loyalty-amount-name">${frappe.utils.escape_html(loyalty_program)}</div>
					<div class="loyalty-amount mode-of-payment-control"></div>
				</div>
			</div>`
		);

		this["loyalty-amount_control"] = frappe.ui.form.make_control({
			df: {
				label: __("Redeem Loyalty Points"),
				fieldtype: "Currency",
				placeholder: __("Enter amount to be redeemed."),
				options: "company:currency",
				read_only,
				onchange: async function () {
					if (!loyalty_points) return;

					if (this.value > max_redeemable_amount) {
						frappe.show_alert({
							message: __("You cannot redeem more than {0}.", [
								format_currency(max_redeemable_amount),
							]),
							indicator: "red",
						});
						frappe.utils.play_sound("submit");
						me["loyalty-amount_control"].set_value(0);
						return;
					}
					const redeem_loyalty_points = this.value > 0 ? 1 : 0;
					await frappe.model.set_value(
						doc.doctype,
						doc.name,
						"redeem_loyalty_points",
						redeem_loyalty_points
					);
					frappe.model.set_value(
						doc.doctype,
						doc.name,
						"loyalty_points",
						parseInt(this.value / conversion_factor)
					);
				},
				description,
			},
			parent: this.$payment_modes.find(`.loyalty-amount.mode-of-payment-control`),
			render_input: true,
		});
		this["loyalty-amount_control"].toggle_label(false);

		this.highlight_selected_mode();
		// this.render_add_payment_method_dom();
	}

	highlight_selected_mode() {
		if (this.selected_mode) {
			const mode = this.sanitize_mode_of_payment(this.selected_mode.df.label);
			this.$payment_modes.find(`.mode-of-payment[data-mode="${mode}"]`).addClass("border-primary");
		}
	}

	render_add_payment_method_dom() {
		const docstatus = this.events.get_frm().doc.docstatus;
		if (docstatus === 0)
			this.$payment_modes.append(
				`<div class="w-full pr-2">
					<div class="add-mode-of-payment w-half text-grey mb-4 no-select pointer">+ Add Payment Method</div>
				</div>`
			);
	}

	update_totals_section(doc) {
		if (!doc) doc = this.events.get_frm().doc;
		const paid_amount = doc.paid_amount;
		const grand_total = this.invoice_total(doc);
		const remaining = grand_total - doc.paid_amount;
		const change = doc.change_amount || remaining <= 0 ? -1 * remaining : undefined;
		const currency = doc.currency;
		const label = doc.paid_amount > grand_total ? __("Change Amount") : __("Remaining Amount");

		if (!this.$totals.is(":visible")) {
			return;
		}

		this.$totals.html(
			`<div class="col">
				<div class="total-label">${__("Grand Total")}</div>
				<div class="value">${format_currency(grand_total, currency)}</div>
			</div>
			<div class="seperator-y"></div>
			<div class="col">
				<div class="total-label">${__("Paid Amount")}</div>
				<div class="value">${format_currency(paid_amount, currency)}</div>
			</div>
			<div class="seperator-y"></div>
			<div class="col">
				<div class="total-label">${label}</div>
				<div class="value ${doc.paid_amount < grand_total ? "text-danger" : "text-success"}">${format_currency(
				change || remaining,
				currency
			)}</div>
			</div>`
		);
	}

	toggle_component(show) {
		show ? this.$component.css("display", "flex") : this.$component.css("display", "none");
	}

	sanitize_mode_of_payment(mode_of_payment) {
		return mode_of_payment
			.replace(/ +/g, "_")
			.replace(/[^\p{L}\p{N}_-]/gu, "")
			.replace(/^[^_a-zA-Z\p{L}]+/u, "")
			.toLowerCase();
	}

	validate_reqd_invoice_fields() {
		if (this.invoice_fields.length === 0) return true;
		const doc = this.events.get_frm().doc;
		for (const df of this.addl_dlg.fields) {
			if (df.reqd && !doc[df.fieldname]) {
				this.addl_dlg.primary_action_label = "Submit";
				this.addl_dlg.complete_order = true;
				this.addl_dlg.show();
				this.addl_dlg.fields_dict[df.fieldname].$input.focus();
				return false;
			}
		}
		return true;
	}

	invoice_total(doc = this.events.get_frm().doc) {
		return cint(doc.disable_rounded_total ?? frappe.sys_defaults.disable_rounded_total)
			? flt(doc.grand_total) : flt(doc.rounded_total || doc.grand_total);
	}

	payment_due() {
		const doc = this.events.get_frm().doc;
		// Native loyalty changes the default tender. Keep its settled contribution.
		return this.invoice_total(doc) - flt(doc.loyalty_amount) / (flt(doc.conversion_rate) || 1) - flt(doc.write_off_amount) - flt(doc.total_advance);
	}

	async load_checkout_context() {
		const doc = this.events.get_frm().doc;
		this.$component.find(".atlas-tip,.atlas-addons").addClass("hidden");
		this.checkout_context = null;
		try {
			const { message } = await frappe.call({ method: "atlas_erp.pos_api.checkout.context", type: "GET",
				args: { pos_profile: doc.pos_profile } });
			if (this.events.get_frm().doc !== doc) return;
			this.checkout_context = message;
			this.$component.find(".atlas-tip").toggleClass("hidden", !message.tips_enabled && !doc.atlas_tip_amount);
			this.$component.find(".atlas-tip").text(doc.is_return ? __("Review tip refund") : __("Add tip"));
			this.$component.find(".atlas-addons").toggleClass("hidden", !message.addons_enabled || !!doc.is_return);
			this.$component.find(".atlas-split").prop("disabled", !!doc.is_return);
			this.$component.find(".atlas-checkout-note").text(message.confirm_external ?
				__("Approve the payment on your terminal first. The POS records its reference.") : "");
		} catch (error) {
			this.$component.find(".atlas-checkout-note").text(__("Checkout settings could not be loaded. Reopen checkout to try again."));
		}
	}

	show_split_payment() {
		const doc = this.events.get_frm().doc;
		if (doc.is_return) return;
		const p = precision("paid_amount", doc) ?? 2;
		const due = this.payment_due();
		const modes = doc.payments.map(row => ({ mode_of_payment: row.mode_of_payment, type: row.type }));
		const default_mode = modes.find(mode => mode.type === "Cash")?.mode_of_payment || modes[0]?.mode_of_payment;
		const confirm = !!this.checkout_context?.confirm_external;
		this.selected_mode = "";
		let dlg;
		dlg = new frappe.ui.Dialog({ title: __("Split payment"), size: "large", fields: [
			{ fieldname: "help", fieldtype: "HTML", options: `<p>${__("Amount due")}: <strong>${format_currency(due, doc.currency)}</strong></p><p>${__("One invoice, multiple payment portions. Each card portion must be approved on the terminal before you confirm it here.")}</p>` },
			{ fieldname: "shares", fieldtype: "Int", label: __("Equal shares"), default: 2 },
			{ fieldname: "divide", fieldtype: "Button", label: __("Divide equally"), click: () => {
				try {
					dlg.fields_dict.portions.df.data = erpnext.PointOfSale.CheckoutMath.shares(due, Number(dlg.get_value("shares")), p)
						.map(amount => ({ mode_of_payment: default_mode, amount, currency: doc.currency }));
					dlg.fields_dict.portions.grid.refresh();
				} catch (error) { frappe.msgprint(__(error.message)); }
			} },
			{ fieldname: "portions", fieldtype: "Table", label: __("Payment portions"), in_place_edit: true,
				data: doc.payments.filter(row => row.amount).map(row => ({ mode_of_payment: row.mode_of_payment,
					amount: row.amount, currency: doc.currency, reference_no: row.reference_no,
					confirmed: row.atlas_external_confirmed && row.atlas_confirmed_amount === row.amount })),
				fields: [
					{ fieldname: "currency", fieldtype: "Data", hidden: 1, default: doc.currency },
					{ fieldname: "mode_of_payment", fieldtype: "Select", label: __("Payment method"), options: modes.map(mode => mode.mode_of_payment), in_list_view: 1, reqd: 1 },
					{ fieldname: "amount", fieldtype: "Currency", label: __("Amount"), options: "currency", in_list_view: 1, reqd: 1 },
					{ fieldname: "reference_no", fieldtype: "Data", label: __("Transaction reference"), in_list_view: 1 },
					{ fieldname: "confirmed", fieldtype: "Check", label: __("External payment approved"), in_list_view: 1 },
				] },
		], primary_action_label: __("Apply payments"), primary_action: async values => {
			if (this.events.get_frm().doc !== doc || this.payment_due() !== due) {
				frappe.msgprint(__("The order changed. Reopen Split payment.")); return;
			}
			try {
				const allocation = erpnext.PointOfSale.CheckoutMath.allocate(due, values.portions || [], modes, p, confirm);
				for (const row of doc.payments) {
					const value = allocation.find(value => value.mode_of_payment === row.mode_of_payment);
					await frappe.model.set_value(row.doctype, row.name, value);
				}
				this.events.get_frm().cscript.calculate_outstanding_amount();
				this.render_payment_mode_dom(); this.update_totals_section();
				dlg.hide();
			} catch (error) { frappe.msgprint(__(error.message)); }
		} });
		dlg.show();
	}

	show_tip_dialog() {
		const doc = this.events.get_frm().doc;
		const settings = this.checkout_context;
		if (!settings || (!settings.tips_enabled && !doc.atlas_tip_amount)) return;
		this.selected_mode = "";
		let dlg;
		dlg = new frappe.ui.Dialog({ title: doc.is_return ? __("Tip refund") : __("Optional staff tip"), fields: [
			{ fieldname: "percentage", fieldtype: "Select", label: __("Tip choice"),
				options: [__("Custom amount"), __("No tip"), ...settings.tip_presets.map(p => `${p}%`)],
				default: __("Custom amount"), onchange: () => {
					const choice = dlg?.get_value("percentage");
					if (!choice || choice === __("Custom amount")) return;
					dlg.set_value("amount", choice === __("No tip") ? 0 :
						flt(Math.abs(doc.net_total) * parseFloat(choice) / 100, precision("atlas_tip_amount", doc)));
				} },
			{ fieldname: "amount", fieldtype: "Float", label: (doc.is_return ? __("Tip to refund") : __("Tip amount")) + ` (${doc.currency})`,
				precision: precision("atlas_tip_amount", doc) ?? 2, default: Math.abs(doc.atlas_tip_amount || 0), reqd: 0,
				description: __("Tips are held in the company's staff-tip account. They are not paid to staff automatically.") },
		], primary_action_label: __("Apply"), primary_action: async ({ amount }) => {
			if (this.events.get_frm().doc !== doc) return;
			if (!Number.isFinite(Number(amount || 0)) || Number(amount) < 0) {
				frappe.msgprint(__("Enter a non-negative tip amount.")); return;
			}
			if (doc.apply_discount_on === "Grand Total" && (doc.discount_amount || doc.additional_discount_percentage)) {
				frappe.msgprint(__("Apply the discount to Net Total before adding a tip.")); return;
			}
			const frm = this.events.get_frm();
			const original_tip = doc.taxes.find(row => row.atlas_is_tip);
			doc.taxes = doc.taxes.filter(row => !row.atlas_is_tip);
			doc.taxes.forEach((row, i) => row.idx = i + 1);
			doc.atlas_tip_amount = flt((doc.is_return ? -1 : 1) * Number(amount || 0), precision("atlas_tip_amount", doc));
			if (doc.atlas_tip_amount) frm.add_child("taxes", { charge_type: "Actual", atlas_is_tip: 1,
				account_head: doc.is_return ? original_tip?.account_head : settings.tip_account,
				description: __("Staff tip"), tax_amount: doc.atlas_tip_amount, cost_center: doc.cost_center });
			frm.dirty();
			await frm.cscript.calculate_taxes_and_totals();
			this.render_payment_mode_dom(); this.update_totals_section();
			dlg.hide();
		} });
		dlg.show();
	}

	async show_service_addons() {
		const doc = this.events.get_frm().doc;
		const { message: items } = await frappe.call({ method: "atlas_erp.pos_api.checkout.service_addons", type: "GET",
			args: { pos_profile: doc.pos_profile } });
		if (this.events.get_frm().doc !== doc) return;
		if (!items.length) { frappe.msgprint(__("Add enabled non-stock sales items and prices to the register's service add-on group.")); return; }
		let dlg;
		dlg = new frappe.ui.Dialog({ title: __("Service add-ons"), fields: [
			{ fieldname: "item", fieldtype: "Select", label: __("Service"), reqd: 1,
				default: items[0].item_code,
				options: items.map(item => ({ value: item.item_code, label: `${frappe.utils.escape_html(item.item_name)} · ${format_currency(item.rate, item.currency)}` })) },
		], primary_action_label: __("Add to order"), primary_action: async ({ item }) => {
			if (this.events.get_frm().doc !== doc) return;
			const selected = items.find(row => row.item_code === item);
			if (!selected) return;
			dlg.hide(); this.edit_cart();
			await this.events.add_service_item(selected);
		} });
		dlg.show();
	}

	async submit_with_external_confirmation() {
		const doc = this.events.get_frm().doc;
		if (this._submitting || this._confirmation_dialog) return;
		const external = doc.payments.filter(row => row.type === "Bank" && row.amount &&
			(!row.atlas_external_confirmed || !row.reference_no || row.atlas_confirmed_amount !== row.amount));
		if (!this.checkout_context) {
			frappe.msgprint(__("Reopen checkout to load the register's payment settings.")); return;
		}
		if (this.checkout_context.confirm_external && external.length) {
			this.selected_mode = "";
			const amounts = external.map(row => row.amount);
			const total = this.invoice_total(doc);
			this._confirmation_dialog = new frappe.ui.Dialog({ title: __("Confirm external payment"), fields: external.flatMap((row, i) => [
				{ fieldname: `amount_${i}`, fieldtype: "HTML", options: `<p>${frappe.utils.escape_html(row.mode_of_payment)}: <strong>${format_currency(row.amount, doc.currency)}</strong></p>` },
				{ fieldname: `ref_${i}`, fieldtype: "Data", label: __("Transaction reference (no card numbers)"), reqd: 1 },
				{ fieldname: `ok_${i}`, fieldtype: "Check", label: __("The terminal or bank confirmed this payment/refund"), reqd: 1 },
			]), primary_action_label: __("Confirm and complete"), primary_action: async values => {
				if (this.events.get_frm().doc !== doc || this.invoice_total(doc) !== total ||
					external.some((row, i) => row.amount !== amounts[i])) {
					frappe.msgprint(__("The payment amount changed. Reopen checkout.")); return;
				}
				for (const [i, row] of external.entries()) {
					if (!values[`ok_${i}`] || !values[`ref_${i}`]?.trim()) return;
					await frappe.model.set_value(row.doctype, row.name, { reference_no: values[`ref_${i}`].trim(), atlas_external_confirmed: 1, atlas_confirmed_amount: row.amount });
				}
				this._confirmation_dialog.hide();
				this._confirmation_dialog = null;
				await this.submit_with_external_confirmation();
			} });
			this._confirmation_dialog.$wrapper.on("hidden.bs.modal", () => this._confirmation_dialog = null);
			this._confirmation_dialog.show(); return;
		}
		this._submitting = true;
		try { await this.events.submit_invoice(); } finally { this._submitting = false; }
	}
};
