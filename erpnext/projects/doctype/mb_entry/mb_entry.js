// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("MB Entry", {
    setup: function(frm){
		frm.get_field('mb_entry_boq').grid.editable_fields = [
			{fieldname: 'item', columns: 3},
			{fieldname: 'is_selected', columns: 1},
			{fieldname: 'uom', columns: 1},
			{fieldname: 'entry_quantity', columns: 1},
			{fieldname: 'entry_rate', columns: 2},
			{fieldname: 'entry_amount', columns: 2}
		];		
	},

	onload: function(frm){
		calculate_totals(frm);
	},
	
	onload_post_render: function(frm){
		cur_frm.refresh();
	},

	refresh(frm) {
        //added new by cety on 8/19/2021
		if (frm.doc.docstatus == 1){
			cur_frm.add_custom_button(__('Accounting Ledger'), function() {
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
		//end
	},

    make_mb_invoice: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.mb_entry.mb_entry.make_mb_invoice",
			frm: frm
		});
	},	
	
	check_all: function(frm){
		check_uncheck_all(frm);
	}
});

frappe.ui.form.on("MB Entry BOQ",{
	entry_quantity: function(frm, cdt, cdn){
		child = locals[cdt][cdn];
		
		if(child.entry_quantity > child.act_quantity){
			msgprint(__("Invoice Quantity cannot be greater than balance quantity.").format(child.entry_quantity))
		}
		
		//if(child.entry_quantity && child.entry_rate){
		frappe.model.set_value(cdt, cdn, 'entry_amount', (parseFloat(child.entry_quantity)*parseFloat(child.entry_rate)).toFixed(2));
		//}
	},
	entry_amount: function(frm, cdt, cdn){
		var child = locals[cdt][cdn];
		var amount = flt(child.entry_quantity || 0.0)*flt(child.entry_rate || 0.0);
		
		if(child.entry_amount > child.act_amount){
			msgprint(__("Invoice Amount cannot be greater than balance amount."));
		} else {
			if(frm.doc.boq_type !== "Milestone Based" && flt(child.amount) != flt(amount)) {
				frappe.model.set_value(cdt, cdn, 'entry_amount', flt(amount));
			}
		}
		calculate_totals(frm);
	},
	is_selected: function(frm, cdt, cdn){
		calculate_totals(frm);
	},
});

var calculate_totals = function(frm){
	var me = frm.doc.mb_entry_boq || [];
	var total_entry_amount = 0.0, net_entry_amount =0.0;
	
	if(frm.doc.docstatus != 1)
	{
		for(var i=0; i<me.length; i++){
			if(me[i].entry_amount && me[i].is_selected==1){
				total_entry_amount += parseFloat(me[i].entry_amount);
			}
		}
		
		cur_frm.set_value("total_entry_amount",(total_entry_amount));
		cur_frm.set_value("total_balance_amount",(parseFloat(total_entry_amount || 0)-parseFloat(frm.doc.total_received_amount || 0)));
	}
}

var check_uncheck_all = function(frm){
	var meb =frm.doc.mb_entry_boq || [];

	for(var id in meb){
		frappe.model.set_value("MB Entry BOQ", meb[id].name, "is_selected", frm.doc.check_all);
	}
}
