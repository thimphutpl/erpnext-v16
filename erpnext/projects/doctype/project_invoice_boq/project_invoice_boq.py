# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectInvoiceBOQ(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		act_amount: DF.Float
		act_quantity: DF.Float
		act_rate: DF.Float
		boq: DF.Data | None
		boq_code: DF.Data | None
		boq_item_name: DF.Data | None
		invoice_amount: DF.Float
		invoice_quantity: DF.Float
		invoice_rate: DF.Float
		is_group: DF.Check
		is_selected: DF.Check
		item: DF.Text | None
		original_amount: DF.Float
		original_quantity: DF.Float
		original_rate: DF.Float
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		uom: DF.Link | None
		uptodate_amount: DF.Float
		uptodate_quantity: DF.Float
		uptodate_rate: DF.Float
	# end: auto-generated types
	pass
