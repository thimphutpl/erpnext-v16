# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SubcontractItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		adjustment_amount: DF.Currency
		adjustment_quantity: DF.Float
		amount: DF.Currency
		balance_amount: DF.Currency
		balance_quantity: DF.Float
		balance_rate: DF.Float
		booked_amount: DF.Currency
		booked_quantity: DF.Float
		boq_amount: DF.Currency
		boq_code: DF.Data | None
		boq_item_name: DF.Data | None
		boq_quantity: DF.Float
		boq_rate: DF.Float
		claimed_amount: DF.Currency
		claimed_quantity: DF.Float
		currency: DF.Link | None
		is_group: DF.Check
		is_selected: DF.Check
		item: DF.Text | None
		parent: DF.Data
		parent_item: DF.Text | None
		parentfield: DF.Data
		parenttype: DF.Data
		project: DF.Link | None
		quantity: DF.Float
		rate: DF.Float
		received_amount: DF.Currency
		received_quantity: DF.Float
		remarks: DF.TextEditor | None
		uom: DF.Link | None
	# end: auto-generated types
	pass
