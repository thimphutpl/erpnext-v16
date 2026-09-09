// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.projects");

frappe.ui.form.on("Task", {
	setup: function (frm) {
		frm.make_methods = {
			Timesheet: () =>
				frappe.model.open_mapped_doc({
					method: "erpnext.projects.doctype.task.task.make_timesheet",
					frm: frm,
				}),
		};

		// Default values set as follows by SHIV on 2017/08/18
		frm.set_value("target_uom","Percent");
		frm.set_value("target_quantity",100);
	},

	refresh: function (frm) {
		var doc = frm.doc;
		if(doc.__islocal) {
			if(!frm.doc.exp_end_date) {
				frm.set_value("exp_end_date", frappe.datetime.add_days(new Date(), 7));
			}
		}

		if(!doc.__islocal) {
			// ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
			// Follwoing view option added by SHIV on 2017/08/17
			if(frappe.model.can_read("Project")) {
				frm.add_custom_button(__("Project"), function() {
					frappe.route_options = {"name": doc.project}
					frappe.set_route("Form", "Project", doc.project);
				}, __("View"), true);
			}			
			// +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++
			if(frappe.model.can_read("Timesheet")) {
				frm.add_custom_button(__("Timesheet"), function() {
					frappe.route_options = {"project": doc.project, "task": doc.name}
					frappe.set_route("List", "Timesheet");
				}, __("View"), true);
			}

			if(frm.perm[0].write) {
				if(frm.doc.status!=="Closed" && frm.doc.status!=="Cancelled") {
					frm.add_custom_button(__("Close"), function() {
						frm.set_value("status", "Closed");
						frm.save();
					});
				} else {
					frm.add_custom_button(__("Reopen"), function() {
						frm.set_value("status", "Open");
						frm.save();
					});
				}
			}
		}
	},

	onload: function (frm) {
		frm.set_query("task", "depends_on", function () {
			let filters = {
				name: ["!=", frm.doc.name],
				status: ["!=", "Closed"],
				is_group: ["=", 0],
			};
			if (frm.doc.project) filters["project"] = frm.doc.project;
			return {
				filters: filters,
			};
		});

		frm.set_query("parent_task", function () {
			let filters = {
				is_group: 1,
				name: ["!=", frm.doc.name],
			};
			if (frm.doc.project) filters["project"] = frm.doc.project;
			return {
				filters: filters,
			};
		});
	},

	is_group: function (frm) {
		frappe.call({
			method: "erpnext.projects.doctype.task.task.check_if_child_exists",
			args: {
				name: frm.doc.name,
			},
			callback: function (r) {
				if (r.message.length > 0) {
					let message = __(
						"Cannot convert Task to non-group because the following child Tasks exist: {0}.",
						[r.message.join(", ")]
					);
					frappe.msgprint(message);
					frm.reload_doc();
				}
			},
		});
	},

	validate: function (frm) {
		frm.doc.project && frappe.model.remove_from_locals("Project", frm.doc.project);
	},
});
