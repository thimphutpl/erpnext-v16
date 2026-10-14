// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Asset History"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			// default: frappe.defaults.get_user_default("year_start_date"),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			// default: frappe.defaults.get_user_default("year_end_date"),
		},
		{
			fieldname: "asset_code",
			label: __("Asset Code"),
			fieldtype: "Link",
			options: "Asset",
			reqd: 1
		},

	]
};
