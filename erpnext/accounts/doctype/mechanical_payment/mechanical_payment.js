// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// cur_frm.add_fetch("branch", "revenue_bank_account", "income_account")

frappe.ui.form.on('Mechanical Payment', {
    taxes_and_charges: function (frm) {
        if (frm.doc.taxes_and_charges) {
            get_gst_account_from_template(frm);
        }
        // calculate_gst_amount(frm);
    },
    // receivable_amount: function (frm) {
    //     calculate_gst_amount(frm);
    // },
    apply_gst: function (frm) {
        // Only calculate if checkbox is checked
        if (frm.doc.apply_gst) {
            calculate_gst_amount(frm);
        } else {
            // Reset GST if unchecked
            frm.set_value('gst_amount', 0);
            frm.set_value('total_gst_amount', 0);
        }
    },



    refresh: function (frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Accounting Ledger'), function () {
                frappe.route_options = {
                    voucher_no: frm.doc.name,
                    from_date: frm.doc.posting_date,
                    to_date: frm.doc.posting_date,
                    company: frm.doc.company,
                    group_by_voucher: false
                };
                frappe.set_route("query-report", "General Ledger");
            }, __("View"));
        }
        // frm.set_df_property('gst_details_section', 'hidden', 1);
        frm.set_df_property('get_transactions_with_gst', 'hidden', 0);
        frm.set_df_property('get_transactions_without_gst', 'hidden', 0);
    },


    "tds_amount": function (frm) {
        calculate_totals(frm);
        frm.toggle_reqd("tds_account", frm.doc.tds_amount);
    },

    get_series: function (frm) {
        frappe.call({
            method: "get_series",
            doc: frm.doc,
            callback: function (r) {
                frm.reload_doc();
            }
        });
    },

    get_transactions_with_gst: function (frm) {
        // frm.set_df_property('gst_details_section', 'hidden', 1);
        frm.refresh_fields();
        frappe.call({
            method: "get_transactions_with_gst",
            doc: frm.doc,
            callback: function (r) {
                frm.refresh_field("items");
                frm.refresh_fields();
            },
            freeze: true,
            freeze_message: "Fetching Transactions... Please Wait"
        });
    },
    get_transactions_without_gst: function (frm) {
        frm.set_df_property('gst_details_section', 'hidden', 0);
        frm.refresh_fields();
        frappe.call({
            method: "get_transactions_without_gst",
            doc: frm.doc,
            callback: function (r) {
                frm.refresh_field("items");
                frm.refresh_fields();
            },
            freeze: true,
            freeze_message: "Fetching Transactions... Please Wait"
        });
    },


    "receivable_amount": function (frm) {
        if (frm.doc.receivable_amount > frm.doc.actual_amount) {
            frm.set_value("receivable_amount", frm.doc.actual_amount);
            frappe.msgprint("Receivable Amount cannot be greater than the Total Payable Amount");
        } else {
            calculate_totals(frm);
            let total = frm.doc.receivable_amount;
            frm.doc.items.forEach(function (d) {
                let allocated = 0;
                if (total > 0 && total >= d.outstanding_amount) {
                    allocated = d.outstanding_amount;
                } else if (total > 0 && total < d.outstanding_amount) {
                    allocated = total;
                } else {
                    allocated = 0;
                }
                d.allocated_amount = allocated;
                total -= allocated;
            });
            frm.refresh_field("items");
        }
    },

    "items_on_form_rendered": function (frm, grid_row, cdt, cdn) {
        let row = frm.open_grid_row();
        row.grid_form.fields_dict.reference_type.set_value(frm.doc.payment_for);
        row.grid_form.fields_dict.reference_type.refresh();
    }
});

function calculate_gst_amount(frm) {
    if (!frm.doc.apply_gst) {
        frm.set_value('gst_amount', 0);
        frm.set_value('total_gst_amount', 0);
        return;
    }

    let receivable_amount = frm.doc.receivable_amount || 0;
    if (receivable_amount <= 0) {
        frm.set_value('gst_amount', 0);
        frm.set_value('total_gst_amount', 0);
        return;
    }

    let gst_rate = frm.doc.tax_rate || 0; // from taxes template
    let gst_amount = receivable_amount * gst_rate / 100;
    let total_gst_amount = receivable_amount + gst_amount;

    frm.set_value('gst_amount', gst_amount);
    frm.set_value('total_gst_amount', total_gst_amount);
}


function calculate_totals(frm) {
    if (frm.doc.receivable_amount) {
        frm.set_value("net_amount", flt(frm.doc.receivable_amount) - flt(frm.doc.tds_amount));
        frm.refresh_field("net_amount");
    }
}

function get_gst_account_from_template(frm) {
    if (!frm.doc.taxes_and_charges) return;

    frappe.call({
        method: "erpnext.projects.doctype.project_invoice.project_invoice.get_taxes_for_template",
        args: { template_name: frm.doc.taxes_and_charges },
        callback: function (r) {
            if (r.message && r.message.length) {
                const tax = r.message[0];
                frm.set_value('account_head', tax.account_head);
                frm.set_value('tax_rate', flt(tax.rate));
            }
        }
    });
}



frappe.ui.form.on("Mechanical Payment Item", {
    "reference_name": function (frm, cdt, cdn) {
        let item = locals[cdt][cdn];
        let rec_amount = flt(frm.doc.receivable_amount);
        let act_amount = flt(frm.doc.actual_amount);
        if (item.reference_name) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: item.reference_type,
                    fieldname: ["outstanding_amount"],
                    filters: {
                        name: item.reference_name
                    }
                },
                callback: function (r) {
                    frappe.model.set_value(cdt, cdn, "outstanding_amount", r.message.outstanding_amount);
                    frappe.model.set_value(cdt, cdn, "allocated_amount", r.message.outstanding_amount);
                    frm.refresh_field("outstanding_amount");
                    frm.refresh_field("allocated_amount");

                    frm.set_value("actual_amount", act_amount + flt(r.message.outstanding_amount));
                    frm.refresh_field("actual_amount");
                    frm.set_value("receivable_amount", rec_amount + flt(r.message.outstanding_amount));
                    frm.refresh_field("receivable_amount");
                }
            });
        }
    },

    "before_items_remove": function (frm, cdt, cdn) {
        let doc = locals[cdt][cdn];
        let amount = flt(frm.doc.receivable_amount);
        let ac_amount = flt(frm.doc.actual_amount) - flt(doc.outstanding_amount);
        frm.set_value("actual_amount", ac_amount);
        frm.refresh_field("actual_amount");
        frm.trigger("receivable_amount");
    }
});


