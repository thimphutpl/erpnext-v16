# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Fuelbook(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		disabled: DF.Check
		equipment: DF.Link | None
		fuelbook_number: DF.Data
		supplier: DF.Link
		type: DF.Literal["Own", "Common"]
	# end: auto-generated types
	pass
