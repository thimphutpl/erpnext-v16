# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from frappe.model.document import Document


class EmployeeGroup(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.setup.doctype.employee_group_table.employee_group_table import EmployeeGroupTable
		from frappe.types import DF
		from hrms.hr.doctype.employee_group_item.employee_group_item import EmployeeGroupItem

		employee_group_name: DF.Data
		employee_list: DF.Table[EmployeeGroupTable]
		employee_pf: DF.Percent
		employer_pf: DF.Percent
		encashment_frequency: DF.Int
		encashment_lapse: DF.Float
		encashment_min: DF.Float
		health_contribution: DF.Percent
		increment_prorated: DF.Check
		items: DF.Table[EmployeeGroupItem]
		leave_encashment_amount: DF.Currency
		leave_encashment_months: DF.Float
		leave_encashment_type: DF.Literal["", "Flat Amount", "Basic Pay", "Gross Pay"]
		limit_multiplier: DF.Float
		max_encashment_days: DF.Float
		min_encashment_days: DF.Float
		minimum_months: DF.Float
		no_of_installment_for_salary: DF.Literal["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
		retirement_age: DF.Int
		salary_advance_limit: DF.Data | None
		salary_advance_max_months: DF.Float
		salary_advance_type: DF.Literal["", "Flat Amount", "Basic Pay", "Net Pay", "Gross Pay"]
	# end: auto-generated types

	pass
