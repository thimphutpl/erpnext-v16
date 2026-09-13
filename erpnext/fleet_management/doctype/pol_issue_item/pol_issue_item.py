# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class POLIssueItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		cost_center: DF.Link | None
		equipment: DF.Link
		equipment_balance: DF.ReadOnly | None
		equipment_branch: DF.Data | None
		equipment_category: DF.Link | None
		equipment_cost_center: DF.Link | None
		equipment_number: DF.Data | None
		equipment_warehouse: DF.Link
		expense_account: DF.Link | None
		hiring_branch: DF.Data | None
		hiring_cost_center: DF.Data | None
		hiring_warehouse: DF.Data | None
		item_code: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		qty: DF.Float
		serial_and_batch_bundle: DF.Data | None
		warehouse: DF.Link | None
	# end: auto-generated types
	pass
