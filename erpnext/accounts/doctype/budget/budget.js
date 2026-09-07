// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
//frappe.provide("erpnext.accounts.dimensions");

frappe.ui.form.on('Budget', {

    setup(frm) {
        frappe.db.get_single_value(
            "Budget Settings",
            "monthly_budget_check"
        ).then(value => {
            set_monthly_budget_fields(frm, cint(value) === 1);
        });
    },
	onload: function(frm) {
		frm.set_query("account", "accounts", function() {
			return {
				filters: {
					company: frm.doc.company,
					is_group: 0
				}
			};
		});
		
		frm.set_query("cost_center", function() {
			return {
				filters: {
					company: frm.doc.company,
					is_group: 0
				}
			};
		});

		frm.set_query("monthly_distribution", function() {
			return {
				filters: {
					fiscal_year: frm.doc.fiscal_year
				}
			};
		});
	
	},

	refresh: function(frm) {
		frm.trigger("toggle_reqd_fields")
		frm.get_field("accounts").grid.grid_pagination.page_length = 150
	},

	budget_against: function(frm) {
		frm.trigger("set_null_value")
		frm.trigger("toggle_reqd_fields")
	},

	set_null_value: function(frm) {
		if(frm.doc.budget_against == 'Cost Center') {
			frm.set_value('project', null)
		} else {
			frm.set_value('cost_center', null)
		}
	},
	get_accounts: function(frm) {
		if(frm.doc.cost_center || frm.doc.project){
			return frappe.call({
				method: "get_accounts",
				doc: frm.doc,
				callback: function(r, rt) {
					frm.refresh_field("accounts");
					frm.refresh_fields();
				},
				freeze: true,
				freeze_message: "Loading Expense Accounts..... Please Wait"
			});
		}else{
			frappe.throw("Either Cost Center or Project is missing. ")
		}
	},
	toggle_reqd_fields: function(frm) {
		frm.toggle_reqd("cost_center", frm.doc.budget_against=="Cost Center");
		frm.toggle_reqd("project", frm.doc.budget_against=="Project");
	}
});


frappe.ui.form.on("Budget Account", {	
	"january": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"february": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"march": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"april": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"may": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"june": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"july": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"august": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"september": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"october": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"november": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"december": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
}); 

function set_initial_budget(frm, cdt, cdn){
	frappe.call({
		method:"set_initial_budget",
		doc: frm.doc,
		callback: function(r) {
			frm.refresh_field('initial_budget');
			frm.refresh_field('budget_amount');
			frm.refresh_fields('accounts');
		}
	})
}

const monthly_fields = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december"
];

function set_monthly_budget_fields(frm, enabled) {
    const accounts = frm.fields_dict.accounts;

    if (!accounts || !accounts.grid) {
        return;
    }

    // January - December
    monthly_fields.forEach(fieldname => {
        accounts.grid.update_docfield_property(
            fieldname,
            "hidden",
            enabled ? 0 : 1
        );

        accounts.grid.update_docfield_property(
            fieldname,
            "reqd",
            enabled ? 1 : 0
        );
    });

    // budget_allocate - same child table
    accounts.grid.update_docfield_property(
        "budget_allocate",
        "hidden",
        enabled ? 1 : 0
    );

    accounts.grid.update_docfield_property(
        "budget_allocate",
        "reqd",
        enabled ? 0 : 1
    );

    // Refresh the same child table
    frm.refresh_field("accounts");
}