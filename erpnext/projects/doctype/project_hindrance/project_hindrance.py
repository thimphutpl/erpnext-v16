# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime
# from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states

class ProjectHindrance(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_designation: DF.Data | None
		approver_name: DF.Data | None
		branch: DF.Link
		company: DF.Link
		employee: DF.Link
		from_date: DF.Date
		hindrance_description: DF.LongText
		project: DF.Link
		to_date: DF.Date
	# end: auto-generated types
	pass
	def validate(self):
		validate_workflow_states(self)
		self.check_date()
	def check_date(self):
		if self.from_date > self.to_date:
			frappe.throw("From Date must me before To Date")