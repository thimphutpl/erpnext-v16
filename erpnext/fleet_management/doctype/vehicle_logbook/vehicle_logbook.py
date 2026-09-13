# -*- coding: utf-8 -*-
# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint, getdate, add_days, get_datetime
from erpnext.custom_utils import check_uncancelled_linked_doc, check_future_date
# from erpnext.fleet_management.report.hsd_consumption_report.fleet_management_report import get_pol_tills, get_pol_consumed_tills

class VehicleLogbook(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		closing_balance: DF.Float
		consumption: DF.Float
		consumption_hours: DF.Float
		consumption_km: DF.Float
		customer: DF.Link | None
		customer_type: DF.Data | None
		distance_km: DF.Int
		ehf_name: DF.Link | None
		equipment: DF.Link | None
		equipment_operator: DF.Data | None
		equipment_run_by_electric: DF.Check
		final_hour: DF.Float
		final_km: DF.Int
		from_date: DF.Date
		from_time: DF.Time
		hour_adjustment_reason: DF.Data | None
		hour_taken: DF.Int
		hsd_amount: DF.Data | None
		hsd_received: DF.Float
		idle_charge: DF.Check
		idle_rate: DF.Currency
		include_hour: DF.Check
		include_km: DF.Check
		initial_hour: DF.Float
		initial_km: DF.Int
		invoice_created: DF.Check
		kph: DF.Float
		lph: DF.Float
		opening_balance: DF.Float
		other_consumption: DF.Float
		payment_completed: DF.Check
		place: DF.Data | None
		pol_type: DF.Data | None
		pool_equipment: DF.Link | None
		pool_equipment_number: DF.Data | None
		rate_type: DF.Data | None
		reason: DF.Data | None
		registration_number: DF.Data | None
		remarks: DF.TextEditor | None
		tank_balance: DF.Data | None
		to_date: DF.Date
		to_time: DF.Time
		total_idle_time: DF.Float
		total_work_time: DF.Float
		vehicle_logbook: DF.Literal["", "Equipment Hiring Form"]
		vlogs: DF.Data | None
		work_rate: DF.Currency
		working_hours: DF.Int
		ys_hours: DF.Float
		ys_km: DF.Float
	# end: auto-generated types

	

	def validate(self):
		# check_future_date(self.to_date)
		self.validate_date()
		self.set_data()
		self.check_dates()
		self.check_double_vl()
		self.check_hire_form()
		self.check_hire_rate()
		# self.check_duplicate()
		self.update_consumed()
		# self.calculate_totals()
		self.update_operator()
		self.check_consumed()
		self.get_pool_equipment()	

		if self.vehicle_logbook in ["Pool Vehicle", "Support Equipment"]:
			self.customer = None 
			self.customer_type = None
		elif not self.customer:
			frappe.throw(("Customer is required for this Vehicle Logbook type."))
	
	def validate_date(self):
		from_date = get_datetime(str(self.from_date) + ' ' + str(self.from_time))
		to_date = get_datetime(str(self.to_date) + ' ' + str(self.to_time))
		if to_date < from_date:
			frappe.throw("From Date/Time cannot be greater than To Date/Time")

		if self.working_hours:
			return
		# elif self.equipment_run_by_electric > 0:
		# 	frappe.throw("Non HSD Consumption cannot be used when yardstick {} is given.".format(self.lph or self.kph))	

		if self.lph or self.kph:
			self.equipment_run_by_electric = 0
	

	def before_save(self):
		if self.working_hours:
			return
		
		# if self.equipment_run_by_electric:
		# 	frappe.throw("Non HSD Consumption cannot be used when yardstick {} is given.".format(self.lph or self.kph))

		if self.lph or self.kph:
			self.equipment_run_by_electric = 0	

        # # Ensure consumption does not exceed tank balance
		# if flt(self.tank_balance) < flt(self.consumption):
		# 	frappe.throw(
        #         ("Tank balance ({}) should be greater than or equal to consumption ({}).").format(
        #             self.tank_balance, self.consumption
        #         )
        #     )
		if self.vehicle_logbook in ["Pool Vehicle", "Support Equipment"]:
			self.customer = None 
			self.customer_type = None
		elif not self.customer:
			frappe.throw(("Customer is required for this Vehicle Logbook type."))	

		# if self.lph or self.kph and self.equipment_run_by_electric:
		# 	frappe.throw("Non HSD Consumption cannot be used when yardstick {} is given.".format(self.lph or self.kph))

	def set_data(self):
		if self.vehicle_logbook == "Pool Vehicle":
			return

		if self.vehicle_logbook == "Support Equipment":
			return	
		

		if not self.ehf_name:
			frappe.throw("Equipment Hire Form is mandatory")
		self.customer_type = frappe.db.get_value("Equipment Hiring Form", self.ehf_name, "private")
		self.customer = frappe.db.get_value("Equipment Hiring Form", self.ehf_name, "customer")

	def check_consumed(self):
		if self.include_hour or self.include_km:
			if self.equipment_run_by_electric:
				return
			if self.working_hours:
				return
			
			if flt(self.consumption) <= 0:
				frappe.throw("Total consumption cannot be zero or less")

	def check_hire_rate(self):
		if self.vehicle_logbook == "Pool Vehicle":
			return

		if self.vehicle_logbook == "Support Equipment":
			return	
		
		if self.rate_type == "Without Fuel":
			return
		
		if self.working_hours:
			return
		
		if self.equipment_run_by_electric:
			return
		
		based_on = frappe.db.get_single_value("Mechanical Settings", "hire_rate_based_on")
		if not based_on:
			frappe.throw("Set the <b>Hire Rate Based On</b> in <b>Mechanical Settings</b>")
		c = frappe.get_doc("Customer", self.customer)
		wf = "a.rate_fuel"
		wof = "a.rate_wofuel"
		ir = "a.idle_rate"

		if True:
			wf = "a.rate_fuel_internal"
			wof = "a.rate_wofuel_internal"
			ir = "a.idle_rate_internal"

			e = frappe.get_doc("Equipment", self.equipment)

			db_query = "select {0}, {1}, {2}, a.yard_hours, a.yard_distance from `tabHire Charge Item` a, `tabHire Charge Parameter` b where a.parent = b.name and b.equipment_type = '{3}' and b.equipment_model = '{4}' and '{5}' between a.from_date and ifnull(a.to_date, now()) and '{6}' between a.from_date and ifnull(a.to_date, now()) LIMIT 1"
			data = frappe.db.sql(db_query.format(wf, wof, ir, e.equipment_type, e.equipment_model, self.from_date, self.to_date), as_dict=True)
			if not data:
				frappe.throw("There is either no Hire Charge defined or your logbook period overlaps with the Hire Charge period.")
			# if based_on == "Hire Charge Parameter":
			# 	name = frappe.db.sql("select ha.name, ha.tender_hire_rate as thr from `tabHiring Approval Details` ha, `tabEquipment Hiring Form` h where ha.parent = h.name and h.docstatus = 1 and ha.equipment = %s and h.name = %s", (str(self.equipment), str(self.ehf_name)), as_dict=True)
			# if name and name[0]['thr'] == 0:
			# 	self.idle_rate = data[0].idle_rate
			# 	if self.rate_type == "With Fuel":
			# 		self.work_rate = data[0].rate_fuel
			# 	if self.rate_type == "Without Fuel":
			# 		self.work_rate = data[0].rate_wofuel
			self.ys_km = data[0].yard_distance
			self.ys_hours = data[0].yard_hours


	def on_update(self):
		self.calculate_balance()

	def on_submit(self):
		self.check_double_vl()
		self.check_hire_rate()
		self.update_consumed()
		# self.calculate_totals()
		# self.check_consumption()
		self.update_hire()
		# self.post_equipment_status_entry()
		#self.check_tank_capacity()
	
	def on_cancel(self):
		check_uncancelled_linked_doc(self.doctype, self.name)
		# frappe.db.sql("delete from `tabEquipment Status Entry` where ehf_name = \'"+str(self.name)+"\'")

	def check_dates(self):
		if getdate(self.from_date) > getdate(self.to_date):
			frappe.throw("From Date cannot be smaller than To Date")

		# if getdate(self.from_date).month != getdate(self.to_date).month:
		# 	frappe.throw("From Date and To Date should be in the same month")

	def check_hire_form(self):
		if self.vehicle_logbook == "Pool Vehicle":
			# Skip setting data for Pool Vehicle
			return
		
		if self.vehicle_logbook == "Support Equipment":
			# Skip setting data for Support Equipment
			return
		if self.working_hours:
			return

		if self.equipment_run_by_electric:
			return	
		
		# if self.lph or self.kph and self.equipment_run_by_electric:
		# 	frappe.throw("Non HSD Consumption cannot be used when {self.lph} {self.kph} is there.")
			
		if self.ehf_name:
			docstatus = frappe.db.get_value("Equipment Hiring Form", self.ehf_name, "docstatus")
			if docstatus != 1:
				frappe.throw("Cannot create Vehicle Logbook without submitting Hire Form")
		try:
			name = frappe.db.sql("select name from `tabHiring Approval Details` where parent = %s and equipment = %s", (self.ehf_name, self.equipment))[0]
		except:
			frappe.throw("Make sure the equipment you selected is in the corresponding hire form")	

	def update_operator(self):
		self.equipment_operator = frappe.db.get_value("Equipment", self.equipment, "current_operator")

	def check_duplicate(self):		
		for a in self.vlogs:
			for b in self.vlogs:
				if a.date == b.date and a.idx != b.idx:
					frappe.throw("Duplicate Dates in Vehicle Logs in row " + str(a.idx) + " and " + str(b.idx))

	def update_consumed(self):
		pol_type = frappe.db.get_value(
			"Equipment",
			self.equipment,
			"fuel_type"
		)

		closing = frappe.db.sql(
			"""
			SELECT `closing_balance`, `to_date`
			FROM `tabVehicle Logbook`
			WHERE `docstatus` = 1
				AND `equipment` = %s
				AND `to_date` <= %s
			ORDER BY `to_date` DESC
			LIMIT 1
			""",
			(self.equipment, self.from_date),
			as_dict=True,
		)

		if closing:
			qty = frappe.db.sql(
				"""
				SELECT SUM(`qty`) AS qty
				FROM `tabConsumed POL`
				WHERE `equipment` = %s
					AND `date` BETWEEN %s AND %s
					AND `docstatus` = 1
					AND `pol_type` = %s
				""",
				(
					self.equipment,
					add_days(closing[0].to_date, 1),
					self.to_date,
					pol_type,
				),
				as_dict=True,
			)
		else:
			qty = frappe.db.sql(
				"""
				SELECT SUM(`qty`) AS qty
				FROM `tabConsumed POL`
				WHERE `equipment` = %s
					AND `date` <= %s
					AND `docstatus` = 1
					AND `pol_type` = %s
				""",
				(
					self.equipment,
					self.to_date,
					pol_type,
				),
				as_dict=True,
			)

		if qty:
			self.hsd_received = qty[0].qty

	def calculate_totals(self):
		if self.vlogs:
			total_w = total_i = 0
			for a in self.vlogs:
				total_w += flt(a.work_time)
				total_i += flt(a.idle_time)
			self.total_work_time = total_w
			self.total_idle_time = total_i

		# if self.include_km:
		# 	if flt(self.ys_km) > 0:
		# 		self.consumption_km = flt(self.distance_km) / flt(self.ys_km)
		# 	elif flt(self.kph) > 0:
		# 		self.consumption_km = flt(self.distance_km)	/ flt(self.kph)	
		if self.include_km:
			if flt(self.ys_km) > 0:
				self.consumption_km = flt(self.distance_km) / flt(self.ys_km)
			elif flt(self.kph) > 0:
				self.consumption_km = flt(self.distance_km)	/ flt(self.kph)
	

		if self.include_hour:
			if flt(self.ys_hours) > 0:
				self.consumption_hours = flt(self.ys_hours) * flt(self.total_work_time)
			elif flt(self.lph) > 0:
				self.consumption_hours = flt(self.lph) * flt(self.total_work_time)

		# Auto-calculate hsd_amount as ys_km * distance_km
		if self.ys_km and self.distance_km:
			self.hsd_amount = flt(self.ys_km) * flt(self.distance_km)	
		
		self.consumption = flt(self.other_consumption) + flt(self.consumption_hours) + flt(self.consumption_km)
		self.closing_balance = flt(self.hsd_received) + flt(self.opening_balance) - flt(self.consumption)
	

	def update_hire(self):
		if self.ehf_name:
			doc = frappe.get_doc("Equipment Hiring Form", self.ehf_name)
			doc.db_set("hiring_status", 1)
		e = frappe.get_doc("Equipment", self.equipment)
		

		if self.final_km:
			# self.check_repair(cint(e.current_km_reading), cint(self.final_km))
			e.db_set("current_km_reading", flt(self.final_km))

		if self.final_hour:
			# self.check_repair(cint(e.current_hr_reading), cint(self.final_hour))
			e.db_set("current_hr_reading", flt(self.final_hour))

	def post_equipment_status_entry(self):
		doc = frappe.new_doc("Equipment Status Entry")
		doc.flags.ignore_permissions = 1 
		doc.equipment = self.equipment
		doc.reason = "Hire"
		doc.ehf_name = self.name
		doc.from_date = self.from_date
		doc.to_date = self.to_date
		doc.hours = self.total_work_time
		doc.to_time = self.to_time
		doc.from_time = self.from_time
		# doc.place = frappe.db.sql("select place from `tabHiring Approval Details` where parent = %s and equipment = %s", (self.ehf_name, self.equipment))[0]
		if self.vehicle_logbook == "Pool Vehicle":
			# result = frappe.db.sql(
			# 	"SELECT place FROM `tabHiring Approval Details` WHERE equipment = %s",
			# 	(self.equipment,),
			# )
			pass
		else:
			result = frappe.db.sql(
				"SELECT place FROM `tabHiring Approval Details` WHERE parent = %s AND equipment = %s",
				(self.ehf_name, self.equipment),
			)

		# if result:
		# 	doc.place = result[0][0]
		# else:
		# 	frappe.throw("No matching place found for the provided details.")
		doc.submit()

	def calculate_balance(self):
		self.db_set("closing_balance", flt(self.opening_balance) + flt(self.hsd_received) - flt(self.consumption))

	def check_repair(self, start, end):
		et, em, branch = frappe.db.get_value("Equipment", self.equipment, ["equipment_type", "equipment_model", "branch"])
		interval = frappe.db.get_value("Hire Charge Parameter", {"equipment_type": et, "equipment_model": em}, "interval")
		if interval:
			for a in range(start, end):
				if (flt(a) % flt(interval)) == 0:
					mails = frappe.db.sql("select email from `tabRegular Maintenance Item` where parent = %s", branch, as_dict=True)
					for b in mails:
						subject = "Regular Maintenance for " + str(self.equipment)
						message = "It is time to do regular maintenance for equipment " + str(self.equipment) + " since it passed the hour/km reading of " + str(a) 
						if b.email:
							try:
								frappe.sendmail(recipients=b.email, sender=None, subject=subject, message=message)
							except:
								pass
					break

	def check_tank_capacity(self):
		em = frappe.db.get_value("Equipment", self.equipment, "equipment_model")
		tank = frappe.db.get_value("Equipment Model", em, "tank_capacity") 
		if tank:
			if flt(tank) < flt(self.closing_balance):
				frappe.msgprint("Closing balance cannot be greater than the tank capacity (" + str(tank) + ")")

	def check_double_vl(self):
		from_datetime = get_datetime(
			f"{self.from_date} {self.from_time}"
		)
		to_datetime = get_datetime(
			f"{self.to_date} {self.to_time}"
		)

		query = """
			SELECT ehf_name
			FROM `tabVehicle Logbook`
			WHERE equipment = %s
				AND docstatus IN (0, 1)
				AND name != %s
				AND %s <= TIMESTAMP(`to_date`, `to_time`)
				AND %s >= TIMESTAMP(`from_date`, `from_time`)
		"""

		result = frappe.db.sql(
			query,
			(
				self.equipment,
				self.name,
				from_datetime,
				to_datetime,
			),
			as_dict=True,
		)

		for a in result:
			frappe.throw(
				"The logbook for the same equipment, date, and time "
				"has been created at " + str(a.ehf_name)
			)

	def check_consumption(self):
		no_own_fuel_tank = frappe.db.get_value("Equipment Type", frappe.db.get_value("Equipment", self.equipment, "equipment_type"), "no_own_tank")
		if no_own_fuel_tank:
			return
		if self.customer_type == "CDCL":
			if flt(self.consumption_km) == 0 and flt(self.consumption_hours) == 0 and flt(self.consumption) == 0:
				self.check_condition()	
		else:
			if self.rate_type == "Without Fuel":
				if flt(self.consumption_km) > 0 or flt(self.consumption_hours) > 0:
					frappe.throw("Should not have consumption when on dry hire to outside customers")
			else:
				if flt(self.consumption_km) == 0 and flt(self.consumption_hours) == 0 and flt(self.consumption) == 0:
					self.check_condition()	

	def check_condition(self): 
		if self.working_hours:
			return
	
		if self.equipment_run_by_electric:
			return
		
		if self.include_km or self.include_hour:
			if self.include_km and self.initial_km == self.final_km:
				pass
			elif self.include_hour and self.initial_hour == self.final_hour:
				pass
			else:
				frappe.throw("Consumption is Mandatory")
		else:
			frappe.throw("Consumption is Mandatory")

	def get_pool_equipment(self):
		if self.vehicle_logbook == "Pool Vehicle":
			pool_equipment = frappe.db.sql("""
				SELECT name
				FROM `tabEquipment`
				WHERE equipment_category = 'Pool Vehicle'
			""", as_dict=True)
			return [equipment['name'] for equipment in pool_equipment]
		return []

@frappe.whitelist()
def get_yards(equipment):
	t, m = frappe.db.get_value("Equipment", equipment, ['equipment_type', 'registration_number'])
	data = frappe.db.sql("select lph, kph from `tabEquipment` where equipment_type = %s and registration_number = %s", (t, m), as_dict=True)
	if not data:
		frappe.throw("Setup yardstick for " + str(m))
	return data			

@frappe.whitelist()
def get_opening(equipment, from_date, to_date, pol_type):
	if not pol_type:
		frappe.throw("Set HSD type in Equipment")

	closing = frappe.db.sql("select name, closing_balance, to_date, final_km, final_hour from `tabVehicle Logbook` where docstatus = 1 and equipment = %s and to_date <= %s order by to_date desc, to_time desc limit 1", (equipment, from_date), as_dict=True)

	if closing:
		qty = frappe.db.sql("select sum(qty) as qty from `tabConsumed POL` where equipment = %s and date between %s and %s and docstatus = 1 and pol_type = %s", (equipment, add_days(closing[0].to_date, 1), to_date, pol_type), as_dict=True)
	else:
		qty = frappe.db.sql("select sum(qty) as qty from `tabConsumed POL` where equipment = %s and date <= %s and docstatus = 1 and pol_type = %s", (equipment, to_date, pol_type), as_dict=True)

	c_km = frappe.db.sql("select final_km from `tabVehicle Logbook` where docstatus = 1 and equipment = %s and to_date <= %s order by to_date desc limit 1", (equipment, from_date), as_dict=True)

	c_hr = frappe.db.sql("select final_hour from `tabVehicle Logbook` where docstatus = 1 and equipment = %s and to_date <= %s order by to_date desc limit 1", (equipment, from_date), as_dict=True)
	result = []
	if closing:
		result.append(closing[0].closing_balance)
		result.append(closing[0].final_km)
		result.append(closing[0].final_hour)
	else:
		result.append(0)
		result.append(0)
		result.append(0)

	if qty:
		result.append(qty[0].qty)
	else:
		result.append(0)

	'''if c_km:
		result.append(c_km[0].final_km)
	else:
		result.append(0)

	if c_hr:
		result.append(c_hr[0].final_hour)
	else:
		result.append(0)'''

	return result


@frappe.whitelist()
def get_equipment_data(equipment_name, all_equipment=0, branch=None):
    data = []

    query = """
        SELECT e.name, e.branch, e.registration_number, e.hsd_type, e.equipment_type
        FROM `tabEquipment` e
        JOIN `tabEquipment Type` et ON e.equipment_type = et.name
    """

    if not all_equipment:
        query += " WHERE et.is_container = 1"
    else:
        query += " WHERE 1=1"
    
    if branch:
        query += " AND e.branch = %(branch)s"
    if equipment_name:
        query += " AND e.name = %(equipment_name)s"
    
    query += " ORDER BY e.branch"
    
    items = frappe.db.sql("""
        SELECT item_code, item_name, stock_uom 
        FROM `tabItem`
        WHERE disabled = 0
    """, as_dict=True)
    
    equipment_details = frappe.db.sql(query, {
        'branch': branch,
        'equipment_name': equipment_name
    }, as_dict=True)
    
    for eq in equipment_details:
        for item in items:
            received = issued = 0
            if all_equipment:
                if eq.hsd_type == item.item_code:
                    received = get_pol_tills("Receive", eq.name, item.item_code)
                    issued = get_pol_consumed_tills(eq.name,)
            else:
                received = get_pol_tills("Stock", eq.name, item.item_code)
                issued = get_pol_tills("Issue", eq.name, item.item_code)
						
            
            if received or issued:
                data.append({
                    'received': received,
                    'issued': issued,
                    'balance': flt(received) - flt(issued)
                })

			# if received or issued:
			# 		row = [received, issued, flt(received) - flt(issued)]
			# 		data.append(row)	
    
    return data

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles: 
		return

	return """(
		`tabVehicle Logbook`.owner = '{user}'
		or
		exists(select 1
			from `tabEmployee` as e
			where e.branch = `tabVehicle Logbook`.branch
			and e.user_id = '{user}')
		or
		exists(select 1
			from `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
			where e.user_id = '{user}'
			and ab.employee = e.name
			and bi.parent = ab.name
			and bi.branch = `tabVehicle Logbook`.branch)
	)""".format(user=user)
