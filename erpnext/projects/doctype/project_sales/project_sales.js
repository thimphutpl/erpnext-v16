// // Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// // For license information, please see license.txt

// frappe.ui.form.on("Project Sales", {
// 	refresh(frm) {
//         if (frm.doc.jv && frappe.model.can_read("Journal Entry")) {
// 			cur_frm.add_custom_button(__('Bank Entries'), function() {
// 				frappe.route_options = {
// 					"Journal Entry Account.reference_type": me.frm.doc.doctype,
// 					"Journal Entry Account.reference_name": me.frm.doc.name,
// 				};
// 				frappe.set_route("List", "Journal Entry");
// 			}, __("View"));
// 		}
// 	},

//     onload: function(frm) {
// 		if(!frm.doc.posting_date) {
// 			cur_frm.set_value("posting_date", get_today())
// 		}
// 	}
// });

// frappe.ui.form.on('Project Sales Item', {
// 	rate: function(frm, cdt, cdn) {
// 		calculate_amount(frm, cdt, cdn)
// 	},
// 	qty: function(frm, cdt, cdn) {
// 		calculate_amount(frm, cdt, cdn)
// 	}
// });

// function calculate_amount(frm, cdt, cdn) {
// 	var item = locals[cdt][cdn]
// 	if (item.rate && item.qty) {
// 		frappe.model.set_value(cdt, cdn, "amount", item.rate * item.qty)
// 	}
// 	cur_frm.refresh_fields("amount")
// }

// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project Sales", {
	refresh(frm) {
		if (frm.doc.jv && frappe.model.can_read("Journal Entry")) {
			cur_frm.add_custom_button(__('Bank Entries'), function () {
				frappe.route_options = {
					"Journal Entry Account.reference_type": me.frm.doc.doctype,
					"Journal Entry Account.reference_name": me.frm.doc.name,
				};
				frappe.set_route("List", "Journal Entry");
			}, __("View"));
		}
	},

	onload: function (frm) {
		if (!frm.doc.posting_date) {
			cur_frm.set_value("posting_date", get_today())
		}
	}
});

frappe.ui.form.on('Project Sales Item', {

	item_code(frm, cdt, cdn) {

		let row = locals[cdt][cdn];

		if (!row.item_code) return;


		frappe.call({
			method: "erpnext.projects.doctype.project_sales.project_sales.get_item_details",
			args: {
				item_code: row.item_code
			},
			callback: function (r) {
				if (r.message) {
					frappe.model.set_value(cdt, cdn, "expense_account", r.message.expense_account);

					cur_frm.refresh_fields("items")

				}

			}
		});
	},
	rate: function (frm, cdt, cdn) {
		calculate_amount(frm, cdt, cdn)
	},
	qty: function (frm, cdt, cdn) {
		calculate_amount(frm, cdt, cdn)
	}
});

function calculate_amount(frm, cdt, cdn) {
	var item = locals[cdt][cdn]
	if (item.rate && item.qty) {
		frappe.model.set_value(cdt, cdn, "amount", item.rate * item.qty)
	}
	cur_frm.refresh_fields("amount")
}