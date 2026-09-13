# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe


from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr
from erpnext.fleet_management.report.hsd_consumption_report.fleet_management_report import get_pol_till, get_pol_tills, get_pol_consumed_till

def execute(filters=None):
	columns = get_columns(filters);
	data = get_data(filters);

	return columns, data

def get_data(filters=None):
	data = []
	query = "select e.name, e.branch, e.registration_number, e.equipment_type from tabEquipment e, `tabEquipment Type`et where e.equipment_type = et.name"
	if not filters.all_equipment:
		query += " and et.is_container = 1"
	if filters.branch:
		query += " and e.branch = \'" + str(filters.branch) + "\'"
		
	items = frappe.db.sql("select item_code, item_name, stock_uom from tabItem where is_pol_item = 1 and disabled = 0", as_dict=True)

	query += " order by e.branch"

	for eq in frappe.db.sql(query, as_dict=True):
		for item in items:
			received = issued = 0
			if filters.all_equipment:
				if eq.hsd_type == item.item_code:
					received = get_pol_tills("Receive", eq.name, filters.to_date, item.item_code)
					issued = get_pol_consumed_till(eq.name, filters.to_date)
			else:
				frappe.throw("jjjjj")
				received = get_pol_tills("Stock", eq.name, filters.to_date, item.item_code)
				issued = get_pol_tills("Issue", eq.name, filters.to_date, item.item_code)

			if received or issued:
				row = [eq.name, eq.registration_number, eq.equipment_type, eq.branch, item.item_code, item.item_name, item.stock_uom, received, issued, flt(received) - flt(issued)]
				data.append(row)
	return data

def get_columns(filters):
	cols = [
		{
			"fieldname": "equipment",
			"label": _("Equipment"),
			"fieldtype": "Link",
			"options": "Equipment",
			"width": 100
		},
		{
			"fieldname": "eq_name",
			"label": _("Equipment Name"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "eq_cat",
			"label": _("Equipment Type"),
			"fieldtype": "Data",
			"width": 130
        },
		{
			"fieldname": "branch",
			"label": _("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"width": 200
        },
		{
			"fieldname": "pol_type",
			"label": _("Item Code"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "pol_name",
			"label": _("Item Name"),
			"fieldtype": "Data",
			"width": 170
        },
		{
			"fieldname": "uom",
			"label": _("UOM"),
			"fieldtype": "Link",
			"options": "UOM",
			"width": 60
        },
		{
			"fieldname": "received",
			"label": _("Received"),
			"fieldtype": "Float",
			"width": 100
        },
	]

	if filters.all_equipment:
		cols.append({
				"fieldname": "issued",
				"label": _("Consumed"),
				"fieldtype": "Float",
				"width": 100
			})
	else:
		cols.append({
				"fieldname": "issued",
				"label": _("Issued"),
				"fieldtype": "Float",
				"width": 100
			})

	cols.append({
				"fieldname": "balance",
				"label": _("Balance"),
				"fieldtype": "Float",
				"width": 100
            })
	return cols