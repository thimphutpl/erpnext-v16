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
		("Insurance For") + ":data:120",
		("Posting Date")+":data:100",
		("Cost Center")+":Link/Cost Center:150",
		("Branch") + ":link/Branch:120",
		("Party") + ":link/Supplier:120",
		("Insured Date")+":date:80",
		("Insurance Type")+":Data:150",
		("Type")+":Data:150",
		("Policy Number")+":data:80",
		("Due Date")+":date:150",
		("Validity")+":date:150",
		("Total Amount")+ ":Data:80",
		("Company") + ":link/Company:120",
	]

def get_data(filters):
	query ="""select inr.equipment, inr.insurance_for, inr.posting_date, inr.cost_center, inr.branch, id.party, id.insured_date, id.insurance_type, id.type, id.policy_number, id.due_date, id.validity, id.total_amount, inr.company
    FROM `tabInsurance and Registration` AS inr, `tabInsurance Details` AS id, `tabHire Invoice Details` AS hid, `tabHire Charge Invoice` AS hci, `tabEquipment` e,  `tabVehicle Logbook` vl   WHERE hid.parent = hci.name AND hid.vehicle_logbook = vl.name and hid.equipment = e.name and hci.docstatus = 1 and ((vl.from_date between '{0}' and '{1}') or (vl.to_date between '{0}' and '{1}'))""".format(filters.get("from_date"), filters.get("to_date"))

	if filters.get("branch"):
		query += " and inr.branch = \'" + str(filters.branch) + "\'"
		
	if filters.get("customer"):
		query += " and hci.customer = \'" + str(filters.customer) + "\'"
	query += " group by hid.equipment, hci.ehf_name"
	#frappe.msgprint("{0}, {1}".format(filters.get("from_date"), filters.get("to_date")))
	return frappe.db.sql(query)







