// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt


// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Project Budget Monitoring"] = {
    filters: [
        {
            fieldname: "project_definition",
            label: "Project Definition",
            fieldtype: "Link",
            options: "Project Definition"
        },
        {
            fieldname: "branch",
            label: "Branch",
            fieldtype: "Link",
            options: "Branch"
        },
        {
            fieldname: "activity_code",
            label: "Project Activity",
            fieldtype: "Link",
			options: "Project"
        },
        {
            fieldname: "budget_status",
            label: "Budget Status",
            fieldtype: "Select",
            options: "\nWithin Budget\nNear Budget Limit\nOver Budget\nNo Budget"
        }
    ],

    formatter: function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (!data) {
            return value;
        }

        if (column.fieldname === "budget_status") {
            if (data.budget_status === "Within Budget") {
                value = `<span style="color:green; font-weight:bold;">${value}</span>`;
            } else if (data.budget_status === "Near Budget Limit") {
                value = `<span style="color:orange; font-weight:bold;">${value}</span>`;
            } else if (data.budget_status === "Over Budget") {
                value = `<span style="color:red; font-weight:bold;">${value}</span>`;
            } else if (data.budget_status === "No Budget") {
                value = `<span style="color:gray; font-weight:bold;">${value}</span>`;
            }
        }

        return value;
    }
};