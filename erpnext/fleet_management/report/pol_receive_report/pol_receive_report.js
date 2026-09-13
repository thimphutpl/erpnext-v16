// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["POL Receive Report"] = {
	"filters": [
		{
			"fieldname":"branch",
			"label": ("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"width": "100",
			"reqd": 1
		},
		{
			"fieldname":"from_date",
			"label": ("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": ("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1
		},
		{
                        "fieldname": "direct",
                        "label": ("Show Only Direct Consumption"),
                        "fieldtype": "Check",
                        "default": 0
                },
		{
                        "fieldname": "own_cc",
                        "label": ("Show Own CC Issue/Receive Only"),
                        "fieldtype": "Check",
                        "default": 0
                },
	]
};


