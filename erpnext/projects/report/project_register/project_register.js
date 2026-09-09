// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Project Register"] = {
	"filters": [
		{
			"fieldname": 	"project",
			"label": 		("Project"),
			"fieldtype": 	"Link",
			"options":		"Project"			
		},
		{
			"fieldname": 	"branch",
			"label": 		("Branch"),
			"fieldtype": 	"Link",
			"options":		"Branch"
		},
		{
			"fieldname": 	"project_category",
			"label": 	("Project Category"),
			"fieldtype": 	"Link",
			"options":	"Project Category"
		},	
		{
			"fieldname": 	"status",
			"label": 	("Status"),
			"fieldtype": 	"Select",
			options: "\nPlanning\nOngoing\nCompleted\nCancelled",
			
		},	
		{
			"fieldname":	"from_date",
			"label":		("From Date"),
			"fieldtype":	"Date",
			"reqd":0
		},
		{
			"fieldname":	"to_date",
			"label":		("To Date"),
			"fieldtype":	"Date",
			"reqd":0
		},
		{
			"fieldname":	"additional_info",
			"label":		("Additional Information"),
			"fieldtype":	"Check",
			"reqd":			0
		},
	]
};
