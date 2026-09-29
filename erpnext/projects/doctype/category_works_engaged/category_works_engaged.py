# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CategoryWorksEngaged(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		activity_type: DF.Link
		carpenter: DF.Int
		electrician: DF.Int
		mason: DF.Int
		operator: DF.Int
		others: DF.Int
		painter: DF.Int
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		quantity: DF.Float
		technician: DF.Int
		time_hrs: DF.Float
		unit: DF.Link | None
		workers: DF.Int
	# end: auto-generated types
	pass
