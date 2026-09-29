# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectInvoiceMB(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		act_balance_amount: DF.Float
		act_entry_amount: DF.Float
		act_invoice_amount: DF.Float
		act_received_amount: DF.Float
		boq: DF.Link
		boq_type: DF.Data | None
		entry_amount: DF.Float
		entry_date: DF.Date | None
		entry_name: DF.Link
		is_selected: DF.Check
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		price_adjustment_amount: DF.Float
		subcontract: DF.Link | None
	# end: auto-generated types
	pass
