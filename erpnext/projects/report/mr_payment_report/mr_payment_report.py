# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data

def get_columns():
	return [
		("Branch ") + ":Data:100",
		("Employee Type") + ":Data:100",
		("Employee ID") + ":Data:90",
		("Employee Name") + ":Data:100",
		("CID") + ":Data:90",
		("Designation") + ":Data:90",
		("Qualification ") + ":Data:80",
		("Bank") + ":Data:60",
		("Account Number") + ":Data:100",
		("Year") + ":Data:40",
		("Month") + ":Data:40",
		("No. of Days") + ":Data:60",
		("Daily Rate") + ":Data:60",
		("Total Wage") + ":Data:60",
		("No. of Hours") + ":Data:60",
		("Hourly Rate") + ":Data:60",
		("Total OT ") + ":Data:60",
		("Gross Pay ") + ":Data:80",
		("Mess Deduction") + ":Data:60",
		("Net Pay") + ":Data:90"
	]

def get_data(filters):
	query = """select p.branch, p.employee_type, i.employee, i.person_name, i.id_card, i.designation, i.qualification, (select bank_name from `tabMuster Roll Employee` where name=i.employee) bank,
			(select bank_ac_no from `tabMuster Roll Employee` where name=i.employee) bank_acc, i.fiscal_year, i.month, i.number_of_days, i.daily_rate,i.total_wage,  i.number_of_hours, 
			i.hourly_rate, i.total_ot_amount, 
			(i.total_wage + i.total_ot_amount), i.mess_deduction, i.total_amount 
			from `tabMR Payment Item` as i, `tabProcess MR Payment` as p 
			where i.parent = p.name and p.docstatus = 1 """

	if filters.get("branch"):
		query += " and p.branch = \'" + str(filters.branch) + "\'"
	if filters.get("year"):
		query += " and i.fiscal_year = \'" + str(filters.year) + "\'"
	if filters.get("month"):
		query += " and i.month = \'" + str(filters.month) + "\'"

	return frappe.db.sql(query)