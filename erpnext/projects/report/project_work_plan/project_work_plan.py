# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe


from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	data    = get_data(filters)
	# frappe.throw(str(data))
	columns = get_columns()
	return columns, data

def get_data(filters):
        data   = []
        # Projects
        prj_list = frappe.db.sql("""
                        select
                                concat(name,'|',project_name) as item,
                                project_name as item_name,
                                null parent_item,
                                0 as indent,
                                expected_start_date as exp_start_date,
                                expected_end_date as exp_end_date,
                                tot_wq_percent as work_quantity,
                                tot_wq_percent_complete as work_quantity_complete,
                                'Project' doctype,
                                name docname
                        from `tabProject`
                        where name = "{0}"
                        order by creation desc
                """.format(filters.get("project")), as_dict=1)
        for prj in prj_list:
                indent = 0
                data.append(prj)

                indent += 1
                tasks = get_tasks(prj, indent)
                data += tasks

                additional_tasks = get_additional_tasks(prj, indent)
                data += additional_tasks
        # frappe.throw("here "+str(data))
        #frappe.msgprint(_("{0}").format(data))
        return data

def get_tasks(prj, indent):
        task_list = frappe.db.sql("""
                                select  concat(t.name,'|',t.subject) as item,
                                        t.subject as item_name,
                                        '{1}' as parent_item,
                                        ifnull(is_group,0) is_group,
                                        {2} as indent,
                                        exp_start_date,
                                        exp_end_date,
                                        work_quantity,
                                        work_quantity_complete,
                                        t.target_uom,
                                        t.target_quantity,
                                        t.target_quantity_complete,
                                        'Task' doctype,
                                        t.name docname
                                from `tabTask` t, (SELECT @rowid:=0) as init
                                where t.project = "{0}"
                                and   t.additional_task = 0
                                order by t.task_idx
                        """.format(prj.docname, prj.item, indent), as_dict=1)
        
        return task_list
        
def get_additional_tasks(prj, indent):
        task_list = frappe.db.sql("""
                                select  concat(t.name,'|',t.subject) as item,
                                        t.subject as item_name,
                                        '{1}' as parent_item,
                                        ifnull(is_group,0) is_group,
                                        {2} as indent,
                                        exp_start_date,
                                        exp_end_date,
                                        work_quantity,
                                        work_quantity_complete,
                                        t.target_uom,
                                        t.target_quantity,
                                        t.target_quantity_complete,
                                        'Task' doctype,
                                        t.name docname
                                from `tabTask` t, (SELECT @rowid:={2}) as init
                                where t.project = "{0}"
                                and   t.additional_task = 1
                                order by t.task_idx
                        """.format(prj.docname, prj.item, indent), as_dict=1)
        
        return task_list

        
def get_data_old(filters):
        data = []
        timesheet_name = 0
        
        # Projects
        prj_list = frappe.db.sql("""
                        select
                                concat(name,'|',project_name) as item,
                                project_name as item_name,
                                null parent_item,
                                0 as indent,
                                expected_start_date as exp_start_date,
                                expected_end_date as exp_end_date,
                                tot_wq_percent as work_quantity,
                                tot_wq_percent_complete as work_quantity_complete,
                                'Project' doctype,
                                name docname
                        from `tabProject`
                        where name = "{0}"
                        order by creation desc
                """.format(filters.get("project")), as_dict=1)

        # Tasks
        for prj in prj_list:
                #indent     = 0
                #prj.indent = indent
                data.append(prj)
                
                task_list = frappe.db.sql("""
                                select  concat(t.name,'|',t.subject) as item,
                                        t.subject as item_name,
                                        concat(p.name,'|',p.project_name) as parent_item,
                                        ifnull(is_group,0) is_group,
                                        1 as indent,
                                        exp_start_date,
                                        exp_end_date,
                                        work_quantity,
                                        work_quantity_complete,
                                        t.target_uom,
                                        t.target_quantity,
                                        t.target_quantity_complete,
                                        'Task' doctype,
                                        t.name docname
                                from `tabTask` t, `tabProject` p
                                where p.name = t.project
                                and   p.name = "{0}"
                                order by t.task_idx
                        """.format(prj.docname), as_dict=1)

                # Timesheets
                for task in task_list:
                        #if task.is_group == 1:
                        #        indent += 1
                        #        
                        #else:
                                
                        data.append(task)
                        timesheet_name += 1
                        
                        ts_list = frappe.db.sql("""
                                                select
                                                        concat(ts.name,'|',td.description) as item,
                                                        td.description as item_name,
                                                        {0} as parent_item,
                                                        3 as indent,
                                                        td.from_date as exp_start_date,
                                                        td.to_date as exp_end_date,
                                                        ts.work_quantity*(td.target_quantity_complete/ts.target_quantity) as work_quantity_complete,
                                                        td.target_quantity_complete,
                                                        'Timesheet' as doctype,
                                                        ts.name as docname
                                                from `tabTimesheet Detail` as td, `tabTimesheet` as ts
                                                where ts.task = '{1}'
                                                and ts.docstatus < 2
                                                and td.parent = ts.name
                                                order by td.from_date, td.to_date
                                        """.format(timesheet_name, task.docname), as_dict=1)

                        if ts_list:
                                ts_heading = frappe.db.sql("""
                                                        select
                                                                {0} as item,
                                                                'Time Sheets' as item_name,
                                                                '{1}' as parent_item,
                                                                2 as indent,
                                                                null as exp_start_date,
                                                                null as exp_end_date,
                                                                {2} as work_quantity_complete
                                                """.format(timesheet_name, task.item, task.work_quantity_complete), as_dict=1)[0]
                                #data.append({"item": "Time Sheets", "parent_item": lvl1.item, "item_name": "Time Sheets", "indent": 2})
                                data.append(ts_heading)
                                
                                for ts in ts_list:
                                        data.append(ts)
        frappe.throw(str(data))
        return data

def get_columns():
        return [
                {
                        "fieldname": "item",
                        "label": _("Item"),
                        "fieldtype": "Link",
                        "options": "Project",
                        "width": 300
                },
                {
                        "fieldname": "exp_start_date",
                        "label": _("Start Date"),
                        "fieldtype": "Date"
                },
                {
                        "fieldname": "exp_end_date",
                        "label": _("End Date"),
                        "fieldtype": "Date"
                },
                {
                        "fieldname": "work_quantity",
                        "label": _("WQ(%)"),
                        "fieldtype": "Percent",
                },
                {
                        "fieldname": "work_quantity_complete",
                        "label": _("WQ(%) Complete"),
                        "fieldtype": "Percent",
                },
                {
                        "fieldname": "target_uom",
                        "label": _("UOM"),
                        "fieldtype": "Link",
                        "options": "UOM"
                },
                {
                        "fieldname": "target_quantity",
                        "label": _("Target"),
                        "fieldtype": "Float"
                },
                {
                        "fieldname": "target_quantity_complete",
                        "label": _("Achievement"),
                        "fieldtype": "Float"
                },
        ]