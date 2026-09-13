# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, get_datetime
from erpnext.fleet_management.report.fleet_management_report import get_pol_till, get_pol_consumed_till
from operator import itemgetter

# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data

# def get_data(filters=None):
#     data = []
    
#     # SQL Query for POL Entry
#     pol_entry_query = """
#         SELECT 
#             name, posting_date, posting_time, branch, equipment, pol_type, qty, type, reference_type, reference_name 
#         FROM 
#             `tabPOL Entry` 
#         WHERE 
#             docstatus = 1
#             {date_filter}
#             {branch_filter}
#             {equipment_filter}
#         ORDER BY 
#             posting_date
#     """
    
#     # Filters
#     date_filter = " AND posting_date BETWEEN %(from_date)s AND %(to_date)s" if filters.get("from_date") and filters.get("to_date") else ""
#     branch_filter = " AND branch = %(branch)s" if filters.get("branch") else ""
#     equipment_filter = " AND equipment = %(equipment)s" if filters.get("equipment") else ""
    
#     # Apply filters
#     formatted_query = pol_entry_query.format(
#         date_filter=date_filter,
#         branch_filter=branch_filter,
#         equipment_filter=equipment_filter
#     )
    
#     # Fetch data
#     pol_entries = frappe.db.sql(formatted_query, filters, as_dict=True)
    
#     for entry in pol_entries:
#         item = frappe.db.get_value("Item", entry.pol_type, ["item_code", "item_name", "stock_uom"], as_dict=True)
#         if not item:
#             continue
        
#         branch = frappe.db.get_value(entry.reference_type, entry.reference_name, "branch")
#         direct_consumption = "Yes" if entry.reference_type == "POL Receive" and frappe.get_value(entry.reference_type, entry.reference_name, "direct_consumption") else "No"
#         received = get_pol_till("Receive", entry.equipment, entry.posting_date, entry.pol_type)
        
#         equipment = frappe.db.get_value(
#             "Equipment", 
#             {"name": entry.equipment}, 
#             ["name", "branch", "equipment_type", "registration_number"], 
#             as_dict=True
#         )
#         if not equipment:
#             continue
        
#         balance = 0
#         if equipment["equipment_type"] == "Tanker":
#             stock = get_pol_till("Stock", entry.equipment, entry.posting_date, entry.pol_type)
#             issued = get_pol_till("Issue", entry.equipment, entry.posting_date, entry.pol_type)
#             balance = flt(stock) - flt(issued)
        
#         consumed_till = get_pol_consumed_till(entry.equipment, entry.posting_date, entry.posting_time)
#         fuel_balance = flt(received) - flt(consumed_till)
        
#         row = [
#             get_datetime(f"{entry.posting_date} {entry.posting_time}"),
#             entry.branch,
#             entry.equipment,
#             equipment["registration_number"],
#             item["item_name"],
#             entry.qty,
#             entry.reference_type,
#             entry.reference_name,
#             fuel_balance,
#             balance,
#             entry.type,
#             branch,
#             direct_consumption,
#         ]
#         data.append(row)
    
#     # Sorting data
#     data = sorted(data, key=itemgetter(0))
#     return data

# def get_columns():
#     return [
#         {"fieldname": "date_time", "label": "Date & Time", "fieldtype": "Datetime", "width": 140},
#         {"fieldname": "branch", "label": "Branch", "fieldtype": "Data", "width": 120},
#         {"fieldname": "equipment", "label": "Equipment", "fieldtype": "Link", "options": "Equipment", "width": 100},
#         {"fieldname": "equipment_no", "label": "Equipment No.", "fieldtype": "Data", "width": 100},
#         {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Link", "options": "Item", "width": 130},
#         {"fieldname": "qty", "label": "Qty", "fieldtype": "Float", "width": 80},
#         {"fieldname": "reference", "label": "Reference", "fieldtype": "Data", "width": 100},
#         {"fieldname": "transaction_no", "label": "Transaction No.", "fieldtype": "Dynamic Link", "options": "reference", "width": 120},
#         {"fieldname": "fuel_tank_balance", "label": "Fuel Tank Balance", "fieldtype": "Float", "width": 100},
#         {"fieldname": "tank_balance", "label": "Tanker Balance", "fieldtype": "Float", "width": 100},
#         {"fieldname": "purpose", "label": "Purpose", "fieldtype": "Data", "width": 90},
#         {"fieldname": "transaction_branch", "label": "Transaction Branch", "fieldtype": "Data", "width": 130},
#         {"fieldname": "direct_consumption", "label": "Direct Consumption", "fieldtype": "Data", "width": 50},
#     ]





def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = [
        {"fieldname": "date_time", "label": "Date & Time", "fieldtype": "Datetime", "width": 140},
        {"fieldname": "branch", "label": "Branch", "fieldtype": "Data", "width": 120},
        {"fieldname": "equipment", "label": "Equipment", "fieldtype": "Link", "options": "Equipment", "width": 100},
        {"fieldname": "equipment_no", "label": "Equipment No.", "fieldtype": "Data", "width": 100},
        {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Link", "options": "Item", "width": 130},
        {"fieldname": "qty", "label": "Qty", "fieldtype": "Float", "width": 80},
        {"fieldname": "reference", "label": "Reference", "fieldtype": "Data", "width": 100},
        {"fieldname": "transaction_no", "label": "Transaction No.", "fieldtype": "Dynamic Link", "options": "reference", "width": 120},
        {"fieldname": "purpose", "label": "Purpose", "fieldtype": "Data", "width": 90},
        {"fieldname": "transaction_branch", "label": "Transaction Branch", "fieldtype": "Data", "width": 130},
        {"fieldname": "direct_consumption", "label": "Direct Consumption", "fieldtype": "Data", "width": 50},
    ]

    # Dynamically include either tank_balance or fuel_tank_balance based on the filter
    if filters.get("tank_balance"):
        columns.append({"fieldname": "tank_balance", "label": "Tanker Balance", "fieldtype": "Float", "width": 100})
    else:
        columns.append({"fieldname": "fuel_tank_balance", "label": "Fuel Tank Balance", "fieldtype": "Float", "width": 100})

    return columns

def get_data(filters=None):
    data = []

    # SQL Query for POL Entry
    pol_entry_query = """
        SELECT 
            name, posting_date, posting_time, branch, equipment, pol_type, qty, type, reference_type, reference_name 
        FROM 
            `tabPOL Entry` 
        WHERE 
            docstatus = 1
            {date_filter}
            {branch_filter}
            {equipment_filter}
        ORDER BY 
            posting_date
    """
    # Filters
    date_filter = " AND posting_date BETWEEN %(from_date)s AND %(to_date)s" if filters.get("from_date") and filters.get("to_date") else ""
    branch_filter = " AND branch = %(branch)s" if filters.get("branch") else ""
    equipment_filter = " AND equipment = %(equipment)s" if filters.get("equipment") else ""

    # Apply filters
    formatted_query = pol_entry_query.format(
        date_filter=date_filter,
        branch_filter=branch_filter,
        equipment_filter=equipment_filter
    )
    # Fetch data
    pol_entries = frappe.db.sql(formatted_query, filters, as_dict=True)
    for entry in pol_entries:
        item = frappe.db.get_value("Item", entry.pol_type, ["item_code", "item_name", "stock_uom"], as_dict=True)
        if not item:
            continue
        branch = frappe.db.get_value(entry.reference_type, entry.reference_name, "branch")
        direct_consumption = "Yes" if entry.reference_type == "POL Receive" and frappe.get_value(entry.reference_type, entry.reference_name, "direct_consumption") else "No"
        received = get_pol_till("Receive", entry.equipment, entry.posting_date, entry.pol_type)
        equipment = frappe.db.get_value(
            "Equipment", 
            {"name": entry.equipment}, 
            ["name", "branch", "equipment_type", "registration_number"], 
            as_dict=True
        )
        if not equipment:
            continue
        balance = 0
        if equipment["equipment_type"] == "Tanker":
            stock = get_pol_till("Stock", entry.equipment, entry.posting_date, entry.pol_type)
            issued = get_pol_till("Issue", entry.equipment, entry.posting_date, entry.pol_type)
            balance = flt(stock) - flt(issued)
        consumed_till = get_pol_consumed_till(entry.equipment, entry.posting_date, entry.posting_time)
        fuel_balance = flt(received) - flt(consumed_till)

        # Include data conditionally based on tank_balance filter
        if filters.get("tank_balance"):
            row = [
                get_datetime(f"{entry.posting_date} {entry.posting_time}"),
                entry.branch,
                entry.equipment,
                equipment["registration_number"],
                item["item_name"],
                entry.qty,
                entry.reference_type,
                entry.reference_name,
                entry.type,
                branch,
                direct_consumption,
                balance,  # Tanker Balance
            ]
        else:
            row = [
                get_datetime(f"{entry.posting_date} {entry.posting_time}"),
                entry.branch,
                entry.equipment,
                equipment["registration_number"],
                item["item_name"],
                entry.qty,
                entry.reference_type,
                entry.reference_name,
                entry.type,
                branch,
                direct_consumption,
                fuel_balance,  # Fuel Tank Balance
            ]

        data.append(row)
    # Sorting data
    data = sorted(data, key=itemgetter(0))
    return data

