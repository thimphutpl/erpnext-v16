// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["POL Ledger"] = {
	"filters": [
		{	
			"fieldname": "branch",
			"label": ("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"width": "100",
			"reqd":1
		},
		{	
			"fieldname": "equipment",
			"label": ("Equipment"),
			"fieldtype": "Link",
			"options": "Equipment",
			"width": "100",
		},
		{
			"fieldname":"from_date",
			"label": ("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd":1
		},
		{
			"fieldname":"to_date",
			"label": ("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd":1
		},
		{
			"fieldname":"tank_balance",
			"label" : ("Own Tank Balance of All Equipments"),
			"fieldtype": "Check",
			"default": 0
		}
	],
	
	"formatter": function (value, row, column, data, default_formatter) {
		// Ensure the default_formatter is callable
		if (typeof default_formatter === "function") {
			value = default_formatter(value, row, column, data);
		} else {
			console.warn("default_formatter is not a function or undefined.");
			value = value || ""; // Fallback to default value
		}

		// Custom logic for specific columns
		if (column.fieldname === "transaction_no") {
			console.log("Transaction No:", value);
		}
		if (column.fieldname === "reference") {
			console.log("Reference:", value);
		}

		// Additional formatting (example for styling values)
		if (value === "X") {
			value = `<div style="color: white; background-color: red; padding: 5px;">${value}</div>`;
		}

		return value;
	},
		
}

