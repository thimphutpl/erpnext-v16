// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Measurement Book Register"] = {
	"filters": [
		{
			"fieldname" : "project",
			"label": ("Project"),
			"fieldtype" : "Link",
			"options" : "Project"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype":"Date",
			"default": frappe.defaults.get_user_default("year_start_date"),
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
		}
	]
}