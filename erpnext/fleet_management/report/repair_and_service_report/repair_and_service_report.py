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
		# ("Equipment Type") + ":data:120",
		# ("Equipment No")+":data:100",
		("Branch")+":Link/Branch:150",
		("Posting Date") + ":date:120",
		("Party Type") + ":data:120",
		("Party")+":Dynamic Link/party_type:150",
		("Total Out Source Amount")+":Currency:150",
		("Total Amount")+ ":Currency:80",
		("Total Stock Amount")+ ":Currency:80",
		("Company")+ ":link/Company:80",
	]

def get_data(filters):
	query ="""select ras.equipment, ras.branch, ras.posting_date, ras.party_type, ras.party, ras.total_out_source_amt, ras.total_amount, ras.total_stock_amt, ras.company FROM `tabHire Invoice Details` AS hid, `tabRepair And Services` AS ras, `tabHire Charge Invoice` AS hci, `tabEquipment` e,  `tabVehicle Logbook` vl   WHERE hid.parent = hci.name AND hid.vehicle_logbook = vl.name and hid.equipment = e.name and hci.docstatus = 1 and ((vl.from_date between '{0}' and '{1}') or (vl.to_date between '{0}' and '{1}'))""".format(filters.get("from_date"), filters.get("to_date"))

	if filters.get("branch"):
		query += " and ras.branch = \'" + str(filters.branch) + "\'"


	if filters.get("customer"):
		query += " and hci.customer = \'" + str(filters.customer) + "\'"
	query += " group by hid.equipment, hci.ehf_name"
	#frappe.msgprint("{0}, {1}".format(filters.get("from_date"), filters.get("to_date")))
	return frappe.db.sql(query)

