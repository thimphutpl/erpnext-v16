# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectBOQItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		balance_amount: DF.Currency
		boq_date: DF.Data | None
		boq_name: DF.Link | None
		paid_amount: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		price_adjustment: DF.Currency
		received_amount: DF.Currency
		total_amount: DF.Currency
	# end: auto-generated types
	pass
