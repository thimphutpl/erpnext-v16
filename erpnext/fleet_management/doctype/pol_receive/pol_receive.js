// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('POL Receive', {	
	setup(frm){
        frm.set_query("equipment", function(){
            return {
                filters: {
                    'company': frm.doc.company,
                    'branch': frm.doc.branch,
                    'disabled': 0,
                }
            }
        });

        frm.set_query("fuelbook", function(){
            return {
                filters: {
                    'equipment': frm.doc.equipment,
                    'disabled': 0,
                }
            }
        });
    },

	onload: function (frm) {
		let grid = frm.fields_dict['advances'].grid;
        grid.cannot_add_rows = true;
	},

	refresh: function(frm) {
		if (frm.doc.docstatus == 1) {
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
	},

	get_advances: function (frm) {
		get_pol_advance(frm);
		//get_previous_km_reading(frm);
	},

	
	// fuelbook: function (frm) {
	// 	get_pol_advance(frm);
	// 	get_previous_km_reading(frm);
	// },
	// supplier: function (frm) {
	// 	if (frm.doc.for_machineries) {
	// 		get_pol_advance(frm);
	// 	}
	// 	get_previous_km_reading(frm);
	// },

	current_km: function(frm) {
        if (flt(frm.doc.current_km) < flt(frm.doc.previous_km)) {
            frappe.msgprint(__('Current KM cannot be less than Previous KM'), __('Validation Error'));
            frm.set_value('current_km', frm.doc.previous_km);
        } else {
            frm.set_value('km_difference', flt(frm.doc.current_km) - flt(frm.doc.previous_km));
			frm.set_value('mileage', flt(frm.doc.km_difference) / flt(frm.doc.total_qty));
        }
    }
});

frappe.ui.form.on('POL Receive Item', {
	qty: function (frm, cdt, cdn) {
		calculate_amount(frm, cdt, cdn);
		calculate_total_amount(frm);
	},

	rate: function (frm, cdt, cdn) {
		calculate_amount(frm, cdt, cdn);
		calculate_total_amount(frm);
	},
	items_add: function (frm, cdt, cdn) {
        let child = locals[cdt][cdn];
        let stock_uom = frm.doc.uom;
        frappe.model.set_value(child.doctype, child.name, 'uom', stock_uom);
        frm.refresh_field('items');
    }
});

var calculate_amount = function(frm, cdt, cdn) {
	let child = locals[cdt][cdn];
	let amount = child.qty * child.rate
	frappe.model.set_value(cdt, cdn, 'amount', parseFloat(amount));
	frm.refresh_field("amount", cdt, cdn)
}

var calculate_total_amount = function(frm){
	var me = frm.doc.items || [];
	var total_amount = 0.00;
	var total_qty = 0.00;
	
	if(frm.doc.docstatus != 1)
	{
		for(var i=0; i<me.length; i++){
			if(me[i].amount){
				total_amount += parseFloat(me[i].amount);
				total_qty += parseFloat(me[i].qty);
			}
		}
		
		cur_frm.set_value("total_amount", (total_amount));
		cur_frm.set_value("total_qty", (total_qty));
	}
}

var get_pol_advance = (frm) => {
	if ((frm.doc.equipment && frm.doc.fuelbook) || (frm.doc.equipment && frm.doc.supplier)) {
		frappe.call({
			method: 'get_pol_advance',
			doc: frm.doc,
			callback: ()=> {
				cur_frm.refresh_fields()
				frm.dirty()
				get_previous_km_reading(frm);
			}
		})
	}
}

var get_previous_km_reading = (frm) => {
	if (frm.doc.equipment && frm.doc.fuelbook && frm.doc.for_machineries !== 1) {
		frappe.call({
			method: 'get_previous_km_reading',
			doc: frm.doc,
			callback: (r) => {
				console.log(r.message);
				
				frm.set_value('previous_km', r.message);
				frm.refresh_field("previous_km");
				frm.refresh_fields()
			}
		})
	}
}
