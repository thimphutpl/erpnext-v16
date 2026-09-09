# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class OvertimePaymentItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		bank_account: DF.ReadOnly
		bank_name: DF.Link
		cost_center: DF.Link | None
		designation: DF.ReadOnly | None
		employee: DF.Link
		employee_name: DF.ReadOnly
		grade: DF.ReadOnly | None
		hourly_rate: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		reference_doc: DF.Link
		total_hours: DF.Float
		total_ot_amount: DF.Currency
	# end: auto-generated types
	pass
