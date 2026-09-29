// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Project Manpower"] = {
	"filters": [
		{
			"fieldname": 	"project",
			"label": 		("Project"),
			"fieldtype": 	"Link",
			"options":		"Project",
			"reqd": 0,
			"width": "200"
		}
	]
};
