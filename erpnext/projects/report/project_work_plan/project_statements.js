frappe.provide("erpnext.financial_statements");

erpnext.project_statements = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": frappe.defaults.get_user_default("fiscal_year"),
			"reqd": 1
		},
		{
			"fieldname": "periodicity",
			"label": __("Periodicity"),
			"fieldtype": "Select",
			"options": [
				{ "value": "Monthly", "label": __("Monthly") },
				{ "value": "Quarterly", "label": __("Quarterly") },
				{ "value": "Half-Yearly", "label": __("Half-Yearly") },
				{ "value": "Yearly", "label": __("Yearly") }
			],
			"default": "Monthly",
			"reqd": 1
		}
	],
	"formatter": function(value, row, column, data, default_formatter) {
		if (column.fieldname=="account") {
			value = data.account_name;

			column.link_onclick =
				"erpnext.financial_statements.open_general_ledger(" + JSON.stringify(data) + ")";
				column.is_tree = true;
		}

		value = default_formatter(row, cell, value, column, data);

		if (!data.parent_account) {
			var $value = $(value).css("font-weight", "bold");
			if (data.warn_if_negative && data[column.fieldname] < 0) {
				$value.addClass("text-danger");
			}

			value = $value.wrap("<p></p>").parent().html();
		}

		return value;
	},
	"open_documents": function(data) {
		console.log(data);
	},
	"tree": true,
	"name_field": "account",
	"parent_field": "parent_account",
	"initial_depth": 3,
	onload: function(report) {
		// dropdown for links to other financial statements
		report.page.add_inner_button(__("Financial Position"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Statement of Financial Position', {company: filters.company});
		}, 'Financial Statements');
		report.page.add_inner_button(__("Comprehensive Income"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Statement of Comprehensive Income', {company: filters.company});
		}, 'Financial Statements');
		report.page.add_inner_button(__("Cash Flow Statement"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Statement of Cash Flow', {company: filters.company});
		}, 'Financial Statements');
	}
};
