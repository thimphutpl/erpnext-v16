// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Project Progress Report"] = {
	"filters": [
		{
			"fieldname": "parent_project",
			"label": ("Parent Project"),
			"fieldtype": "Select",
			"options": ["", "GI Project", "DFG Project", "Other Project"],
			"on_change": function(query_report) {
				frappe.query_report.set_filter_value("project_definition", null);
				frappe.query_report.set_filter_value("project", null);
				// frappe.query_report.set_filter_value("task", null);
				frappe.query_report.refresh();
			},
			"reqd": 1
		},
		{
			"fieldname": "project_definition",
			"label": ("Gyalsung Academy(Project Definition)"),
			"fieldtype": "Link",
			"options": "Project Definition",
			"get_query": function() {
				var parent_project = frappe.query_report.get_filter_value("parent_project")
				return {
					'doctype': "Project Definition",
					'filters': [['project_category', '=', parent_project]]
				}
			},
			"on_change": function(query_report) {
				frappe.query_report.set_filter_value("project", null);
				// frappe.query_report.set_filter_value("task", null);
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "project",
			"label": ("Activity(Project)"),
			"fieldtype": "Link",
			"options": "Project",
			"get_query": function() {
				var project_definition = frappe.query_report.get_filter_value("project_definition")
				return { 'doctype': "Project",
						'filters': [
								['project_definition', '=', project_definition]
				]}
			},
			"on_change": function(query_report) {
				frappe.query_report.set_filter_value("task", null);
				frappe.query_report.refresh();
			}
		},
		// {
		// 	"fieldname": "task",
		// 	"label": ("Task"),
		// 	"fieldtype": "Link",
		// 	"options": "Task",
		// 	"get_query": function() {
		// 		var project = frappe.query_report.get_filter_value("project")
		// 		return { 'doctype': "Task",
		// 				'filters': [
		// 						['project', '=', project]
		// 		]}
		// 	},
		// },
	]
};
