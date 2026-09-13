// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Hire Charge Parameter', {
	refresh: function(frm) {
		disable_drag_drop(frm)
	},

	onload: function(frm) {
		disable_drag_drop(frm);
	},

	"items_on_form_rendered": function(frm, grid_row, cdt, cdn) {
		var row = cur_frm.open_grid_row();
		var d = get_today().toString()
		if(!row.grid_form.fields_dict.from_date.value) {
			row.grid_form.fields_dict.from_date.set_value(d.substring(8) + "-" + d.substring(5, 7) + "-" + d.substring(0, 4))
		}
		if(!row.grid_form.fields_dict.rate_fuel.value) {
			row.grid_form.fields_dict.rate_fuel.set_value(frm.doc.with_fuel)
		}
		if(!row.grid_form.fields_dict.rate_wofuel.value) {
			row.grid_form.fields_dict.rate_wofuel.set_value(frm.doc.without_fuel)
		}
		if(!row.grid_form.fields_dict.idle_rate.value) {
			row.grid_form.fields_dict.idle_rate.set_value(frm.doc.idle)
		}
                if(!row.grid_form.fields_dict.rate_fuel_internal.value) {
                        row.grid_form.fields_dict.rate_fuel_internal.set_value(frm.doc.with_fuel_internal)
                }
                if(!row.grid_form.fields_dict.rate_wofuel_internal.value) {
                        row.grid_form.fields_dict.rate_wofuel_internal.set_value(frm.doc.without_fuel_internal)
                }
                if(!row.grid_form.fields_dict.idle_rate_internal.value) {
                        row.grid_form.fields_dict.idle_rate_internal.set_value(frm.doc.idle_internal)
                }
		if(!row.grid_form.fields_dict.yard_hours.value) {
			row.grid_form.fields_dict.yard_hours.set_value(frm.doc.lph)
		}
		if(!row.grid_form.fields_dict.yard_distance.value) {
			row.grid_form.fields_dict.yard_distance.set_value(frm.doc.kph)
		}
		if(!row.grid_form.fields_dict.perf_bench.value) {
			row.grid_form.fields_dict.perf_bench.set_value(frm.doc.benchmark)
		}
		if(!row.grid_form.fields_dict.main_int.value) {
			row.grid_form.fields_dict.main_int.set_value(frm.doc.interval)
		}
		row.grid_form.fields_dict.from_date.refresh()
	},
});

function disable_drag_drop(frm) {
	frm.page.body.find('[data-fieldname="items"] [data-idx] .data-row').removeClass('sortable-handle');
}

frappe.ui.form.on("Hire Charge Parameter", "refresh", function(frm) {
    cur_frm.set_query("equipment_model", function() {
        return {
            "filters": {
		"equipment_type": frm.doc.equipment_type
            }
        };
    });
})

// frappe.ui.form.on("Hire Charge Parameter", "refresh", function(frm) {
//     cur_frm.set_query("registration_number", function() {
//         return {
//             "filters": {
// 		"equipment_type": frm.doc.equipment_type
//             }
//         };
//     });
// })


// frappe.ui.form.on("Hire Charge Parameter", {
//     refresh: function (frm) {
//         frm.set_query("registration_number", function () {
//             if (!frm.doc.equipment_type) {
//                 frappe.msgprint(__('Please select Equipment Type first.'));
//                 return;
//             }
//             return {
//                 // query: "erpnext.fleet_management.doctype.hire_charge_parameter.hire_charge_parameter.fetch_registration_numbers",
//                 query: "erpnext.fleet_management.doctype.equipment.equipment.fetch_registration_numbers",
//                 filters: {
//                     equipment_type: frm.doc.equipment_type
//                 }
//             };
//         });
//     }
// });

// frappe.ui.form.on("Hire Charge Parameter", {
//     registration_number: function (frm) {
//         // Ensure the selected value persists in the field
//         frm.refresh_field("registration_number");
//     }
// });


frappe.ui.form.on("Equipment", {
    refresh: function (frm) {
        frm.set_query("registration_number", function () {
            if (!frm.doc.equipment_type) {
                frappe.msgprint(__('Please select Equipment Type first.'));
                return;
            }
            return {
                // query: "erpnext.fleet_management.doctype.hire_charge_parameter.hire_charge_parameter.fetch_registration_numbers",
                query: "erpnext.fleet_management.doctype.equipment.equipment.fetch_registration_numbers",
                filters: {
                    equipment_type: frm.doc.equipment_type
                }
            };
        });
    }
});

frappe.ui.form.on("Equipment", {
    registration_number: function (frm) {
        // Ensure the selected value persists in the field
        frm.refresh_field("registration_number");
    }
});


frappe.ui.form.on('Hire Charge Item', {
        before_items_remove: function(frm, cdt, cdn) {
                doc = locals[cdt][cdn]
                if(!doc.__islocal) {
                        frappe.throw("Cannot delete saved Items")
                }
        }
})

