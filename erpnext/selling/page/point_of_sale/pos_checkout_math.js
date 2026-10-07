/* Money allocation in currency minor units; native ERP still quotes and posts. */
erpnext.PointOfSale.CheckoutMath = {
	units(value, precision = 2) {
		const number = Number(value);
		if (!Number.isFinite(number) || !Number.isInteger(precision) || precision < 0 || precision > 6) {
			throw new Error("Enter a valid payment amount.");
		}
		const units = Math.round((number + Math.sign(number) * Number.EPSILON) * 10 ** precision);
		if (!Number.isSafeInteger(units)) throw new Error("Payment amount is too large.");
		return units;
	},
	shares(total, count, precision = 2) {
		const units = this.units(total, precision);
		if (units < 0 || !Number.isInteger(count) || count < 2 || count > 20) {
			throw new Error("Choose between 2 and 20 shares for a sale.");
		}
		return Array.from({ length: count }, (_, i) =>
			(Math.floor(units / count) + (i < units % count ? 1 : 0)) / 10 ** precision
		);
	},
	allocate(total, rows, modes, precision = 2, require_confirmation = false) {
		const due = this.units(total, precision);
		if (due < 0) throw new Error("Use the refund workflow for returns.");
		const amounts = new Map(modes.map(mode => [mode.mode_of_payment, 0]));
		const references = new Map();
		let paid = 0, cash = 0;
		for (const row of rows) {
			const mode = modes.find(mode => mode.mode_of_payment === row.mode_of_payment);
			const amount = this.units(row.amount || 0, precision);
			if (!mode || amount < 0) throw new Error("Choose a register payment method and a non-negative amount.");
			if (!amount) continue;
			if (mode.type === "Bank" && require_confirmation &&
				(!row.confirmed || !String(row.reference_no || "").trim())) {
				throw new Error("Confirm each external payment and enter its transaction reference.");
			}
			paid += amount;
			if (mode.type === "Cash") cash += amount;
			amounts.set(mode.mode_of_payment, amounts.get(mode.mode_of_payment) + amount);
			const refs = references.get(mode.mode_of_payment) || [];
			if (row.reference_no) refs.push(String(row.reference_no).trim());
			references.set(mode.mode_of_payment, refs);
		}
		if (paid < due) throw new Error("The split does not cover the amount due.");
		if (paid - due > cash) throw new Error("Overpayment must be cash that can be returned as change.");
		return modes.map(mode => {
			const reference = [...new Set(references.get(mode.mode_of_payment) || [])].join("; ");
			if (reference.length > 140) throw new Error("Transaction references are too long. Use fewer references per payment method.");
			const confirmed = mode.type === "Bank" && amounts.get(mode.mode_of_payment) > 0 && require_confirmation ? 1 : 0;
			return { mode_of_payment: mode.mode_of_payment, amount: amounts.get(mode.mode_of_payment) / 10 ** precision,
				reference_no: reference, atlas_external_confirmed: confirmed,
				atlas_confirmed_amount: confirmed ? amounts.get(mode.mode_of_payment) / 10 ** precision : 0 };
		});
	},
};
