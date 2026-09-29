// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("project", "branch", "branch");
cur_frm.add_fetch("project", "cost_center", "cost_center");
cur_frm.add_fetch("project","party_type","party_type");
cur_frm.add_fetch("project","party","party");

frappe.ui.form.on("BOQ", {
    setup: function(frm){
        frm.get_docfield("boq_item").allow_bulk_edit = 1;		
		
		frm.get_field('boq_item').grid.editable_fields = [
			{fieldname: 'boq_code', columns: 1},
			{fieldname: 'item', columns: 3},
			{fieldname: 'is_group', columns: 1},
			{fieldname: 'uom', columns: 1},
			{fieldname: 'quantity', columns: 1},
			{fieldname: 'rate', columns: 1},
			{fieldname: 'amount', columns: 2}
		];
		
		frm.get_field('boq_history_item').grid.editable_fields = [
			{fieldname: 'transaction_type', columns: 2},
			{fieldname: 'transaction_date', columns: 2},
			{fieldname: 'initial_amount', columns: 2},
			{fieldname: 'adjustment_amount', columns: 2},
			{fieldname: 'final_amount', columns: 2},
		];
	},

	refresh(frm) {
        // boq_item_html(frm);
		if(!frm.doc.__islocal && frm.doc.docstatus==1){
			if(frappe.model.can_read("BOQ Adjustment")) {
				frm.add_custom_button(__("Adjustments"), function() {
					frappe.route_options = {"boq": frm.doc.name}
					frappe.set_route("List", "BOQ Adjustment");
				}, __("View"), true);
			}

			if(frappe.model.can_read("MB Entry")) {
				frm.add_custom_button(__("MB Entries"), function() {
					frappe.route_options = {"boq": frm.doc.name}
					frappe.set_route("List", "MB Entry");
				}, __("View"), true);
			}			
			
			if(frappe.model.can_read("Project Invoice")) {
				frm.add_custom_button(__("Invoices"), function() {
					frappe.route_options = {"boq": frm.doc.name}
					frappe.set_route("List", "Project Invoice");
				}, __("View"), true);
			}			
		}
		
		frm.trigger("get_defaults");
		
		if(frm.doc.docstatus==1){
			frm.add_custom_button(__("Adjustment"),function(){frm.trigger("make_boq_adjustment")},
				__("Make"), "icon-file-alt"
			);
			if(frm.doc.party_type !== "Supplier"){
				frm.add_custom_button(__("Subcontract"), function(){frm.trigger("make_boq_subcontract")},__("Make"), "icon-file-alt");
			}
		}
		
		if(frm.doc.docstatus==1 && parseFloat(frm.doc.claimed_amount) < (parseFloat(frm.doc.total_amount)+parseFloat(frm.doc.price_adjustment))){
			
			frm.add_custom_button(__("Measurement Book Entry"),function(){frm.trigger("make_book_entry")},
				__("Make"), "icon-file-alt"
			);
			frm.add_custom_button(__("Invoice"),function(){frm.trigger("make_mb_invoice")},
				__("Make"), "icon-file-alt"
			);			
		}
	},
    make_boq_adjustment: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.boq.boq.make_boq_adjustment",
			frm: frm
		});
	},
	
	make_boq_subcontract: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.boq.boq.make_boq_subcontract",
			frm: frm
		});
	},
	
	make_mb_invoice: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.boq.boq.make_mb_invoice",
			frm: frm
		});
	},	
	
	make_book_entry: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.boq.boq.make_book_entry",
			frm: frm
		});
	},
	
	project: function(frm){
		frm.trigger("get_defaults");
	},
	
	get_defaults: function(frm){
		frm.add_fetch("project", "branch","branch");
		frm.add_fetch("project", "cost_center","cost_center");		
	},
	
});

frappe.ui.form.on("BOQ Item",{
	quantity: function(frm, cdt, cdn){
		calculate_amount(frm, cdt, cdn);
	},
	
	rate: function(frm, cdt, cdn){
		calculate_amount(frm, cdt, cdn);
	},
	
	amount: function(frm){
		calculate_total_amount(frm);
	},
})

var calculate_amount = function(frm, cdt, cdn){
	child = locals[cdt][cdn];
	amount = 0.0;
	
	//if(child.quantity && child.rate){
	amount = parseFloat(child.quantity)*parseFloat(child.rate)
	//}
	
	frappe.model.set_value(cdt, cdn, 'amount', parseFloat(amount));
	frappe.model.set_value(cdt, cdn, 'balance_quantity', parseFloat(child.quantity));
	frappe.model.set_value(cdt, cdn, 'balance_amount', parseFloat(amount));
}

var calculate_total_amount = function(frm){
	var bi = frm.doc.boq_item || [];
	var total_amount = 0.0, balance_amount = 0.0;
	
	for(var i=0; i<bi.length; i++){
		if (bi[i].amount){
			total_amount += parseFloat(bi[i].amount);
		}
	}
	balance_amount = parseFloat(total_amount) - parseFloat(frm.doc.received_amount)
	cur_frm.set_value("total_amount",total_amount);
	cur_frm.set_value("balance_amount",balance_amount);
}
