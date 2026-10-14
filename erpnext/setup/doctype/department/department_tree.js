frappe.treeview_settings["Department"] = {
    ignore_fields: ["parent_department"],

    get_tree_nodes:
        "erpnext.setup.doctype.department.department.get_children",

    add_tree_node:
        "erpnext.setup.doctype.department.department.add_node",

    filters: [
        {
            fieldname: "company",
            fieldtype: "Link",
            options: "Company",
            label: __("Company"),
            default: erpnext.utils.get_tree_default("company"),
        },
    ],

    breadcrumb: "HR",
    root_label: "All Departments",
    get_tree_root: true,

    menu_items: [
        {
            label: __("New Department"),
            action: function () {
                frappe.new_doc("Department");
            },
            condition:
                'frappe.boot.user.can_create.indexOf("Department") !== -1',
        },
    ],

    onload: function (treeview) {
        treeview.make_tree();
    },

    onrender: function(node) {
		if (!node.data || !node.data.value) {
			return;
		}
	
		// Skip root node if it represents a Company
		if (
			node.data.value === "All Departments" ||
			node.data.value === "All Department" ||
			node.data.value === frappe.defaults.get_user_default("Company")
		) {
			return;
		}
	
		get_identifier(node);
	},
};


function get_identifier(node) {

    if (!node.data || !node.data.value || !node.$tree_link) {
        return;
    }

    frappe.call({
        method:
            "erpnext.setup.doctype.department.department.get_employee_count",

        args: {
            department: node.data.value,
        },

        callback: function (r) {

            if (!r.message) {
                return;
            }

            const data = r.message;

            // Remove existing badges before inserting new ones
            node.$tree_link
                .siblings(".department-info-badges")
                .remove();

            let badges = $('<span class="department-info-badges"></span>');

            if (data.approver_designation) {
                $('<span class="badge badge-light"></span>')
                    .text(data.approver_designation)
                    .css({
                        "font-size": "xx-small",
                        "margin-left": "5px",
                        "border-right": "1px solid grey",
                        "border-radius": "3px 0px 0px 3px",
                        "background-color": "#f68446",
                    })
                    .appendTo(badges);
            }

            if (data.approver_name) {
                $('<span class="badge badge-light"></span>')
                    .text(data.approver_name)
                    .css({
                        "font-size": "xx-small",
                        "border-right": "1px solid grey",
                        "border-radius": "3px",
                        "background-color": "#e5c9f7",
                    })
                    .appendTo(badges);
            }

            $('<span class="badge badge-light"></span>')
                .text(data.count ?? 0)
                .css({
                    "font-size": "xx-small",
                    "border-radius": "3px",
                    "background-color": "gold",
                })
                .appendTo(badges);

            node.$tree_link.after(badges);
        },
    });
}