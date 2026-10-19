frappe.provide("frappe.ui.form");

frappe.ui.form.BranchQuickEntryForm = class BranchQuickEntryForm extends frappe.ui.form.QuickEntryForm {
	render_dialog() {
		super.render_dialog();

		this.fields_dict.cost_center.get_query = () => {
			return {
				filters: {
					company: this.get_value("company"),
				},
			};
		};
	}
};
