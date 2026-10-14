# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr, rounded
from frappe.utils.data import get_first_day, get_last_day, add_years, date_diff, now, today, getdate

def execute(filters=None):
    # validate_filters(filters)
    data = get_data(filters)
    columns = get_columns()
    return columns, data

def validate_filters(filters):
    # if not filters.fiscal_year:
    #     frappe.throw(_("Fiscal Year {0} is required").format(filters.fiscal_year))

    # fiscal_year = frappe.db.get_value("Fiscal Year", filters.fiscal_year, ["year_start_date", "year_end_date"], as_dict=True)
    # if not fiscal_year:
    #     frappe.throw(_("Fiscal Year {0} does not exist").format(filters.fiscal_year))
    # else:
    #     filters.year_start_date = getdate(fiscal_year.year_start_date)
    #     filters.year_end_date = getdate(fiscal_year.year_end_date)
    
    from datetime import datetime

    filters.year_start_date = datetime.strptime(filters.fiscal_year + "-01-01", "%Y-%m-%d").date()
    filters.year_end_date = datetime.strptime(filters.fiscal_year + "-12-31", "%Y-%m-%d").date()


    if not filters.from_date:
        filters.from_date = filters.year_start_date

    if not filters.to_date:
        filters.to_date = filters.year_end_date

    filters.from_date = getdate(filters.from_date)
    filters.to_date = getdate(filters.to_date)

    if filters.from_date > filters.to_date:
        frappe.throw(_("From Date cannot be greater than To Date"))

    if (filters.from_date < filters.year_start_date) or (filters.from_date > filters.year_end_date):
        frappe.msgprint(_("From Date should be within the Fiscal Year. Assuming From Date = {0}")\
            .format(formatdate(filters.year_start_date)))

        filters.from_date = filters.year_start_date

    if (filters.to_date < filters.year_start_date) or (filters.to_date > filters.year_end_date):
        frappe.msgprint(_("To Date should be within the Fiscal Year. Assuming To Date = {0}")\
            .format(formatdate(filters.year_end_date)))
        filters.to_date = filters.year_end_date

    if filters.get('asset_category'):
        filters.asset_category = filters.get('asset_category')

    if filters.get('asset_code'):
        filters.asset_code = filters.get('asset_code')

def get_depreciation_details(filters):
    query= """
        SELECT
            ads.asset AS asset,
            SUM(CASE
                WHEN ds.schedule_date < '{from_date}' THEN ds.depreciation_amount
                ELSE 0
            END) AS dep_opening,
            SUM(CASE
                WHEN ds.schedule_date BETWEEN '{from_date}' AND '{to_date}' THEN ds.depreciation_amount
                ELSE 0
            END) AS dep_addition,
            SUM(CASE
                WHEN ds.schedule_date < '{from_date}' THEN ds.income_depreciation_amount
                ELSE 0
            END) AS opening_income,
            SUM(CASE
                WHEN ds.schedule_date BETWEEN '{from_date}' AND '{to_date}' THEN ds.income_depreciation_amount
                ELSE 0
            END) AS depreciation_income_tax
        FROM `tabDepreciation Schedule` as ds, `tabAsset Depreciation Schedule` ads
        WHERE ads.name=ds.parent AND ds.schedule_date <= '{to_date}'
        AND (IFNULL(ds.journal_entry,'') != '' )
        GROUP BY ds.parent
    """.format(from_date=filters.from_date, to_date=filters.to_date, fiscal_year = filters.fiscal_year)

    query_two= """
        SELECT
            ads.asset AS asset,
            SUM(ds.depreciation_amount) AS dep_total_next_year
        FROM `tabDepreciation Schedule` AS ds, `tabAsset Depreciation Schedule` ads
        WHERE ads.name=ds.parent AND YEAR(ds.schedule_date) = '{fiscal_year}' 
        AND (SELECT status FROM `tabAsset` WHERE name = ads.asset) IN ('Submitted','Partially Depreciated')
        GROUP BY ds.parent

    """.format(fiscal_year = str(int(filters.fiscal_year)+1))

    depreciation_details = frappe._dict()
    depreciation_details_two = frappe._dict()
    for row in frappe.db.sql(query, as_dict=True):
        depreciation_details.setdefault(row.asset, row)
    for row in frappe.db.sql(query_two, as_dict=True):
        depreciation_details_two.setdefault(row.asset, row)
    return depreciation_details, depreciation_details_two

def get_data(filters):
    query = """
            SELECT
            a.name, a.asset_name, a.asset_category, a.asset_sub_category, a.asset_issue_details
                FROM 
            `tabAsset` AS a
            LEFT JOIN `tabAsset Finance Book` AS f ON f.parent = a.name       
        WHERE a.docstatus = 1 
        AND (
            a.status not in ('Scrapped', 'Sold')
            OR
            (a.status in ('Scrapped', 'Sold'))
        )
        """.format(from_date=filters.from_date, to_date=filters.to_date)
                
    if filters.cost_center:
        query+=" and a.cost_center = \'" + filters.cost_center + "\'"

    if filters.asset_category:
        query+=" and a.asset_category = \'" + filters.asset_category + "\'"

    if filters.asset_code:
        query +=" and a.name = '{}'".format(filters.asset_code)
    if filters.status:
        query +=" and a.status = '{}'".format(filters.status)

    asset_data = frappe.db.sql(query, filters, as_dict=True)
    # depreciation_details, depreciation_details_two = get_depreciation_details(filters)
    data = []
    if asset_data:
        for a in asset_data:
            for ai in frappe.db.sql("""
                select name, issued_to, employee_name, cost_center, issued_date, qty from `tabAsset Issue Details` where name = '{}'
            """.format(a.asset_issue_details),as_dict=1):
                ai_row = {
                    "asset_code": a.name,
                    "asset_name": a.asset_name,
                    "serial_number": a.serial_number,
                    "asset_category": a.asset_category,
                    "asset_sub_category": a.asset_sub_category,
                    "reference_type": "Asset Issue Details",
                    "reference_name": ai.name,
                    "issued_to": ai.issued_to,
                    "employee_name": ai.employee_name,
                    "designation": frappe.db.get_value("Employee", ai.issued_to, "designation"),
                    "cost_center": ai.cost_center,
                    "date_of_issue": ai.issued_date,
                    "status": a.status,
                    "project": a.project,
                    "remarks": a.remarks,
                }
                data.append(ai_row)
            for am in frappe.db.sql("""
                select am.name, am.transaction_date, ami.to_employee, ami.target_location from `tabAsset Movement` am, `tabAsset Movement Item` ami
				where ami.parent = am.name and ami.from_employee != ami.to_employee and ami.asset = '{}' order by am.transaction_date asc
            """.format(a.name), as_dict=1):
                row = {
                    "asset_code": a.name,
                    "asset_name": a.asset_name,
                    "serial_number": a.serial_number,
                    "asset_category": a.asset_category,
                    "asset_sub_category": a.asset_sub_category,
                    "reference_type": "Asset Movement",
                    "reference_name": am.name,
                    "issued_to": am.to_employee,
                    "employee_name": frappe.db.get_value("Employee", am.to_employee, "employee_name"),
                    "designation": frappe.db.get_value("Employee", am.to_employee, "designation"),
                    "target_location": am.target_location,
                    "date_of_issue": am.transaction_date,
                    "status": a.status,
                    "project": a.project,
                    "remarks": a.remarks,
                }
                data.append(row)
    return data

def get_columns():
    return [
        {
            "fieldname": "asset_code",
            "label": _("Asset Code"),
            "fieldtype": "Link",
            "options": "Asset",
            "width": 140
        },
        {
            "fieldname": "asset_name",
            "label": _("Asset Name"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "serial_number",
            "label": _("Serial Number"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "asset_category",
            "label": _("Asset Category"),
            "fieldtype": "Link",
            "options":"Asset Category",
            "width": 150
        },
        # {
        #     "fieldname": "asset_sub_category",
        #     "label": _("Sub Category"),
        #     "fieldtype": "Link",
        #     "options":"Item Sub Group",
        #     "width": 150
        # },
        {
            "fieldname": "reference_type",
            "label": _("Reference Type"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "reference_name",
            "label": _("Reference Name"),
            "fieldtype": "Dynamic Link",
            "options": "reference_type",
            "width": 100
        },
        {
            "fieldname": "issued_to",
            "label": _("Issued To"),
            "fieldtype": "Data",
            "width": 100
        },
         {
            "fieldname": "employee_name",
            "label": _("Employee Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "target_location",
            "label": _("Location"),
            "fieldtype": "Link",
            "options": "Location",
            "width": 130
        },
        {
            "fieldname": "date_of_issue",
            "label": _("Date of Issue"),
            "fieldtype": "Date",
            "width": 120
        }  
    ]

