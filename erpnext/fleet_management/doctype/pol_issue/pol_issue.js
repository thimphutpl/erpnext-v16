// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('POL Issue', {
    // setup: function (frm) {
    //     frm.set_query("tanker", function () {
    //         return {
    //             query: "erpnext.fleet_management.doctype.pol_issue.pol_issue.get_tanker_data",
    //             filters: { branch: frm.doc.branch }
    //         };
    //     });
    // },
    tank_balance: function (frm) {
        console.log("tanker function triggered");
        // frappe.throw("tanker")
        if (frm.doc.tanker) {
            // frappe.throw("tankers")
            frappe.call({
                method: 'erpnext.fleet_management.doctype.pol_issue.pol_issue.get_tanker_details',
                args: { 
                    tanker: frm.doc.tanker, 
                    posting_date: frm.doc.posting_date, 
                    pol_type: frm.doc.pol_type 
                },
                callback: function (r) {
                    if (r.message) {
                        frm.set_value('tank_balance', r.message.balance);
                    }
                }
            });
        } else {
            frm.set_value('tank_balance', '');
        }
    },

	onload: function(frm) {
		if(!frm.doc.posting_date) {
			// frm.set_value("posting_date", get_today())
            frm.set_value('posting_date', frappe.datetime.now_date());
		}
        // frm.set_query("tanker", function () {
        //     return {
        //         query: "erpnext.fleet_management.doctype.pol_issue.pol_issue.get_tanker_data",
        //         filters: { branch: frm.doc.branch }
        //     };
        // });
	},

	refresh: function(frm) {
		if(frm.doc.docstatus == 1) {
			cur_frm.add_custom_button(__("Stock Ledger"), function() {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date,
					company: frm.doc.company
				};
				frappe.set_route("query-report", "Stock Ledger");
			}, __("View"));

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

		// cur_frm.set_query("pol_type", function () {
        //     return {
        //         filters: {
        //             disabled: 0,
        //             is_pol_item: 1
        //         }
        //     };
        // });

        // cur_frm.set_query("tanker", function () {
        //     if (!frm.doc.branch) {
        //         frappe.msgprint(__('Please select a branch first.'));
        //         return null;
        //     }
        //     return {
        //         query: "erpnext.fleet_management.doctype.pol_issue.pol_issue.equipment_query",
        //         filters: { branch: frm.doc.branch }
        //     };
        // });
	},

	tanker: function (frm) {
        if (frm.doc.equipment) {
            frappe.call({
                method: "erpnext.fleet_management.doctype.pol_issue.pol_issue.get_equipment_data", // Update with the correct path
                args: {
                    equipment_name: frm.doc.equipment,
                    // to_date: frm.doc.to_date,
                    // all_equipment: frm.doc.all_equipment || 1,
                    branch: frm.doc.branch
                },
                callback: function(response) {
                    if (response.message) {
                        let data = response.message;

                        // Process and display the fetched data
                        frappe.msgprint({
                            title: __('Fetched Equipment Data'),
                            message: `<pre>${JSON.stringify(data, null, 4)}</pre>`,
                            indicator: 'green'
                        });

                        // Optional: You can set a field value with specific data
                        if (data.length > 0) {
                            frm.set_value('tank_balance', data[0].balance);
                        }
                    } else {
                        frappe.msgprint(__('No data found for the selected equipment.'));
                    }
                }
            });
        } else {
            // Clear related fields if no equipment is selected
            frm.set_value('tank_balance', '');
        }
    },


	"items_on_form_rendered": function(frm, grid_row, cdt, cdn) {
		var row = cur_frm.open_grid_row();
		/*if(!row.grid_form.fields_dict.pol_type.value) {
			//row.grid_form.fields_dict.pol_type.set_value(frm.doc.pol_type)
                	row.grid_form.fields_dict.pol_type.refresh()
		}*/
	},

	"branch": function(frm) {
		return frappe.call({
			method: "erpnext.custom_utils.get_cc_warehouse",
			args: {
				"branch": frm.doc.branch
			},
			callback: function(r) {
				cur_frm.set_value("cost_center", r.message.cc)
				// cur_frm.set_value("warehouse", r.message.wh)
				cur_frm.refresh_fields()
			}
		})
	}
});

cur_frm.add_fetch("equipment", "registration_number", "equipment")

frappe.ui.form.on("POL Issue", "refresh", function(frm) {
    	cur_frm.set_query("pol_type", function() {
		return {
		    "filters": {
			"disabled": 0,
			"is_pol_item": 1
		    }
		};
	    });
	
	// cur_frm.set_query("tanker", function() {
	// 	return {
	// 		"query": "erpnext.fleet_management.doctype.pol_issue.pol_issue.equipment_query",
	// 		// "query": "erpnext.fleet_management.doctype.pol_issue.pol_issue.get_equipment_data",
			
	// 		filters: {'branch': frm.doc.branch}
	// 	}
	// })

	
	cur_frm.set_query("warehouse", function() {
                return {
                        query: "erpnext.controllers.queries.filter_branch_wh",
                        filters: {'branch': frm.doc.branch}
                }
            });

        frm.fields_dict['items'].grid.get_field('equipment_warehouse').get_query = function(doc, cdt, cdn) {
                item = locals[cdt][cdn]
                return {
                        "query": "erpnext.controllers.queries.filter_branch_wh",
                        filters: {'branch': item.equipment_branch}
                }
        }

        frm.fields_dict['items'].grid.get_field('hiring_warehouse').get_query = function(doc, cdt, cdn) {
                item = locals[cdt][cdn]
                return {
                        "query": "erpnext.controllers.queries.filter_branch_wh",
                        filters: {'branch': item.hiring_branch}
                }
        }

	frm.fields_dict['items'].grid.get_field('equipment').get_query = function(doc, cdt, cdn) {
		doc = locals[cdt][cdn]
                
                        return {
                                filters: {
                                        "disabled": 0,
					"equipment_type": ["not in", ['Skid Tank', 'Barrel']]
                                }
                        }
                }
	
})

frappe.ui.form.on("POL Issue Item", "equipment", function(doc, cdt, cdn) {
	doc = locals[cdt][cdn]
	if(doc.equipment_branch) {
		return frappe.call({
			method: "erpnext.custom_utils.get_cc_warehouse",
			args: {
				"branch": doc.equipment_branch
			},
			callback: function(r) {
                console.log(r)
                frappe.model.set_value(cdt, cdn, "cost_center", r.message.cc)
				frappe.model.set_value(cdt, cdn, "equipment_cost_center", r.message.cc)
				frappe.model.set_value(cdt, cdn, "equipment_warehouse", r.message.wh)
				cur_frm.refresh_fields()
			}
		})
	}
})



frappe.ui.form.on("POL Issue Items", {
    equipment: function (frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn); // Get the specific row in the child table

        if (row.equipment_branch) {
            // Fetch Cost Center and Warehouse
            frappe.call({
                method: "erpnext.custom_utils.get_cc_warehouse",
                args: {
                    branch: row.equipment_branch
                },
                callback: function (r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "equipment_cost_center", r.message.cc);
                        frappe.model.set_value(cdt, cdn, "equipment_warehouse", r.message.wh);
                        frappe.model.set_value(cdt, cdn, "tank_capacity", r.message.wh);
                    }
                }
            });
        }

        if (row.equipment) {
            // Fetch Equipment Data
            frappe.call({
                method: "erpnext.fleet_management.doctype.pol_issue.pol_issue.get_equipment_datas",
                args: {
                    equipment: row.equipment,
                    all_equipment: frm.doc.all_equipment || 1,
                    branch: frm.doc.branch
                },
                callback: function (response) {
                    if (response.message) {
                        let data = response.message;

                        // Optional: Display fetched data
                        frappe.msgprint({
                            title: __('Fetched Equipment Data'),
                            message: `<pre>${JSON.stringify(data, null, 4)}</pre>`,
                            indicator: 'green'
                        });

                        // Set the balance in the current row
                        frappe.model.set_value(cdt, cdn, "equipment_balance", data[0]?.balance || 0);
                    } else {
                        frappe.msgprint(__('No data found for the selected equipment.'));
                        frappe.model.set_value(cdt, cdn, "equipment_balance", 0);
                    }
                }
            });
        } else {
            // Clear the field if no equipment is selected
            frappe.model.set_value(cdt, cdn, "equipment_balance", 0);
        }

        // Refresh fields to update UI
        cur_frm.refresh_fields();
    }
});




frappe.ui.form.on('POL Issue Items', {
    // Triggered when the 'equipment' field in the child table changes
    equipment: function (frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn); // Get the specific row in the child table

        if (row.equipment) {
            frappe.call({
                method: "erpnext.fleet_management.doctype.pol_issue.pol_issue.get_equipment_datas",
                args: {
                    equipment: row.equipment,
                    all_equipment: frm.doc.all_equipment || 1,
                    branch: frm.doc.branch
                },
                callback: function (response) {
                    if (response.message) {
                        let data = response.message;

                        // Optional: Display fetched data
                        frappe.msgprint({
                            title: __('Fetched Equipment Data'),
                            message: `<pre>${JSON.stringify(data, null, 4)}</pre>`,
                            indicator: 'green'
                        });

                        // Set the balance in the current row
                        frappe.model.set_value(cdt, cdn, "equipment_balance", data[0]?.balance || 0);
                        cur_frm.refresh_fields()
                    } else {
                        frappe.msgprint(__('No data found for the selected equipment.'));
                        frappe.model.set_value(cdt, cdn, "equipment_balance", 0);
                        cur_frm.refresh_fields()
                    }
                }
            });
        } else {
            // Clear the field if no equipment is selected
            frappe.model.set_value(cdt, cdn, "equipment_balance", 0);
        }
    }
});

