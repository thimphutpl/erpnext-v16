// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project Hindrance", {
	refresh(frm) {

	},
    onload: function (frm){
        frm.set_query("project", function (doc) {
			return {
				filters: {
					branch: doc.branch,
                    docstatus: 0,
				},
			};
		});
    }
});
