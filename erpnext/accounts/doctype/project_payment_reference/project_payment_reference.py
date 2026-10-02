# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectPaymentReference(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account_head: DF.Data | None
		allocated_amount: DF.Currency
		due_date: DF.Date | None
		exchange_rate: DF.Currency
		gst_amount: DF.Currency
		invoice_type: DF.Data | None
		outstanding_amount: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		reference_doctype: DF.Link | None
		reference_name: DF.DynamicLink | None
		tax_rate: DF.Float
		taxes_and_charges: DF.Data | None
		total_amount: DF.Currency
		total_gst_amount: DF.Currency
	# end: auto-generated types
	pass
