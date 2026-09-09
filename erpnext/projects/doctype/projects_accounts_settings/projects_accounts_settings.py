# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectsAccountsSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		accrued_expense_account: DF.Link | None
		advance_account_internal: DF.Link | None
		advance_account_supplier: DF.Link
		gep_overtime_account: DF.Link | None
		gep_wages_account: DF.Link | None
		inventory_account: DF.Link
		invoice_account_internal: DF.Link | None
		invoice_account_supplier: DF.Link | None
		mess_deduction_account: DF.Link | None
		mr_overtime_account: DF.Link
		mr_wages_account: DF.Link
		project_accrued_income_account: DF.Link | None
		project_advance_account: DF.Link
		project_invoice_account: DF.Link
		retention_account_receivable: DF.Link | None
	# end: auto-generated types
	pass
