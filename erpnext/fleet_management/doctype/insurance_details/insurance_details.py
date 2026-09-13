# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class InsuranceDetails(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		due_date: DF.Date
		insurance_type: DF.Literal["", "Third Party", "Comprehensive", "Fire Insurance"]
		insured_date: DF.Date
		journal_entry: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		party: DF.Link
		policy_number: DF.Data
		total_amount: DF.Data
		type: DF.Literal["", "Insurance"]
		validity: DF.Date
	# end: auto-generated types
	pass
