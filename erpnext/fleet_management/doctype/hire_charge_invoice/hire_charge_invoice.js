// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Hire Charge Invoice', {
	refresh: function(frm) {
		if(frm.doc.docstatus===1){
			frm.add_custom_button(__('Accounting Ledger'), function(){
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date,
					company: frm.doc.company,
					group_by_voucher: false
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));
		}

		frm.set_df_property("discount_amount", "read_only", frm.doc.owned_by == "CDCL")
		if (frm.doc.invoice_jv && frappe.model.can_read("Journal Entry")) {
			cur_frm.add_custom_button(__('Journal Entry'), function() {
				frappe.route_options = {
					"Journal Entry Account.reference_type": frm.doc.doctype,
					"Journal Entry Account.reference_name": frm.doc.name,
				};
				frappe.set_route("List", "Journal Entry");
			}, __("View"));
		}
		if (frm.doc.owned_by != "CDCL" && frm.doc.outstanding_amount > 0 && frappe.model.can_write("Journal Entry")) {
			/*//cur_frm.toggle_display("receive_payment", 1)
			cur_frm.add_custom_button(__('Payment'), function() {
				cur_frm.cscript.receive_payment()
			}, __("Receive")); */
			frm.add_custom_button("Receive Payment", function() {
				frappe.model.open_mapped_doc({
					method: "erpnext.fleet_management.doctype.hire_charge_invoice.hire_charge_invoice.make_payment_entry",
					frm: cur_frm
				})
			}, __("Receive"));
		}
		else {
			cur_frm.toggle_display("receive_payment", 0)
		}
	},
	onload: function(frm) {
		if (!frm.doc.posting_date) {
			frm.set_value("posting_date", get_today());
		}
	},
	"get_vehicle_logbooks": function(frm) {
		get_vehicle_logs(frm.doc.ehf_name)
	},
	"advance_amount": function(frm) {
		calculate_balance(frm)
	},
	"total_invoice_amount": function(frm) {
		calculate_balance(frm)
	},
	"discount_amount": function(frm) {
		calculate_balance(frm)
	},
	"get_advances": function(frm) {
		get_advances(frm.doc.ehf_name)
	},
	"receive_payment": function(frm) {
		if(!frm.doc.payment_jv) {
			return frappe.call({
				method: "erpnext.fleet_management.doctype.hire_charge_invoice.hire_charge_invoice.make_bank_entry",
				args: {
					"frm": cur_frm.doc.name,
				},
				callback: function(r) {
					cur_frm.refresh()
				}
			});
		}
		cur_frm.refresh_field("payment_jv")
		cur_frm.refresh_field("receive_payment")
		cur_frm.refresh()
	}
});

function calculate_balance(frm) {
	if (frm.doc.total_invoice_amount) {
		if(!frm.doc.advance_amount) {frm.doc.advance_amount = 0}
		if(!frm.doc.discount_amount) {frm.doc.discount_amount = 0}
		frm.set_value("balance_amount", frm.doc.total_invoice_amount - frm.doc.advance_amount - frm.doc.discount_amount)
		frm.refresh_field("balance_amount")
		frm.set_value("outstanding_amount", frm.doc.balance_amount)
		frm.refresh_field("outstanding_amount")
	}	
}

cur_frm.add_fetch("ehf_name","customer","customer")
cur_frm.add_fetch("ehf_name","private","owned_by")
cur_frm.add_fetch("branch","branch","cost_center")
//cur_frm.add_fetch("ehf_name","advance_amount","advance_amount")


frappe.ui.form.on("Hire Charge Invoice", "refresh", function(frm) {
    cur_frm.set_query("ehf_name", function() {
        return {
            "filters": {
                "payment_completed": 0,
		"docstatus": 1,
		"branch": frm.doc.branch
            }
        };
    });
})

frappe.ui.form.on('Hire Invoice Advance', {
	"allocated_amount": function(frm, cdt, cdn) {
		var item = locals[cdt][cdn]
		if(item.allocated_amount >= 0 && item.allocated_amount <= item.actual_advance_amount) {
			calculate_advance_total(frm)
		}
		else {
			frappe.msgprint("Allocated Amount should be between 0 and advance amount")
			frm.set_value("allocated_amount", item.actual_advance_amount)
			frm.refresh_field("allocated_amount")
		}
	}
})

function calculate_advance_total(frm) {
	var total = 0;
	var bal_total = 0;
	frm.doc.advances.forEach(function(d) { 
		total += d.allocated_amount
		bal_total += d.balance_advance_amount
	})
	frm.set_value("advance_amount", total)
	frm.set_value("balance_advance_amount", bal_total)
	frm.refresh_field("advance_amount")
	frm.refresh_field("balance_advance_amount")
}
	
function get_vehicle_logs(form) {
	frappe.call({
		method: "erpnext.fleet_management.doctype.hire_charge_invoice.hire_charge_invoice.get_vehicle_logs",
		async: false,
		args: {
			"form": form,
		},
		freeze: true,
		freeze_message: "Loading Logbook Data...... Please Wait",
		callback: function(r) {
			if(r.message) {
				var total_invoice_amount = 0;
				cur_frm.clear_table("items");
				r.message.forEach(function(logbook) {
				        var row = frappe.model.add_child(cur_frm.doc, "Hire Invoice Details", "items");
					row.vehicle_logbook = logbook['name']
					row.registration_number = logbook['registration_number']
					row.total_work_hours = logbook['total_work_time']
					row.total_idle_hours = logbook['total_idle_time']
					row.equipment = logbook['equipment']
					row.rate_type = logbook['rate_type']
					row.work_rate = logbook['work_rate']
					row.idle_rate = logbook['idle_rate']
					row.amount_idle = logbook['total_idle_time'] * logbook['idle_rate']
					row.amount_work = logbook['total_work_time'] * logbook['work_rate']
					row.number_of_days = logbook['no_of_days']
					row.total_amount = (row.amount_idle + row.amount_work)
					refresh_field("items");

					total_invoice_amount += (row.amount_idle + row.amount_work)
					
					// frappe.call({
					// 	method: "erpnext.fleet_management.doctype.hire_charge_invoice.hire_charge_invoice.get_vehicle_accessories",
					// 	async: false,
					// 	args: {
					// 		"form": form,
					// 		"equipment": logbook['equipment']
					// 	},
					// 	callback: function(r) {
					// 		if(r.message) {
					// 			r.message.forEach(function(access) {
					// 				var row = frappe.model.add_child(cur_frm.doc, "Hire Invoice Details", "items");
					// 				row.vehicle_logbook = logbook['name']
					// 				row.registration_number = access['name']
					// 				row.equipment = logbook['equipment']
					// 				row.rate_type = logbook['rate_type']
					// 				row.total_work_hours = logbook['total_work_time']
					// 				row.total_idle_hours = logbook['total_idle_time']
					// 				row.work_rate = access['work']
					// 				row.idle_rate = access['idle']
					// 				row.amount_idle = logbook['total_idle_time'] * access['idle']
					// 				row.amount_work = logbook['total_work_time'] * access['work']
					// 				row.number_of_days = logbook['no_of_days']
					// 				row.total_amount = (row.amount_idle + row.amount_work)
					// 				refresh_field("items");

					// 				total_invoice_amount += (row.amount_idle + row.amount_work)
					// 			})
					// 		}
					// 	}
					// });
				});

				cur_frm.set_value("total_invoice_amount", total_invoice_amount)
				cur_frm.refresh_field("total_invoice_amount")
				cur_frm.refresh()
			}
			else {
				frappe.msgprint("No Vehicle Logs found!")
			}
		}
	})
}

//Get Advance Details
function get_advances(hire_name) {
	console.log(hire_name)
	frappe.call({
		method: "erpnext.fleet_management.doctype.hire_charge_invoice.hire_charge_invoice.get_advances",
		args: {
			"hire_name": hire_name,
		},
		callback: function(r) {
			if(r.message) {
				var total_advance_amount = 0;
				cur_frm.clear_table("advances");
				r.message.forEach(function(adv) {
				        var row = frappe.model.add_child(cur_frm.doc, "Hire Invoice Advance", "advances");
					row.jv_name = adv['name']
					row.reference_row = adv['reference_row']
					row.actual_advance_amount = adv['amount']
					row.allocated_amount = adv['amount']
					row.advance_account = adv['advance_account']
					row.advance_cost_center = adv['cost_center']
					row.remarks = adv['remark']
					refresh_field("advances");

					total_advance_amount += row.allocated_amount
				});
				cur_frm.set_value("advance_amount", total_advance_amount)
				cur_frm.refresh()
			}
			else {
				frappe.msgprint("No Advances found!")
			}
		}
	})
}

cur_frm.cscript.receive_payment = function(){
	var doc = cur_frm.doc;
	frappe.ui.form.is_saving = true;
	frappe.call({
		method: "erpnext.fleet_management.doctype.hire_charge_invoice.hire_charge_invoice.make_bank_entry",
		args: {
			"frm": cur_frm.doc.name,
		},
		callback: function(r){
			cur_frm.reload_doc();
		},
		always: function() {
			frappe.ui.form.is_saving = false;
		}
	});
}

