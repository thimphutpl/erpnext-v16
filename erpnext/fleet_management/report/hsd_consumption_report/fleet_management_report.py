# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint,add_days, cstr, flt, getdate, nowdate, rounded, date_diff

# #
# Both recieved and issued pols can be queried with this
# #
def get_pol_till(purpose, equipment, date, pol_type=None, additional_type=None):
	if not equipment or not date:
		frappe.throw(_("Equipment and Till Date are Mandatory"))

	total = 0
	query = """
		SELECT SUM(qty) AS total 
		FROM `tabPOL Entry` 
		WHERE docstatus = 1 
			AND type = %s 
			AND equipment = %s 
			AND posting_date <= %s
	"""
	args = [purpose, equipment, date]

	if pol_type:
		query += " AND pol_type = %s"
		args.append(pol_type)

	if additional_type:
		query += " AND type = %s"
		args.append(additional_type)

	quantity = frappe.db.sql(query, args, as_dict=True)
	if quantity and quantity[0].total:
		total = quantity[0].total

	return total

def get_pol_tills(purpose, equipment, date, pol_type=None):
	if not equipment:
		frappe.throw("Equipment and Till Date are Mandatory")
	total = 0
	query = "select sum(qty) as total from `tabPOL Entry` where docstatus = 1 and type = \'"+str(purpose)+"\' and equipment = \'" + str(equipment) + "\'"
	if pol_type:
		query += " and pol_type = \'" + str(pol_type) + "\'"
	

	quantity = frappe.db.sql(query, as_dict=True)
	if quantity:
		total = quantity[0].total
	return total

def get_pol_transfer(purpose, equipment, date, pol_type=None):
	if not equipment:
		frappe.throw("Equipment and Till Date are Mandatory")
	total = 0
	query = "select sum(qty) as total from `tabPOL Entry` where docstatus = 1 and type = \'"+str(purpose)+"\' and equipment = \'" + str(equipment) + "\'"
	if pol_type:
		query += " and pol_type = \'" + str(pol_type) + "\'"
	

	quantity = frappe.db.sql(query, as_dict=True)
	if quantity:
		total = quantity[0].total
	return total

##
# Both recieved and issued pols can be queried with this
##
def get_pol_between(purpose, equipment, from_date, to_date, pol_type=None):
	if not equipment or not from_date or not to_date:
		frappe.throw("Equipment and From/To Date are Mandatory")
	total = 0
	query = "select sum(qty) as total from `tabPOL Entry` where docstatus = 1 and type = \'"+str(purpose)+"\' and equipment = \'" + str(equipment) + "\' and date between \'" + str(from_date) + "\' and \'" + str(to_date) + "\'"
	if pol_type:
		query += " and pol_type = \'" + str(pol_type) + "\'"
		
	quantity = frappe.db.sql(query, as_dict=True)
	if quantity:
		total = quantity[0].total
	return total

##
# Get consumed POl as per yardstick
##
def get_pol_consumed_till(equipment, date):
	if not equipment or not date:
		frappe.throw("Equipment and Till Date are Mandatory")
	pol = frappe.db.sql("select sum(consumption) as total from `tabVehicle Logbook` where docstatus = 1 and equipment = %s and to_date <= %s", (equipment, date), as_dict=True)
	if pol:
		return pol[0].total
	else:
		return 0	
	
def get_pol_consumed_tills(equipment):
	if not equipment:
		frappe.throw("Equipment are Mandatory")
	pol = frappe.db.sql("select sum(consumption) as total from `tabVehicle Logbook` where docstatus = 1 and equipment = %s", (equipment, ), as_dict=True)
	if pol:
		return pol[0].total
	else:
		return 0			

def get_km_till(equipment, date):
	if not equipment or not date:
		frappe.throw("Equipment and Till Date are Mandatory")
	km = frappe.db.sql("select final_km from `tabVehicle Logbook` where docstatus = 1 and equipment = %s and to_date <= %s order by final_km desc limit 1", (equipment, date), as_dict=True)
	if km:
		return km[0].final_km
	else:
		return 0	

def get_hour_till(equipment, date):
	if not equipment or not date:
		frappe.throw("Equipment and Till Date are Mandatory")
	hr = frappe.db.sql("select final_hour from `tabVehicle Logbook` where docstatus = 1 and equipment = %s and to_date <= %s order by final_hour desc limit 1", (equipment, date), as_dict=True)
	if hr:
		return hr[0].final_hour
	else:
		return 0	

def get_employee_expense(equipment, f_date, t_date):
	if not equipment or not f_date or not t_date:
		frappe.throw("Equipment and From/Till Date are Mandatory")

	operators = frappe.db.sql("""
			select operator, employee_type, start_date, end_date
			from `tabEquipment Operator`
			where parent = '{0}' 
			and   docstatus < 2
			and   (start_date between {1} and {2} OR end_date between {3} and {4})
		""".format(equipment, f_date, t_date, f_date, t_date), as_dict=1)

	for a in operators:
		prorate_fraction = 1
		if getdate(f_date) < getdate(a.start_date) and getdate(t_date) > getdate(a.end_date):
		# Pay

		# Bonus

		# PBVA

		# Travel

		#Leave Encashment
			pass