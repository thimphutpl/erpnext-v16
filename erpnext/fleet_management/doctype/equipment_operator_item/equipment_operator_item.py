# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EquipmentOperatorItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from_date: DF.Date | None
		operator: DF.DynamicLink
		operator_name: DF.Data | None
		operator_type: DF.Literal["Employee", "Muster Roll Employee"]
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		to_date: DF.Date | None
	# end: auto-generated types
	pass
