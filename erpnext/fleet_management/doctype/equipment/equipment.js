// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Equipment", {
    setup: function (frm) {
        frm.set_query("fuel_type", function(){
            return {
                filters: {
                    'is_pol_item': 1,
                    'disabled': 0,
                }
            }
        });
    },

	refresh(frm) {

	},
});
