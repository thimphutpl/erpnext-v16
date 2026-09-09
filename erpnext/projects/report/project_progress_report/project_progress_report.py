# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff

def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters=None):
	columns = []
	if filters.get("parent_project") and not filters.get("project_definition") and not filters.get("project") and not filters.get("task"):
		columns = [
			{
			"fieldname": "project_definition",
			"label": "Project Definition",
			"fieldtype": "Link",
			"options": "Project Definition",
			"width": 150
			},
			{
			"fieldname": "start_date",
			"label": "Start Date",
			"fieldtype": "Date",
			"width": 120
			},
			{
			"fieldname": "end_date",
			"label": "End Date",
			"fieldtype": "Date",
			"width": 120
			},
			{
			"fieldname": "duration",
			"label": "Duration(Days)",
			"fieldtype": "Float",
			"width": 120
			},
			{
			"fieldname": "weightage",
			"label": "PP Weightage(%)",
			"fieldtype": "Float",
			"width": 120
			},
			{
			"fieldname": "site_progress",
			"label": "Site Progress(%)",
			"fieldtype": "Data",
			"width": 120
			},
			{
			"fieldname": "project_progress",
			"label": "Project Progress(%)",
			"fieldtype": "Float",
			"width": 120
			},
			{
			"fieldname": "estimated_budget",
			"label": "Provisional Estimated Budget",
			"fieldtype": "Float",
			"width": 120
			},
			{
			"fieldname": "actual_expenses",
			"label": "Actual Expense",
			"fieldtype": "Float",
			"width": 120
			},
			{
			"fieldname": "financial_progress",
			"label": "Financial Progress(%)",
			"fieldtype": "Float",
			"width": 120
			},
		]
	elif filters.get("parent_project") and filters.get("project_definition") and not filters.get("project") and not filters.get("task"):
		columns = [
			{
			"fieldname": "project",
			"label": "Project",
			"fieldtype": "Link",
			"options": "Project",
			"width": 150
			},
			{
			"fieldname": "start_date",
			"label": "Start Date",
			"fieldtype": "Date",
			"width": 120
			},
			{
			"fieldname": "end_date",
			"label": "End Date",
			"fieldtype": "Date",
			"width": 120
			},
			{
			"fieldname": "duration",
			"label": "Duration(Days)",
			"fieldtype": "Float",
			"width": 120
			},
			{
			"fieldname": "weightage",
			"label": "PP Weightage(%)",
			"fieldtype": "Float",
			"width": 120
			},
			{
			"fieldname": "site_progress",
			"label": "Site Progress(%)",
			"fieldtype": "Data",
			"width": 120
			},
			{
			"fieldname": "project_progress",
			"label": "Project Progress(%)",
			"fieldtype": "Float",
			"width": 120
			},
			{
			"fieldname": "estimated_budget",
			"label": "Provisional Estimated Budget",
			"fieldtype": "Float",
			"width": 120
			},
			{
			"fieldname": "actual_expenses",
			"label": "Actual Expenses",
			"fieldtype": "Float",
			"width": 120
			},
			{
			"fieldname": "financial_progress",
			"label": "Financial Progress(%)",
			"fieldtype": "Data",
			"width": 120
			},
		]
	return columns

def get_data(filters=None):
	data = []
	if filters.get("parent_project") and not filters.get("project_definition") and not filters.get("project") and not filters.get("task"):
		for pd in frappe.db.get_all("Project Definition", {"project_category": filters.get("parent_project"), "docstatus": 1}, ["name", "physical_progress", "physical_progress_weightage", "percent_completed" ,"provisional_estimated_budget", "a_expenses", "f_progress"]):
			start_date = None
			end_date = None
			duration = None
			start_dates = []
			end_dates = []
			cc_mandays = frappe.db.sql("""
                              select sum(mandays) from `tabProject` where project_definition = '{}' and docstatus < 2
                              """.format(pd.name))
			overall_mandays = frappe.db.sql("""
                              select sum(mandays) from `tabProject` where docstatus < 2
                              """.format(pd.name))
			for prj in frappe.db.get_all("Project Definition", {"name": pd.name}, ["start_date", "end_date"]):
				if prj.start_date:
					start_dates.append(prj.start_date)
				if prj.end_date:
					end_dates.append(prj.end_date)
			if len(start_dates) > 0:
				start_date = min(start_dates)
			if len(end_dates) > 0:
				end_date = min(end_dates)
			if start_date and end_date:
				duration = date_diff(end_date, start_date)+1
			data.append({"project_definition": pd.name, "start_date": start_date, "end_date": end_date, "duration": duration, "project_progress": pd.physical_progress, "weightage": pd.physical_progress_weightage, "site_progress": pd.percent_completed, "estimated_budget": pd.provisional_estimated_budget, "actual_expenses": pd.a_expenses, "financial_progress": pd.f_progress})
	elif filters.get("parent_project") and filters.get("project_definition") and not filters.get("project") and not filters.get("task"):
		for pd in frappe.db.get_all("Project", {"project_definition": filters.get("project_definition"), "docstatus": ["<", 2]}, ["name", "physical_progress", "physical_progress_weightage", "percent_completed", "total_duration", "expected_start_date", "expected_end_date", "estimated_budget", "actual_expenses", "financial_progress"]):
			start_date = None
			end_date = None
			duration = None
			# start_dates = []
			# end_dates = []
			# for prj in frappe.db.get_all("Project Definition", {"name": pd.name}, ["start_date", "end_date"]):
			# 	if prj.start_date:
			# 		start_dates.append(prj.start_date)
			# 	if prj.end_date:
			# 		end_dates.append(prj.end_date)
			# if len(start_dates) > 0:
			# 	start_date = min(start_dates)
			# if len(end_dates) > 0:
			# 	end_date = min(end_dates)
			# if start_date and end_date:
			# 	duration = date_diff(end_date, start_date)+1
			data.append({"project": pd.name, "start_date": pd.expected_start_date, "end_date": pd.expected_end_date, "duration": pd.total_duration, "project_progress": pd.physical_progress, "weightage": pd.physical_progress_weightage, "site_progress": pd.percent_completed, "estimated_budget": pd.estimated_budget, "actual_expenses": pd.actual_expenses, "financial_progress": pd.financial_progress})

	return data