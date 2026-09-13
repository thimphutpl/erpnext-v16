# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate
from frappe.utils.data import nowdate, add_years, add_days, date_diff

class HireChargeParameter(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.fleet_management.doctype.hire_charge_item.hire_charge_item import HireChargeItem
		from frappe.types import DF

		amended_from: DF.Link | None
		benchmark: DF.Float
		equipment: DF.Link | None
		equipment_model: DF.Link
		equipment_type: DF.Link
		idle: DF.Currency
		idle_internal: DF.Currency
		interval: DF.Float
		items: DF.Table[HireChargeItem]
		kph: DF.Float
		lph: DF.Float
		registration_number: DF.Data
		with_fuel: DF.Currency
		with_fuel_internal: DF.Currency
		without_fuel: DF.Currency
		without_fuel_internal: DF.Currency
	# end: auto-generated types
	def before_save(self):
		for i, item in enumerate(sorted(self.items, key=lambda item: item.from_date), start=1):
			item.idx = i

	# def validate(self):
	# 	self.set_dates()
	# 	self.set_parameter_values()

	def validate(self):
		self.set_dates()
		self.set_parameter_values()

		# Check if the hire charge parameter for the same equipment already exists
		existing_parameter = frappe.db.get_value(
			"Hire Charge Parameter",
			{
				"registration_number": self.registration_number,
				"equipment_type": self.equipment_type,
				"equipment_model": self.equipment_model,
				"name": ["!=", self.name],  # Exclude the current document
			},
			"name"
		)

		if existing_parameter:
			frappe.throw(
				f"Hire Charge Parameter already exists for Equipment '{self.registration_number}'. "
				f"Please update '{existing_parameter}' instead of creating a duplicate."
			)


	def set_dates(self):
							to_date = self.items[len(self.items) - 1].to_date
							for a in reversed(self.items):
									a.to_date = to_date
									to_date = add_days(a.from_date, -1)

	def set_parameter_values(self):
		# p = frappe.db.sql("select name from `tabHire Charge Parameter` where registration_number = %s and equipment_type = %s and equipment_model = %s and name != %s", str(self.registeration_number), (str(self.equipment_type), str(self.equipment_model), str(self.name)), as_dict=True)
		p = frappe.db.sql(
			"""
			SELECT name 
			FROM `tabHire Charge Parameter` 
			WHERE registration_number = %s 
			AND equipment_type = %s 
			AND equipment_model = %s 
			AND name != %s
			""", 
			(self.registration_number, self.equipment_type, self.equipment_model, self.name),
			as_dict=True
		)
		if p:
			frappe.throw("Hire Charges for the equipment type and model already exists. Update " + str(p[0].name))
		if self.items:
			self.db_set("without_fuel", self.items[len(self.items) - 1].rate_wofuel)	
			self.db_set("with_fuel", self.items[len(self.items) - 1].rate_fuel)	
			self.db_set("idle", self.items[len(self.items) - 1].idle_rate)	
			self.db_set("without_fuel_internal", self.items[len(self.items) - 1].rate_wofuel_internal)
			self.db_set("with_fuel_internal", self.items[len(self.items) - 1].rate_fuel_internal)
			self.db_set("idle_internal", self.items[len(self.items) - 1].idle_rate_internal)
			self.db_set("lph", self.items[len(self.items) - 1].yard_hours)	
			self.db_set("kph", self.items[len(self.items) - 1].yard_distance)	
			self.db_set("benchmark", self.items[len(self.items) - 1].perf_bench)	
			self.db_set("interval", self.items[len(self.items) - 1].main_int)
		if len(self.items) > 1:
			for a in range(len(self.items)-1):
				self.items[a].to_date = frappe.utils.data.add_days(getdate(self.items[a + 1].from_date), -1)


@frappe.whitelist()
def fetch_registration_numbers(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql(
        """
        SELECT
            registration_number
        FROM
            `tabEquipment`
        WHERE
            equipment_type = %(equipment_type)s
        AND
            registration_number LIKE %(txt)s
        LIMIT %(start)s, %(page_len)s
        """,
        {
            "equipment_type": filters.get("equipment_type"),
            "txt": f"%{txt}%",
            "start": start,
            "page_len": page_len
        }
    )
