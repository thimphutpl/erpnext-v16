// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Invoice Register"] = {
	"filters": [
		 {
                        "fieldname":"project",
                        "label": ("Project"),
                        "fieldtype": "Link",
                        "options" : "Project"

                },

                {
                        "fieldname":"from_date",
                        "label": ("From Date"),
                        "fieldtype": "Date",

                },

                {
                        "fieldname":"to_date",
                        "label": ("To Date"),
                        "fieldtype": "Date",

                }


	]
}