# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MaintenanceAccountsSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF


		# end: auto-generated types

		default_advance_account: DF.Link
		default_advance_amount: DF.Link
		default_goods_account: DF.Link
		default_pol_expense_account: DF.Link
		default_receivable_account: DF.Link
		default_services_account: DF.Link
		discount_account: DF.Link
		hire_expense_account: DF.Link
		hire_revenue_account: DF.Link
		hire_revenue_internal_account: DF.Link
		maintenance_expense_account: DF.Link | None
		pool_vehicle_pol_expenses: DF.Link
	# end: auto-generated types
	pass
