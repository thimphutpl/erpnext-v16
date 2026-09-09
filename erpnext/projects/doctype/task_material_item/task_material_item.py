# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class TaskMaterialItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		child_reference: DF.Data | None
		item: DF.Link | None
		item_amount: DF.Currency
		item_amount_used: DF.Currency
		item_name: DF.ReadOnly | None
		item_quantity: DF.Float
		item_quantity_used: DF.Float
		item_rate: DF.Currency
		item_uom: DF.ReadOnly | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		reference_name: DF.DynamicLink | None
		reference_type: DF.Link | None
	# end: auto-generated types
	pass
