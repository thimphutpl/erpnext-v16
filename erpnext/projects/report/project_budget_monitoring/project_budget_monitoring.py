# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "label": _("Project Definition"),
            "fieldname": "project_definition",
            "fieldtype": "Link",
            "options": "Project Definition",
            "width": 180,
        },
        {
            "label": _("Activity Code"),
            "fieldname": "activity_code",
            "fieldtype": "Data",
            "width": 220,
        },
        {
            "label": _("Branch"),
            "fieldname": "branch",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "label": _("Project Status"),
            "fieldname": "project_status",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Estimated Budget"),
            "fieldname": "estimated_budget",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": _("Actual Expense"),
            "fieldname": "actual_expenses",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": _("Variance"),
            "fieldname": "variance",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": _("Variance %"),
            "fieldname": "variance_percent",
            "fieldtype": "Percent",
            "width": 110,
        },
        {
            "label": _("Budget Status"),
            "fieldname": "budget_status",
            "fieldtype": "Data",
            "width": 130,
        },
    ]

def get_data(filters):
    conditions = ""
    values = {}

    if filters.get("project_definition"):
        conditions += " AND pd.name = %(project_definition)s"
        values["project_definition"] = filters.get("project_definition")

    if filters.get("branch"):
        conditions += " AND opi.branch = %(branch)s"
        values["branch"] = filters.get("branch")

    if filters.get("activity_code"):
        conditions += " AND opi.site_name = %(activity_code)s"
        values["activity_code"] = filters.get("activity_code")

    rows = frappe.db.sql("""
        SELECT
            pd.name AS project_definition,
            opi.site_name AS activity_code,
            opi.branch AS branch,
            opi.status AS project_status,
            p.name AS project,
            p.estimated_budget AS estimated_budget,
            p.actual_expenses AS actual_expenses
        FROM `tabProject Definition` pd
        LEFT JOIN `tabOngoing Project Item` opi
            ON opi.parent = pd.name
        LEFT JOIN `tabProject` p
            ON p.name = opi.site_name
        WHERE pd.docstatus < 2
            {conditions}
        ORDER BY pd.name, opi.idx
    """.format(conditions=conditions), values, as_dict=1)

    data = []

    for row in rows:
        estimated_budget = flt(row.get("estimated_budget"))
        actual_expense = flt(row.get("actual_expenses"))

        variance = estimated_budget - actual_expense

        variance_percent = 0
        if estimated_budget:
            variance_percent = ((actual_expense - estimated_budget) / estimated_budget) * 100

        if not estimated_budget:
            budget_status = "No Budget"
        elif actual_expense > estimated_budget:
            budget_status = "Over Budget"
        elif actual_expense >= estimated_budget * 0.9:
            budget_status = "Near Budget Limit"
        else:
            budget_status = "Within Budget"

        if filters.get("budget_status") and filters.get("budget_status") != budget_status:
            continue

        data.append({
            "project_definition": row.project_definition,
            "activity_code": row.activity_code,
            "branch": row.branch,
            "project_status": row.project_status,
            "estimated_budget": estimated_budget,
            "actual_expenses": actual_expense,
            "variance": variance,
            "variance_percent": variance_percent,
            "budget_status": budget_status,
        })

    return data