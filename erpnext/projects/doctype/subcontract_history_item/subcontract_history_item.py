# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SubcontractHistoryItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		adjustment_amount: DF.Currency
		final_amount: DF.Currency
		initial_amount: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		remarks: DF.SmallText | None
		transaction_date: DF.Date | None
		transaction_name: DF.DynamicLink | None
		transaction_type: DF.Link | None
	# end: auto-generated types
	pass
