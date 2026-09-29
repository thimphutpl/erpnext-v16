# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectInvoiceItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		boq: DF.Link | None
		gross_invoice_amount: DF.Currency
		invoice_date: DF.Data | None
		invoice_name: DF.Link | None
		net_invoice_amount: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		price_adjustment_amount: DF.Currency
		subcontract: DF.Link | None
		total_balance_amount: DF.Currency
		total_paid_amount: DF.Currency
		total_received_amount: DF.Currency
	# end: auto-generated types
	pass
