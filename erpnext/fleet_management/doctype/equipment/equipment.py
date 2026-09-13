# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Equipment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.fleet_management.doctype.equipment_operator_item.equipment_operator_item import EquipmentOperatorItem
		from frappe.types import DF

		asset_code: DF.Link | None
		branch: DF.Link
		chasis_number: DF.Data | None
		company: DF.Link
		cost_center: DF.Link | None
		current_hr_reading: DF.Data | None
		current_km_reading: DF.Data | None
		current_operator: DF.Data | None
		disabled: DF.Check
		engine_number: DF.Data | None
		equipment_category: DF.Link
		equipment_model: DF.Link
		equipment_name: DF.Data | None
		equipment_type: DF.Link
		fuel_type: DF.Link | None
		fuelbook: DF.Link | None
		initial_km_reading: DF.Float
		initial_reading: DF.Float
		kph: DF.Float
		lph: DF.Float
		reading_uom: DF.Link | None
		registration_number: DF.Data
		table_qptk: DF.Table[EquipmentOperatorItem]
	# end: auto-generated types
	pass


@frappe.whitelist()
def get_equipments(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("select a.equipment as name from `tabHiring Approval Details` a where docstatus = 1 and a.parent = \'"+ str(filters.get("ehf_name")) +"\'")
