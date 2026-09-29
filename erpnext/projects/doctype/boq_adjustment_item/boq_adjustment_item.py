# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class BOQAdjustmentItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		adjustment_amount: DF.Float
		adjustment_quantity: DF.Float
		adjustment_rate: DF.Float
		adjustment_type: DF.Literal["Update existing balance"]
		amount: DF.Float
		balance_amount: DF.Currency
		balance_amount_adj: DF.Currency
		balance_quantity: DF.Float
		balance_quantity_adj: DF.Float
		balance_rate: DF.Float
		balance_rate_adj: DF.Float
		booked_amount: DF.Float
		booked_quantity: DF.Float
		boq_code: DF.Data
		boq_item_name: DF.Data | None
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
		uom: DF.Link | None
	# end: auto-generated types
	pass
