// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project Definition', {
	setup: function (frm) {
		frm.set_query("division", function () {
			return {
				filters: [
					["is_division", "=", "1"]
				]
			};
		});
		frm.set_query("section", function () {
			return {
				filters: {
					"is_section": 1,
					"parent_department": frm.doc.division
				}
			};
		});
	},
	refresh: function (frm) {
		if(frm.doc.docstatus == 1){
			frm.set_df_property("total_overall_project_cost","read_only",1);
		}
		frm.set_df_property("project_code", "read_only", frm.is_new() ? 0 : 1);
		if (frm.doc.docstatus == 1 && (frm.doc.status == "Created" || frm.doc.status == "Ongoing")) {
			frm.add_custom_button("Create Project Branch", function () {
				frappe.model.open_mapped_doc({
					method: "erpnext.projects.doctype.project_definition.project_definition.make_project",
					frm: cur_frm
				})
			}).addClass("btn-primary");
			frm.add_custom_button("Make Purchase Requistion", function () {
				frappe.model.open_mapped_doc({
					method: "erpnext.projects.doctype.project_definition.project_definition.make_purchase_requisition",
					frm: cur_frm
				})
			},
				__("Make")
			)
			frm.add_custom_button("Make Material Issue Request", function () {
				frappe.model.open_mapped_doc({
					method: "erpnext.projects.doctype.project_definition.project_definition.make_material_issue_request",
					frm: cur_frm
				})
			},
				__("Make")
			)
			cur_frm.add_custom_button("Make Stock Issue Entry",
				function (){
					frappe.model.open_mapped_doc({
						method: "erpnext.projects.doctype.project_definition.project_definition.make_stock_issue_entry",
						frm: cur_frm
					})
				},
				__("Make")
			)
			frm.add_custom_button("Make Stock Return Entry", function () {
				frappe.model.open_mapped_doc({
					method: "erpnext.projects.doctype.project_definition.project_definition.make_stock_return_entry",
					frm: cur_frm
				})
			},
				__("Make")
			)
			frm.add_custom_button("Update Progress", function () {
				frappe.call({
					method: "update_project_progress",
					doc: frm.doc,
					callback: function(){
						window.location.reload();
					}
				})
			}).addClass("btn-primary");
		}
		// if (frm.doc.docstatus == 1 && frm.doc.project_profile == "Internal") {
		// 	frm.add_custom_button("Monthly Settlement", function () {
		// 		frappe.model.open_mapped_doc({
		// 			method: "erpnext.projects.doctype.project_definition.project_definition.monthly_settlement",
		// 			frm: cur_frm
		// 		})
		// 	}).addClass("btn-primary");
		// }
		frappe.call({
			method: "erpnext.projects.doctype.project_definition.project_definition.get_project_cost",
			args: {
				project_definition: cur_frm.doc.name
			},
			callback: function (r, rt) {
				frm.refresh_fields()
				let total_cost = 0;
				frm.doc.project_sites.map((item) => {
					total_cost = total_cost + item.total_cost
				})
				frm.doc.total_overall_project_cost = total_cost
				cur_frm.refresh_fields()
			},
		});
		frm.refresh_fields();

		frappe.call({
			method: "check_logged_in_user_role",
			doc:frm.doc,
			callback: function(r){     
				console.log(r.message)
				toggle_remarks_display(frm, r.message[0])
			}
		})
	}
});
var toggle_remarks_display = function(frm, freeze_project){
	frm.set_df_property("freeze_project","read_only",freeze_project)
}