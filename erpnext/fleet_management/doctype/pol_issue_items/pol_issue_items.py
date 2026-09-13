# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class POLIssueItems(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		equipment: DF.Link
		equipment_branch: DF.Data | None
		equipment_category: DF.Link | None
		equipment_cost_center: DF.Link | None
		equipment_number: DF.Data | None
		equipment_warehouse: DF.Link
		has_serial_no: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		qty: DF.Float
	# end: auto-generated types
	pass
