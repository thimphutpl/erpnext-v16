# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from erpnext.fleet_management.report.fleet_management_report import get_pol_between

def execute(filters=None):
        columns = get_columns()
        data = get_data(filters)

        return columns, data

# def get_columns():
#         return [
#                 ("Equipment ") + ":Link/Equipment:120",
#                 ("Equipment No.") + ":Data:120",
#                 ("Item Code") + ":Data:100",
#                 ("Item Name") + ":Data:170",
#                 ("UoM") + ":Link/Item:120",
#                 ("Quantity") + ":Float:120"
#         ]

def get_columns():
    columns = [
        {
            "label": ("Equipment"),
            "fieldname": "equipment",
            "fieldtype": "Link",
            "options": "Equipment",
            "width": 120,
        },
        {
            "label": ("Equipment No."),
            "fieldname": "registration_number",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": ("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Data",
            # "options": "Item",
            "width": 100,
        },
        {
            "label": ("Item Name"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 170,
        },
        {
            "label": ("Stock UoM"),
            "fieldname": "stock_uom",
            "fieldtype": "Link",
			"options": "Item",
            "width": 120,
        },
        {
            "label": ("Quantity"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 120,
        },
    ]
    return columns


def get_data(filters):
	data = []
	query =  "select name, registration_number FROM tabEquipment WHERE 1"

	if filters.get("branch"):
		query += " and branch = \'" + str(filters.branch) + "\'"

	items = frappe.db.sql("select item_code, item_name, stock_uom from tabItem where is_pol_item = 1", as_dict=True)

	for eq in frappe.db.sql(query, as_dict=True):
		for item in items:
			own_cc = 0
			if filters.get("own_cc"):
				own_cc = 1
			balance = get_pol_between("Issue", eq.name, filters.from_date, filters.to_date, item.item_code, own_cc)
			if balance:
				row = [eq.name, eq.registration_number, item.item_code, item.item_name, item.stock_uom, balance]
				data.append(row)
	return data
