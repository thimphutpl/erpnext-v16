# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EquipmentCategory(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		allow_hire: DF.Check
		description: DF.SmallText | None
		disabled: DF.Check
		equipment_category: DF.Data
		pol_advance_account: DF.Link | None
		r_m_expense_account: DF.Link | None
	# end: auto-generated types
	pass
