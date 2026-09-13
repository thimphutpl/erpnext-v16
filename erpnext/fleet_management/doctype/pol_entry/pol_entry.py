# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class POLEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		amount: DF.Currency
		branch: DF.Link
		cost_center: DF.Link | None
		current_km: DF.Float
		equipment: DF.Link
		equipment_category: DF.Link | None
		equipment_type: DF.Link | None
		fuelbook: DF.Link | None
		is_opening: DF.Check
		item_name: DF.Data | None
		km_difference: DF.Float
		memo_number: DF.Data | None
		mileage: DF.Float
		own_cost_center: DF.Check
		pol_slip_no: DF.Data | None
		pol_type: DF.Data
		posting_date: DF.Date | None
		posting_time: DF.Time | None
		qty: DF.Float
		rate: DF.Currency
		reference_name: DF.DynamicLink | None
		reference_type: DF.Literal["", "POL Receive", "POL Issue", "Vehicle Logbook", "HSD Adjustment", "Equipment POL Transfer"]
		supplier: DF.Link | None
		type: DF.Literal["Receive", "Issue", "Stock", "consumed"]
		uom: DF.Literal["", "Hour", "KM"]
	# end: auto-generated types
	pass
