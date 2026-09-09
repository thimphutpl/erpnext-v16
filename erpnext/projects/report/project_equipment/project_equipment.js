// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Project Equipment"] = {
	"filters": [
		{	"fieldname":"project",
                        "label": ("Project"),
                        "fieldtype": "Link",
                        "options": "Project",
                        "width": "100",
                  
		},
                {
                        "fieldname":"from_date",
                        "label": ("From Date"),
                        "fieldtype": "Date",
                        "width": "80",
                },
                {
                        "fieldname":"to_date",
                        "label": ("To Date"),
                        "fieldtype": "Date",
			"width": "80",
		},

	]
}
