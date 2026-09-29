# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	data    = get_data(filters)
	columns = get_columns()
	return columns, data


# def get_columns(filters):
# 	cols = [
# 		("ID")                  + ":Link/Project:80",
# 		("Project")             + ":Data:250",
# 		("Employee Name")       + ":Data:120",
# 		("Gender")   			+ ":Data:120",
		  
# 	]
# 	return cols

# def get_data(filters):
# 	cond  = get_conditions(filters)
# 	query = """
# 			select distinct
# 						p.name          as project_id,
# 						p.project_name  as project_name,
# 						p.branch        as branch,
# 						p.cost_center   as cost_center,
# 						wh.parenttype   as employee_type,
# 						wh.parent       as employee,
# 						wh.from_date    as from_date,
# 						ifnull(wh.to_date, "Current Cost Center")     as to_date,
# 						e.employee_name as employee_name,
# 						e.gender        as gender,
# 						e.designation   as designation,
# 						e.status        as status,
# 						'Project'       as doctype,
# 						p.name          as docname
# 				from `tabProject` as p,
# 						`tabEmployee Internal Work History` as wh
# 				left join `tabEmployee` as e
# 				on e.employee = wh.parent
# 				where p.name    = "{0}"
# 				and   wh.branch = p.branch
# 				and wh.to_date is Null
# 				order by project_id, employee_type, employee 
				
# 		""".format(cond)    
	

	
def get_data(filters):
	cond = []
	data = []
	result = frappe.db.sql("""
				select distinct
						p.name          as project_id,
						p.project_name  as project_name,
						p.branch        as branch,
						p.cost_center   as cost_center,
						wh.parenttype   as employee_type,
						wh.parent       as employee,
						wh.from_date    as from_date,
						ifnull(wh.to_date, "Current Cost Center")     as to_date,
						e.employee_name as employee_name,
						e.gender        as gender,
						e.designation   as designation,
						e.status        as status,
						'Project'       as doctype,
						p.name          as docname
				from `tabProject` as p,
						`tabEmployee Internal Work History` as wh
				left join `tabEmployee` as e
				on e.employee = wh.parent
				where wh.branch = p.branch
				and wh.to_date is Null
				order by project_id, employee_type, employee 
			""".format(cond), as_dict=1)
						#.format(filters.get("project")), as_dict=1)

	for i in result:
		if i.employee_type.lower() in ('gep employee','muster roll employee'):
			other = frappe.db.sql("""
					select
						person_name,
						gender,
						designation,
						status
					from `tab{0}`
					where name = '{1}'
			""".format(i.employee_type, i.employee), as_dict=1)[0]

			if other:
				i["employee_name"] = other.person_name
				i["status"] = other.status
				i["gender"] = other.gender
				i["designation"] = other.designation
				
		data.append(i)
	return data




def get_columns():
	return [
		{
			"fieldname": "project_id",
			"label": _("Project"),
			"fieldtype": "Link",
			"options": "Project",
			"width": 300
		},
		{
			"fieldname": "employee",
			"label": _("Employee ID"),
			"width": 100
		},
		{
			"fieldname": "employee_name",
			"label": _("Employee Name"),
			"width": 150
		},
		{
			"fieldname": "gender",
			"label": _("Gender"),
			"width": 80
		},
		

		{
			"fieldname": "designation",
			"label": _("Designation"),
			"width": 150
		},
		{
			"fieldname": "employee_type",
			"label": _("Type"),
			"width": 100
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"width": 80
		},
		{
			"fieldname": "branch",
			"label": _("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"width": 100
		},
		{
			"fieldname": "cost_center",
			"label": _("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 100
		},
		{
			"fieldname": "from_date",
			"label": _("From Date"),
			"width": 100
		},
		{
			"fieldname": "to_date",
			"label": _("To Date"),
			"width": 100
		},
	]

def get_conditions(filters):
	cond = []

	if filters.get("project"):
		cond.append('name = "{0}"'.format(filters.get("project")))

	else:
		query = ""

	return query