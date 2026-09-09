# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class BOQItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		adjustment_amount: DF.Float
		adjustment_quantity: DF.Float
		amount: DF.Float
		balance_amount: DF.Float
		balance_quantity: DF.Float
		balance_rate: DF.Float
		booked_amount: DF.Float
		booked_quantity: DF.Float
		boq_code: DF.Data
		claimed_amount: DF.Float
		claimed_quantity: DF.Float
		currency: DF.Link | None
		is_group: DF.Check
		item: DF.Text
		parent: DF.Data
		parent_item: DF.Text | None
		parentfield: DF.Data
		parenttype: DF.Data
		project: DF.Link | None
		quantity: DF.Float
		rate: DF.Float
		received_amount: DF.Float
		received_quantity: DF.Float
		remarks: DF.TextEditor | None
		subcontract_amount: DF.Currency
		subcontract_quantity: DF.Float
		subcontract_rate: DF.Float
		uom: DF.Link | None
	# end: auto-generated types
	pass
