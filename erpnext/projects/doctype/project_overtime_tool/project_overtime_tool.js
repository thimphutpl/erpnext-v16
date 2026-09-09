// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Project Overtime Tool", {
// 	refresh(frm) {

// 	},
// });


// cur_frm.add_fetch("cost_center", "branch", "branch")
// cur_frm.add_fetch("project", "cost_center", "cost_center")
// cur_frm.add_fetch("project", "branch", "branch")

frappe.ui.form.on("Project Overtime Tool", {
	refresh: function(frm) {
		frm.disable_save();
	},
	
	onload: function(frm) {
		frm.set_value("date", get_today());
	},

	number_of_hours: function(frm) {
		erpnext.project_overtime_tool.load_employees(frm);
	},

	project: function(frm) {
		erpnext.project_overtime_tool.load_employees(frm);
		cur_frm.set_df_property("cost_center", "read_only", frm.doc.project ? 1 : 0) 
	},

	date: function(frm) {
		erpnext.project_overtime_tool.load_employees(frm);
	},

	employee_type: function(frm) {
		erpnext.project_overtime_tool.load_employees(frm);
	},

	cost_center: function(frm) {
		erpnext.project_overtime_tool.load_employees(frm);
	},

	branch: function(frm) {
		erpnext.project_overtime_tool.load_employees(frm);
	},
});


erpnext.project_overtime_tool = {
	load_employees: function(frm) {
		if(frm.doc.employee_type && frm.doc.cost_center && frm.doc.branch && frm.doc.date && frm.doc.number_of_hours) {
			frappe.call({
				method: "erpnext.projects.doctype.project_overtime_tool.project_overtime_tool.get_employees",
				args: {
					date: frm.doc.date,
					number_of_hours: frm.doc.number_of_hours,
					employee_type: frm.doc.employee_type,
					cost_center: frm.doc.cost_center,
					branch: frm.doc.branch
				},
				callback: function(r) {
					if(r.message['unmarked'].length > 0) {
						unhide_field('unmarked_attendance_section')
						if(!frm.employee_area) {
							frm.employee_area = $('<div>')
							.appendTo(frm.fields_dict.employees_html.wrapper);
						}
						frm.EmployeeSelector = new erpnext.EmployeeSelector(frm, frm.employee_area, r.message['unmarked'])
					}
					else{
						hide_field('unmarked_attendance_section')
					}

					if(r.message['marked'].length > 0) {
						unhide_field('marked_attendance_section')
						if(!frm.marked_employee_area) {
							frm.marked_employee_area = $('<div>')
								.appendTo(frm.fields_dict.marked_attendance_html.wrapper);
						}
						frm.marked_employee = new erpnext.MarkedEmployee(frm, frm.marked_employee_area, r.message['marked'])
					}
					else{
						hide_field('marked_attendance_section')
					}
				}
			});
		}
	}
}

erpnext.MarkedEmployee = Class.extend({
	init: function(frm, wrapper, employee) {
		this.wrapper = wrapper;
		this.frm = frm;
		this.make(frm, employee);
	},
	make: function(frm, employee) {
		var me = this;
		$(this.wrapper).empty();

		var row;
		$.each(employee, function(i, m) {
			var attendance_icon = "icon-check";
			var color_class = "";
			if(m.status == "Absent") {
				attendance_icon = "icon-check-empty"
				color_class = "text-muted";
			}

			if (i===0 || i % 4===0) {
				row = $('<div class="row"></div>').appendTo(me.wrapper);
			}

			$(repl('<div class="col-sm-3 %(color_class)s">\
				<label class="marked-employee-label"><span class="%(icon)s"></span>\
				%(employee)s (%(id)s)</label>\
				</div>', {
					employee: m.person_name,
					id: m.name,
					icon: attendance_icon,
					color_class: color_class
				})).appendTo(row);
		});
	}
});


erpnext.EmployeeSelector = Class.extend({
	init: function(frm, wrapper, employee) {
		this.wrapper = wrapper;
		this.frm = frm;
		this.make(frm, employee);
	},
	make: function(frm, employee) {
		var me = this;

		$(this.wrapper).empty();
		var employee_toolbar = $('<div class="col-sm-12 top-toolbar">\
			<button class="btn btn-default btn-add btn-xs"></button>\
			<button class="btn btn-xs btn-default btn-remove"></button>\
			</div>').appendTo($(this.wrapper));

		var mark_employee_toolbar = $('<div class="col-sm-12 bottom-toolbar">\
			<button class="btn btn-primary btn-mark-present btn-xs"></button>\
			<button class="btn btn-default btn-mark-absent btn-xs"></button></div>')

		employee_toolbar.find(".btn-add")
			.html(__('Check all'))
			.on("click", function() {
				$(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
					if(!$(check).is(":checked")) {
						check.checked = true;
					}
				});
			});

		employee_toolbar.find(".btn-remove")
			.html(__('Uncheck all'))
			.on("click", function() {
				$(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
					if($(check).is(":checked")) {
						check.checked = false;
					}
				});
			});

		mark_employee_toolbar.find(".btn-mark-present")
            .addClass('custom-allocate-overtime-btn')
			.html(__('Allocate Overtime'))
            .css("margin-top", "20px")

			.on("click", function() {
				var employee_present = [];
				$(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
					if($(check).is(":checked")) {
						employee_present.push(employee[i]);
					}
				});
				if(frm.doc.number_of_hours > 0) {
					frappe.call({
						method: "erpnext.projects.doctype.project_overtime_tool.project_overtime_tool.allocate_overtime",
						args:{
							"employee_list":employee_present,
							"date": frm.doc.date,
							"purpose": frm.doc.purpose,
							"number_of_hours": frm.doc.number_of_hours,
							"employee_type": frm.doc.employee_type,
							"cost_center": frm.doc.cost_center,
							"branch": frm.doc.branch
						},

						callback: function(r) {
							erpnext.project_overtime_tool.load_employees(frm);

						}
					});
				}
				else {frappe.msgprint("Number of Hours should be greater than 0")}
			});

		var row;
		$.each(employee, function(i, m) {
			if (i===0 || (i % 4) === 0) {
				row = $('<div class="row"></div>').appendTo(me.wrapper);
			}

			$(repl('<div class="col-sm-3 unmarked-employee-checkbox">\
				<div class="checkbox">\
				<label><input type="checkbox" class="employee-check" employee="%(employee)s"/>\
				%(employee)s (%(id)s)</label>\
				</div></div>', {employee: m.person_name, id:m.name})).appendTo(row);
		});

		mark_employee_toolbar.appendTo($(this.wrapper));
	}
});
