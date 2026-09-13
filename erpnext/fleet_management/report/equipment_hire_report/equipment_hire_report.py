# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns =get_columns()
	data =get_data(filters)
	return columns, data

def get_columns():
	return [
		("Equipment") + ":Link/Equipment:120",
		("Equipment Type") + ":data:120",
		("Equipment No")+":data:100",
		("Hire Form Name")+":Link/Equipment Hiring Form:150",
		("Customer Name") + ":data:120",
		("Customer Type") + ":data:120",
		("Hour W Fuel")+":data:80",
		("Rate W Fuel")+":Currency:150",
		("Amount W Fuel")+":Currency:150",
		("Hour W/O Fuel")+":data:80",
		("Rate W/O Fuel")+":Currency:150",
		("Amount W/O Fuel")+":Currency:150",
		("Idle Hour")+ ":data:80",
       		("Idle Rate")+":Currency:150",
		("Idle Amount") + ":Currency:150",
		("CDCL")+":Currency:150",
		("Private")+":Currency:150",
		("Others")+":Currency:150",
		("Total Hire Charge")+":Currency:150",
	]

def get_data(filters):
	query ="""select hid.equipment, (select equipment_type FROM tabEquipment e WHERE e.name = hid.equipment), hid.registration_number, hci.ehf_name, hci.customer, (select c.customer_group FROM tabCustomer AS c WHERE hci.customer = c.name),
        CASE hid.rate_type
        WHEN 'With Fuel' THEN (select sum(hid.total_work_hours))
        END,
        CASE hid.rate_type
        WHEN 'With Fuel' THEN (select hid.work_rate)
        END,
        CASE hid.rate_type
        WHEN 'With Fuel' THEN (select sum(hid.amount_work))
        END,
        CASE hid.rate_type
        WHEN 'Without Fuel' THEN (select sum(hid.total_work_hours))
        END,
        CASE hid.rate_type
        WHEN 'Without Fuel' THEN (select hid.work_rate)
        END,
        CASE hid.rate_type
        WHEN 'Without Fuel' THEN (select sum(hid.amount_work))
        END,
        sum(hid.total_idle_hours), hid.idle_rate, sum(hid.amount_idle),
        CASE hci.owned_by
        WHEN 'CDCL' THEN (select sum(hid.total_amount))
        END,
        CASE hci.owned_by
        WHEN 'Private' THEN (select sum(hid.total_amount))
        END,
        CASE hci.owned_by
        WHEN 'Others' THEN (select sum(hid.total_amount))
        END,sum(hid.total_amount) FROM `tabHire Invoice Details` AS hid, `tabHire Charge Invoice` AS hci, `tabEquipment` e,  `tabVehicle Logbook` vl   WHERE hid.parent = hci.name AND hid.vehicle_logbook = vl.name and hid.equipment = e.name and hci.docstatus = 1 and ((vl.from_date between '{0}' and '{1}') or (vl.to_date between '{0}' and '{1}'))""".format(filters.get("from_date"), filters.get("to_date"))

	if filters.get("branch"):
		query += " and hci.branch = \'" + str(filters.branch) + "\'"

	'''if filters.get("from_date") and filters.get("to_date"):
		query += " and (vl.from_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'") or
		(vl.to_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'")

		#OR vl.to_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"'''


	if filters.get("customer"):
		query += " and hci.customer = \'" + str(filters.customer) + "\'"
	query += " group by hid.equipment, hci.ehf_name"
	#frappe.msgprint("{0}, {1}".format(filters.get("from_date"), filters.get("to_date")))
	return frappe.db.sql(query)
