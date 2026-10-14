# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AssetReceivedEntries(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link | None
		brand: DF.Link | None
		child_ref: DF.Data | None
		company: DF.Link | None
		cost_center: DF.Link | None
		item_code: DF.Link
		item_name: DF.Data | None
		model: DF.Data | None
		qty: DF.Data
		received_date: DF.Date
		ref_doc: DF.Link
		warehouse: DF.Link | None
	# end: auto-generated types

	pass
