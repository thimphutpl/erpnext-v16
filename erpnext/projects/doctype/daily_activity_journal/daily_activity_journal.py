# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DailyActivityJournal(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.projects.doctype.category_works_engaged.category_works_engaged import CategoryWorksEngaged
		from erpnext.projects.doctype.machinery_hours_item.machinery_hours_item import MachineryHoursItem
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		date: DF.Date
		items: DF.Table[CategoryWorksEngaged]
		machinery_items: DF.Table[MachineryHoursItem]
		project: DF.Link
		remarks: DF.SmallText | None
		title: DF.Data
	# end: auto-generated types
	pass
