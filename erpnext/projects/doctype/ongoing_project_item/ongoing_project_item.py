# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class OngoingProjectItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		branch: DF.Link | None
		cost_center: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		site_name: DF.Data | None
		status: DF.Literal["Ongoing", "Completed"]
		total_cost: DF.Currency
	# end: auto-generated types
	pass
