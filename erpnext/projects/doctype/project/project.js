// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
frappe.ui.form.on("Project", {
	setup(frm) {
		frm.make_methods = {
			Timesheet: () => {
				open_form(frm, "Timesheet", "Timesheet Detail", "time_logs");
			},
			"Purchase Order": () => {
				open_form(frm, "Purchase Order", "Purchase Order Item", "items");
			},
			"Purchase Receipt": () => {
				open_form(frm, "Purchase Receipt", "Purchase Receipt Item", "items");
			},
			"Purchase Invoice": () => {
				open_form(frm, "Purchase Invoice", "Purchase Invoice Item", "items");
			},
		};
	},
	onload: function (frm) {
		enable_disable(frm);
		const so = frm.get_docfield("sales_order");
		so.get_route_options_for_new_doc = () => {
			if (frm.is_new()) return {};
			return {
				customer: frm.doc.customer,
				project_name: frm.doc.name,
			};
		};

		frm.set_query("user", "users", function () {
			return {
				query: "erpnext.projects.doctype.project.project.get_users_for_project",
			};
		});

		frm.set_query("department", function (doc) {
			return {
				filters: {
					company: doc.company,
				},
			};
		});

		// sales order
		frm.set_query("sales_order", function () {
			var filters = {
				project: ["in", frm.doc.__islocal ? [""] : [frm.doc.name, ""]],
			};

			if (frm.doc.customer) {
				filters["customer"] = frm.doc.customer;
			}

			return {
				filters: filters,
			};
		});

		frm.set_query("cost_center", () => {
			return {
				filters: {
					company: frm.doc.company,
				},
			};
		});
	},

	refresh: function (frm) {
		enable_disable(frm);
		// ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
		if(!frm.doc.__islocal){
			if(in_list([...frappe.user_roles], 'Admin')){
				frm.add_custom_button(__("Change Status"), function(){frm.trigger("change_status_ongoing")});
			}
			frm.add_custom_button(__("Advance"), function(){frm.trigger("make_project_advance")},__("Make"), "icon-file-alt");
			frm.add_custom_button(__("BOQ"), function(){frm.trigger("make_boq")},__("Make"), "icon-file-alt");
			frm.add_custom_button(__("Extension of Time"), function(){frm.trigger("extension_of_time")},__("Make"), "icon-file-alt");
			frm.add_custom_button(__("Project Register"), function(){
					frappe.route_options = {
						project: frm.doc.name,
						additional_info: 1
					};
					frappe.set_route("query-report", "Project Register");
				},__("Reports"), "icon-file-alt"
			);
			frm.add_custom_button(__("Manpower"), function(){
					frappe.route_options = {
						project: frm.doc.name
					};
					frappe.set_route("query-report", "Project Manpower");
				},__("Reports"), "icon-file-alt"
			);
		}
		// +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++

		if (frm.doc.__islocal) {
			frm.web_link && frm.web_link.remove();
		} else {
			frm.add_web_link("/projects?project=" + encodeURIComponent(frm.doc.name));

			frm.trigger("show_dashboard");
		}
		frm.trigger("set_custom_buttons");
		// +++++++++++++++++++++ Begins +++++++++++++++++++++
		if(frm.doc.docstatus === 0){
			enable_disable_items(frm);
		}
		// +++++++++++++++++++++ Ends +++++++++++++++++++++
	},

	set_custom_buttons: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(
				__("Duplicate Project with Tasks"),
				() => {
					frm.events.create_duplicate(frm);
				},
				__("Actions")
			);

			frm.add_custom_button(
				__("Update Total Purchase Cost"),
				() => {
					frm.events.update_total_purchase_cost(frm);
				},
				__("Actions")
			);

			frm.trigger("set_project_status_button");

			if (frappe.model.can_read("Task")) {
				frm.add_custom_button(
					__("Gantt Chart"),
					function () {
						frappe.route_options = {
							project: frm.doc.name,
						};
						frappe.set_route("List", "Task", "Gantt");
					},
					__("View")
				);

				frm.add_custom_button(
					__("Kanban Board"),
					() => {
						frappe
							.call(
								"erpnext.projects.doctype.project.project.create_kanban_board_if_not_exists",
								{
									project: frm.doc.name,
								}
							)
							.then(() => {
								frappe.set_route("List", "Task", "Kanban", frm.doc.project_name);
							});
					},
					__("View")
				);
			}
		}
	},

	update_total_purchase_cost: function (frm) {
		frappe.call({
			method: "erpnext.projects.doctype.project.project.recalculate_project_total_purchase_cost",
			args: { project: frm.doc.name },
			freeze: true,
			freeze_message: __("Recalculating Purchase Cost against this Project..."),
			callback: function (r) {
				if (r && !r.exc) {
					frappe.msgprint(__("Total Purchase Cost has been updated"));
					frm.refresh();
				}
			},
		});
	},

	set_project_status_button: function (frm) {
		frm.add_custom_button(
			__("Set Project Status"),
			() => {
				let d = new frappe.ui.Dialog({
					title: __("Set Project Status"),
					fields: [
						{
							fieldname: "status",
							fieldtype: "Select",
							label: "Status",
							reqd: 1,
							options: "Completed\nCancelled",
						},
					],
					primary_action: function () {
						frm.events.set_status(frm, d.get_values().status);
						d.hide();
					},
					primary_action_label: __("Set Project Status"),
				}).show();
			},
			__("Actions")
		);
	},

	create_duplicate: function (frm) {
		return new Promise((resolve) => {
			frappe.prompt("Project Name", (data) => {
				frappe
					.xcall("erpnext.projects.doctype.project.project.create_duplicate_project", {
						prev_doc: frm.doc,
						project_name: data.value,
					})
					.then(() => {
						frappe.set_route("Form", "Project", data.value);
						frappe.show_alert(__("Duplicate project has been created"));
					});
				resolve();
			});
		});
	},

	set_status: function (frm, status) {
		frappe.confirm(__("Set Project and all Tasks to status {0}?", [status.bold()]), () => {
			frappe
				.xcall("erpnext.projects.doctype.project.project.set_project_status", {
					project: frm.doc.name,
					status: status,
				})
				.then(() => {
					frm.reload_doc();
				});
		});
	},

	make_boq: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.project.project.make_boq",
			frm: frm
		});
	},

	extension_of_time: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.project.project.extension_of_time",
			frm: frm
		});
	},
	// ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
	// Following function created by SHIV on 02/09/2017
	make_project_advance: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.project.project.make_project_advance",
			frm: frm
		});
	},
	// +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++
	change_status_ongoing: function(frm){
		return frappe.call({
			method: "erpnext.projects.doctype.project.project.change_status_ongoing",
			args:{
				'project_id': frm.doc.name
			},
			callback: function(r, rt) {
				if(r.message){
					frappe.msgprint("Project Status changed to Ongoing");
				}
				cur_frm.reload_doc()
			},
		});
	},

	tasks_refresh: function(frm) {
		var grid = frm.get_field('tasks').grid;
		grid.wrapper.find('select[data-fieldname="status"]').each(function() {
			if($(this).val()==='Open') {
				$(this).addClass('input-indicator-open');
			} else {
				$(this).removeClass('input-indicator-open');
			}
		});
	},

	project_type: function(frm){
		enable_disable(frm);
		update_party_info(frm.doc);
	},
	party_type: function(frm){
		enable_disable(frm);
		update_party_info(frm.doc);
	},
	party: function(frm){
		update_party_info(frm.doc);
	},
	project_category: function(){
		cur_frm.set_value('project_sub_category','');
		cur_frm.fields_dict['project_sub_category'].get_query = function(doc, dt, dn) {
		   return {
				filters:{"project_category": doc.project_category}
		   }
		}
	}
});

function open_form(frm, doctype, child_doctype, parentfield) {
	frappe.model.with_doctype(doctype, () => {
		let new_doc = frappe.model.get_new_doc(doctype);

		// add a new row and set the project
		let new_child_doc = frappe.model.get_new_doc(child_doctype);
		new_child_doc.project = frm.doc.name;
		new_child_doc.parent = new_doc.name;
		new_child_doc.parentfield = parentfield;
		new_child_doc.parenttype = doctype;
		new_doc[parentfield] = [new_child_doc];
		new_doc.project = frm.doc.name;

		frappe.ui.form.make_quick_entry(doctype, null, null, new_doc);
	});
}

var update_party_info=function(doc){
	cur_frm.call({
		method: "update_party_info",
		doc:doc
	});
}

var enable_disable = function(frm){
	// Display tasks only after the project is saved
	frm.toggle_display("activity_and_tasks", !frm.is_new());
	frm.toggle_display("activity_tasks", !frm.is_new());
	frm.toggle_display("sb_additional_tasks", !frm.is_new());
	frm.toggle_display("additional_tasks", !frm.is_new());
	
	//cur_frm.toggle_reqd("party_type", frm.doc.project_type=="External");
	//cur_frm.toggle_reqd("party", frm.doc.party_type || frm.doc.project_type=="External");
	cur_frm.toggle_reqd("party_type", 1);
	cur_frm.toggle_reqd("party", 1);
	
	if (frm.doc.project_type == "External") {
		frm.set_query("party_type", function() {
			return {
				//filters: {"name": ["in", ["Customer", "Supplier"]]}
				filters: {"name": ["in", ["Supplier"]]}
			}
		});
		//cur_frm.toggle_reqd("party", frm.doc.party_type);
	} else {
		frm.set_query("party_type", function() {
			return {
				//filters: {"name": ["in", ["Employee"]]}
				filters: {"name": ["in", ["Customer"]]}
			}
		});
	}
}

// ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
// Following block of code added by SHIV on 11/08/2017
frappe.ui.form.on("Activity Tasks", {
	activity_tasks_remove: function(frm, doctype, name){
		calculate_work_quantity(frm);
	},
	edit_task: function(frm, doctype, name) {
		var doc = frappe.get_doc(doctype, name);
		if(doc.task_id) {
			frappe.set_route("Form", "Task", doc.task_id);
		} else {
			msgprint(__("Save the document first."));
		}
	},
	view_timesheet: function(frm, doctype, name){
		var doc = frappe.get_doc(doctype, name);
		if(doc.task_id){
			frappe.route_options = {"project": frm.doc.name, "task": doc.task_id}
			frappe.set_route("List", "Timesheet");
		} else {
			msgprint(__("Save the document first."));
		}
	},
	status: function(frm, doctype, name) {
		frm.trigger('tasks_refresh');
	},
	work_quantity: function(frm, doctype, name){
		calculate_work_quantity(frm);
	},
});

frappe.ui.form.on("Additional Tasks", {
	activity_tasks_remove: function(frm, doctype, name){
		calculate_work_quantity(frm);
	},
	edit_task: function(frm, doctype, name) {
		var doc = frappe.get_doc(doctype, name);
		if(doc.task_id) {
			frappe.set_route("Form", "Task", doc.task_id);
		} else {
			msgprint(__("Save the document first."));
		}
	},
	view_timesheet: function(frm, doctype, name){
		var doc = frappe.get_doc(doctype, name);
		if(doc.task_id){
			frappe.route_options = {"project": frm.doc.name, "task": doc.task_id}
			frappe.set_route("List", "Timesheet");
		} else {
			msgprint(__("Save the document first."));
		}
	},
	status: function(frm, doctype, name) {
		frm.trigger('tasks_refresh');
	},
	work_quantity: function(frm, doctype, name){
		calculate_work_quantity(frm);
	},
});

function enable_disable_items(frm){
	var toggle_fields = ["branch"];
	
	if(frm.doc.branch){
		if(in_list([...frappe.user_roles], "CPBD")){
			toggle_fields.forEach(function(field_name){
				frm.set_df_property(field_name, "read_only", 0);
			});
		}
		else {
			toggle_fields.forEach(function(field_name){
				frm.set_df_property(field_name, "read_only", 1);
			});
		}
	}
}

// ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
// Following function created by SHIV on 2017/08/17
var calculate_work_quantity = function(frm){
	var at = frm.doc.activity_tasks || [];
	var adt= frm.doc.additional_tasks || [];
	total_work_quantity = 0.0;
	total_work_quantity_complete = 0.0;
	total_add_work_quantity = 0.0;
	total_add_work_quantity_complete = 0.0;

	for(var i=0; i<at.length; i++){
		//console.log(at[i].is_group);
		if (at[i].work_quantity && !at[i].is_group){
			total_work_quantity += at[i].work_quantity || 0;
			total_work_quantity_complete += at[i].work_quantity_complete || 0;
		}
	}
	
	for(var i=0; i<adt.length; i++){
		//console.log(at[i].is_group);
		if (adt[i].work_quantity && !adt[i].is_group){
			total_add_work_quantity += adt[i].work_quantity || 0;
			total_add_work_quantity_complete += adt[i].work_quantity_complete || 0;
		}
	}
	
	cur_frm.set_value("tot_wq_percent",total_work_quantity);
	cur_frm.set_value("tot_wq_percent_complete",total_work_quantity_complete);
	cur_frm.set_value("tot_add_wq_percent",total_add_work_quantity);
	cur_frm.set_value("tot_add_wq_percent_complete",total_add_work_quantity_complete);
}
// +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++
frappe.ui.form.on("Project", "refresh", function(frm) {
    cur_frm.set_query("cost_center", function() {
        return {
            "filters": {
			"is_group": 0,
			"disabled": 0
            }
        };
    });
})