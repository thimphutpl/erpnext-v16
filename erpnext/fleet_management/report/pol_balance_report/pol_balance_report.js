// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["POL Balance Report"] = {
	"filters": [
		{
			"fieldname": "branch",
			"label": ("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"width": "100",
		},
		{
			"fieldname":"to_date",
			"label" : ("Balance As Of"),
			"fieldtype": "Date",
			"width": "80",
			"reqd" : 1
		},          
		{
			"fieldname":"all_equipment",
			"label" : ("Tank Balance of All Equipments"),
			"fieldtype": "Check",
			"default": 0
		}
	]
}
