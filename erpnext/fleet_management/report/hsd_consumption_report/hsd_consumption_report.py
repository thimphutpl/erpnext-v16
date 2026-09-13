# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.data import get_first_day, get_last_day, add_days
from frappe.utils import flt, getdate, formatdate, cstr
from erpnext.fleet_management.report.fleet_management_report import (
    get_km_till,
    get_hour_till,
    get_pol_till,
    get_pol_between,
    get_pol_consumed_till,
    get_ini_km_till,
    get_ini_hour_till
)


def execute(filters=None):
    columns = get_columns()
    query = construct_query(filters)
    data = get_data(query, filters)

    return columns, data


def get_data(query, filters=None):
    data = []
    datas = frappe.db.sql(query, as_dict=True)
    
    for d in datas:
        own_cc = 0
        if filters.own_cc:
            own_cc = 1

        # Fetch and handle None values gracefully
        d.drawn = flt(get_pol_between("Receive", d.name, filters.from_date, filters.to_date, d.hsd_type, own_cc))
        received_till = flt(get_pol_till("Receive", d.name, add_days(getdate(filters.from_date), -1), d.hsd_type))
        consumed_till = flt(get_pol_consumed_till(d.name, add_days(getdate(filters.from_date), -1), filter_dry=own_cc))
        consumed_till_end = flt(get_pol_consumed_till(d.name, filters.to_date, filter_dry=own_cc))
        
        # Calculations
        d.consumed = flt(consumed_till_end) - flt(consumed_till)
        d.opening = flt(received_till) - flt(consumed_till)
        # d.open_km = flt(get_km_till(d.name, add_days(getdate(filters.from_date), -1)))
        # d.open_hr = flt(get_hour_till(d.name, add_days(getdate(filters.from_date), -1)))
        d.open_km = flt(get_ini_km_till(d.name, getdate(filters.from_date)))
        d.open_hr = flt(get_ini_hour_till(d.name, getdate(filters.from_date)))
        d.close_km = flt(get_km_till(d.name, filters.to_date))
        d.close_hr = flt(get_hour_till(d.name, filters.to_date))
        
        # Fetch additional values with defaults
        d.cap = flt(frappe.db.get_value("Equipment", d.equipment, "tank_capacity"), 0.0)
        d.cap = flt(frappe.db.get_value("Equipment", d.equipment, "kph"), 0.0)
        d.cap = flt(frappe.db.get_value("Equipment", d.equipment, "lph"), 0.0)
        
        rate = frappe.db.sql("""
            SELECT (SUM(pol.qty * pol.rate) / SUM(pol.qty)) AS rate 
            FROM `tabPOL Receive` pol 
            WHERE pol.branch = %s AND pol.docstatus = 1 AND pol.pol_type = %s
        """, (d.branch, d.hsd_type))
        d.rate = rate and flt(rate[0][0]) or 0.0
        
        vl_records = frappe.db.sql("""
            SELECT place , hsd_amount
            FROM `tabVehicle Logbook` 
            WHERE equipment = %s AND docstatus = 1 
            ORDER BY to_date DESC LIMIT 1
        """, d.name, as_dict=1)
        d.place = vl_records and vl_records[0].get('place', "") or ""
        d.hsd_amount = vl_records and vl_records[0].get('hsd_amount', "") or ""
        
        ys_records = frappe.db.sql("""
            SELECT hci.yard_hours, hci.yard_distance 
            FROM `tabHire Charge Item` hci, `tabHire Charge Parameter` hcp 
            WHERE hcp.name = hci.parent 
            AND hcp.equipment_type = %s 
            AND hcp.equipment_model = %s 
            AND (%s BETWEEN from_date AND IFNULL(to_date, CURDATE()) OR %s BETWEEN from_date AND IFNULL(to_date, CURDATE()))
        """, (d.equipment_type, d.equipment_model, filters.from_date, filters.to_date), as_dict=1)
        d.yskm = ys_records and flt(ys_records[0].get('yard_distance'), 0.0) or 0.0
        d.yshour = ys_records and flt(ys_records[0].get('yard_hours'), 0.0) or 0.0

        # Calculate HSD Amount safely
        d.hsd_amount = flt(d.consumed) * flt(d.rate)
        
        # row = [
        #     d.name, d.equipment_category, d.equipment_type, d.registration_number, d.place,
        #     "{0}/{1}".format(d.open_km, d.open_hr), "{0}/{1}".format(d.close_km, d.close_hr),
        #     round(d.close_km - d.open_km, 2), round(d.close_hr - d.open_hr, 2),
        #     round(flt(d.drawn), 2), round(flt(d.opening), 2), round(flt(d.drawn + d.opening), 2),
        #     d.yskm, d.yshour, round(d.consumed, 2), round(flt(d.closing), 2),
        #     flt(d.cap), round(flt(d.rate), 2), round(flt(d.rate) * flt(d.consumed), 2),
        #     round(d.hsd_amount, 2),  # HSD Amount
        # ]
        consumed_lph = round(round(d.close_hr - d.open_hr, 2) * d.lph, 2)
        d.closing = flt(d.opening) + flt(d.drawn) - flt(d.consumed) - flt(consumed_lph)
        row = [
            d.name, d.branch, d.equipment_category, d.equipment_type, d.registration_number, d.place,
            "{0}/{1}".format(d.open_km, d.open_hr), 
            "{0}/{1}".format(d.close_km, d.close_hr),
            round(d.close_km - d.open_km, 2), 
            round(d.close_hr - d.open_hr, 2),
            round(flt(d.drawn), 2), 
            round(flt(d.opening), 2), 
            round(flt(d.drawn + d.opening), 2),
            d.kph, d.lph, 
            round(d.consumed, 2), 
            consumed_lph, 
            round(consumed_lph + round(d.consumed, 2), 2), 
            round(flt(d.closing), 2), 
            round(flt(d.rate), 2), 
            round(flt(d.rate) * flt(d.consumed), 2),
            round(d.hsd_amount, 2),  # HSD Amount
        ]
        data.append(row)
    return data




def construct_query(filters):
    query = """SELECT e.name, e.branch, e.equipment_category, e.hsd_type, e.lph, e.kph,
        e.registration_number, e.equipment_type, e.equipment_model 
        FROM `tabEquipment Operator Item` eh, `tabEquipment` e 
        WHERE eh.parent = e.name """
    if filters.get("branch"):
        query += f" AND e.branch = '{filters.branch}'"

    if filters.get("from_date") and filters.get("to_date"):
        query += f" AND ('{filters.to_date}' >= IFNULL(eh.from_date, CURDATE()) AND '{filters.from_date}' <= IFNULL(eh.to_date, CURDATE()))"

    if not filters.include_disabled:
        query += " AND e.disabled = 0"

    # if filters.not_cdcl:
    #     query += " AND e.not_cdcl = 0"

    query += " GROUP BY e.name, e.branch ORDER BY e.equipment_category, e.equipment_type ASC"
    return query


def get_columns():
    columns = [
        {
            "label": _("Equipment"),
            "fieldname": "equipment",
            "fieldtype": "Link",
            "options": "Equipment",
            "width": 120,
        },
         {
            "label": _("Branch"),
            "fieldname": "branch",
            "fieldtype": "Link",
            "options": "Branch",
            "width": 120,
        },
        {
            "label": _("Equipment Category"),
            "fieldname": "equipment_category",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Equipment Type"),
            "fieldname": "equipment_type",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Registration No"),
            "fieldname": "registration_number",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Location"),
            "fieldname": "location",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Initial KM/H"),
            "fieldname": "initial_km_hr",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Final KM/H"),
            "fieldname": "final_km_hr",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("KM"),
            "fieldname": "km",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Hour"),
            "fieldname": "hour",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("HSD Drawn (L)"),
            "fieldname": "hsd_drawn",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Prev Bal (L)"),
            "fieldname": "prev_bal",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Total HSD (L)"),
            "fieldname": "total_hsd",
            "fieldtype": "Data",
            "width": 100,
        },
        # {
        #     "label": _("Per KM"),
        #     "fieldname": "per_km",
        #     "fieldtype": "Data",
        #     "width": 110,
        # },
        # {
        #     "label": _("Per Hour"),
        #     "fieldname": "per_hour",
        #     "fieldtype": "Data",
        #     "width": 110,
        # },
        {
            "label": _("Per KM"),
            "fieldname": "kph",
            "fieldtype": "Data",
            "width": 110,
        },
        {
            "label": _("Per Hour"),
            "fieldname": "lph",
            "fieldtype": "Data",
            "width": 110,
        },
        {
            "label": _("HSD Consumption (Km)"),
            "fieldname": "hsd_consumption_km",
            "fieldtype": "Data",
            "width": 110,
        },
        {
            "label": _("HSD Consumption (Hr)"),
            "fieldname": "hsd_consumption_hr",
            "fieldtype": "Data",
            "width": 110,
        },
        {
            "label": _("HSD Consumption"),
            "fieldname": "hsd_consumption",
            "fieldtype": "Data",
            "width": 110,
        },
        {
            "label": _("Closing Bal (L)"),
            "fieldname": "closing_bal",
            "fieldtype": "Data",
            "width": 110,
        },
        {
            "label": _("Rate (Nu.)"),
            "fieldname": "rate",
            "fieldtype": "Currency",
            "width": 100,
        },
        {
            "label": _("Amount (Nu.)"),
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 100,
        },
        {
            "label": _("HSD Amount"),
            "fieldname": "hsd_amount",
            "fieldtype": "Data",
            "width": 120,
        },
    ]
    return columns


# @frappe.whitelist()
# def fetch_tank_balance_from_hsd(equipment):
#     if not equipment:
#         frappe.throw("Equipment is required to fetch Tank Balance.")

#     closing = frappe.db.get_value("HSD Consumption Report", {"equipment": equipment}, "closing")
    
#     if closing is None:
#         frappe.throw(f"No HSD Consumption Report entry found for the selected equipment: {equipment}")

#     return closing



