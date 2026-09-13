# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class BluebookandEmission(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		application_no: DF.Data
		journal_entry: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		party: DF.Link
		penalty_amount: DF.Currency
		receipt_date: DF.Date
		receipt_number: DF.Data
		remarks: DF.SmallText | None
		total_amount: DF.Currency
		type: DF.Literal["", "Registration Certificate", "Fitness", "Emission", "Offense"]
		valid_upto: DF.Date
	# end: auto-generated types
	pass
