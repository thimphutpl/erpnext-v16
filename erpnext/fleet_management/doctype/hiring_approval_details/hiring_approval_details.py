# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HiringApprovalDetails(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		diff_rate: DF.Check
		equipment: DF.Link | None
		equipment_model: DF.ReadOnly | None
		equipment_type: DF.Link
		from_date: DF.Date
		from_time: DF.Time | None
		grand_total: DF.Currency
		idle_rate: DF.Currency
		irate1: DF.Currency
		irate2: DF.Currency
		irate3: DF.Currency
		irate4: DF.Currency
		irate5: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		place: DF.Data | None
		rate3: DF.Currency
		rate4: DF.Currency
		rate5: DF.Currency
		rate: DF.Currency
		rate_type: DF.Literal["", "With Fuel", "Without Fuel"]
		registration_number: DF.Data | None
		remarks: DF.SmallText | None
		request_reference: DF.Data | None
		to_date: DF.Date
		to_time: DF.Time | None
		total_hours: DF.Data
	# end: auto-generated types
	pass
