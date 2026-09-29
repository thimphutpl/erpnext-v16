// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
frappe.provide("erpnext.financial_statements");

// frappe.require("assets/erpnext/js/project_statements.js", function() {
frappe.query_reports["Project Work Plan"] = {
	"filters": [
		{
			"fieldname": 	"project",
			"label": 		("Project"),
			"fieldtype": 	"Link",
			"options":		"Project",
			"reqd": 1
		}
	],
	// "formatter": function(value, row, column, data, default_formatter) {
	// 	// if (column.fieldname=="item") {
	// 	// 	value = data.item_name;

	// 	// 	//console.log(dataContext)
	// 	// 	column.link_onclick =
	// 	// 		"erpnext.project_statements.open_documents(" + JSON.stringify(data) + ")";
			
	// 	// 		column.is_tree = true;
	// 	// }

	// 	value = default_formatter(row, cell, value, column, data);

	// 	if (!data.parent_item || data.item_name == "Time Sheets") {
	// 		//var $value = $(value).css("font-weight", "bold");
	// 		var $value = $(value).css({"font-weight": "bold", "color": "blue", "background-color": "#75ff3a"});

	// 		/*
	// 		if (dataContext.warn_if_negative && dataContext[columnDef.df.fieldname] < 0) {
	// 			$value.addClass("text-danger");
	// 		}
	// 		*/
	// 		console.log($value.wrap("<p></p>").parent().html())
	// 		value = $value.wrap("<p></p>").parent().html();
	// 	}
		
	// 	/*
	// 	if (dataContext.doctype == "Task"){
	// 		var $value = $(value).css({"color": "#bb0077"});
	// 		value = $value.wrap("<p></p>").parent().html();
	// 	}
	// 	*/
		
	// 	return value;
	// },
	// "tree": true,
	// "name_field": "item",
	// "parent_field": "parent_item",
	// "initial_depth": 0
}
// });
