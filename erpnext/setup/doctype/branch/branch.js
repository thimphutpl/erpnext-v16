// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Branch", {
	onload: function (frm) {
		frm.set_query("expense_bank_account", function() {
			return {
				filters: {
					'is_group': 0,
					'account_type': 'Bank'
				}
			}
		});
	},

	refresh: function (frm) {
		
	},
});