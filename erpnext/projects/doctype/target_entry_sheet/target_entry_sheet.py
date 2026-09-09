# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TargetEntrySheet(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		activity_weightage: DF.ReadOnly | None
		amended_from: DF.Link | None
		entry_name: DF.Data | None
		entry_type: DF.Data | None
		from_date: DF.Date | None
		ga_weightage: DF.ReadOnly | None
		percent_completed: DF.Data | None
		percent_completed_overall: DF.Data | None
		percent_completed_overall_gi: DF.Data | None
		project: DF.Link | None
		project_parent: DF.Link | None
		to_date: DF.Date | None
	# end: auto-generated types
	pass
