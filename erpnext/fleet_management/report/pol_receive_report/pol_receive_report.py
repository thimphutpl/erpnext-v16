# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)

    return columns, data

def get_columns(filters):
    if not filters.get("own_cc"):
        columns = [
            {
                "label": ("Equipment"),
                "fieldname": "equipment",
                "fieldtype": "Link",
                "options": "Equipment",
                "width": 120,
            },
            {
                "label": ("Fuelbook"),
                "fieldname": "fuelbook",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "label": ("Supplier"),
                "fieldname": "supplier",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "label": ("Item Code"),
                "fieldname": "pol_type",
                "fieldtype": "Data",
                "width": 100,
            },
            {
                "label": ("Item Name"),
                "fieldname": "item_name",
                "fieldtype": "Data",
                "width": 170,
            },
            {
                "label": ("Date"),
                "fieldname": "posting_date",
                "fieldtype": "Date",
                "width": 120,
            },
            {
                "label": ("Quantity"),
                "fieldname": "qty",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "label": ("Rate"),
                "fieldname": "rate",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "label": ("Amount"),
                "fieldname": "amount",
                "fieldtype": "Currency",
                "width": 120,
            },
        ]
    else:
        columns = [
            {
                "label": ("Equipment"),
                "fieldname": "equipment",
                "fieldtype": "Link",
                "options": "Equipment",
                "width": 120,
            },
            {
                "label": ("Supplier"),
                "fieldname": "supplier",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "label": ("Item Code"),
                "fieldname": "pol_type",
                "fieldtype": "Link",
                "options": "Item",
                "width": 100,
            },
            {
                "label": ("Item Name"),
                "fieldname": "item_name",
                "fieldtype": "Data",
                "width": 170,
            },
            {
                "label": ("Date"),
                "fieldname": "posting_date",
                "fieldtype": "Date",
                "width": 120,
            },
            {
                "label": ("Quantity"),
                "fieldname": "qty",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "label": ("Rate"),
                "fieldname": "rate",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "label": ("Amount"),
                "fieldname": "amount",
                "fieldtype": "Currency",
                "width": 120,
            },
        ]
    return columns

def get_data(filters):
    query = """
        SELECT 
            p.equipment, p.fuelbook, 
            p.supplier, p.item_name, p.posting_date,
            pr.qty, pr.rate, IFNULL(pr.amount, 0) AS amount
        FROM `tabPOL Receive` AS p, `tabPOL Receive Item` AS pr
        WHERE p.docstatus = 1
    """

    conditions = []

    if filters.get("branch"):
        conditions.append("p.branch = %(branch)s")

    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("p.posting_date BETWEEN %(from_date)s AND %(to_date)s")

    if filters.get("direct"):
        conditions.append("p.direct_consumption = 1")

    if filters.get("own_cc"):
        conditions.append("p.fuelbook_branch = p.equipment_branch")

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += " ORDER BY p.equipment"

    return frappe.db.sql(query, filters, as_dict=True)