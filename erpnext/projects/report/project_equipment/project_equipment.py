from __future__ import unicode_literals
import frappe
from datetime import datetime
import time
from frappe import _, json
from frappe.utils import flt, cint
from frappe.utils.data import get_last_day
from frappe.utils.data import flt, cint,add_days, cstr, flt, getdate, nowdate, rounded, date_diff

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	cond1 = cond2 = " and 1=1"
	if filters.get("project"):
			br = frappe.db.get_value("Project", filters.get("project"), "branch")
		#frappe.msgprint("{0}".format(br))
			cond1 += " and e.branch = '{0}' and p.name = '{1}'".format(br, filters.get("project"))
			cond2 += " and h.customer_branch = '{0}' and p.name = '{1}'".format(br, filters.get("project"))

	if filters.get("from_date") and filters.get("to_date"):

		cond1 += " and  ((p.expected_start_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\') \
				 or (p.expected_end_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'))" 

		cond2 += " and ((hd.from_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\') \
			 or (hd.to_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'))"

	data  =  frappe.db.sql(""" select distinct p.name as p_name, p.branch as p_branch, e.name as e_name, 
				e.equipment_number as e_no, e.branch as e_branch,
                                p.expected_start_date as from_date, p.expected_end_date as end_date,
                                '' as rate, '' as idle_rate
                                from tabEquipment e, `tabProject` p
                                where e.branch = p.branch {0}
                                union all
                                select distinct p.name as p_name, p.branch as p_branch,
                                hd.equipment as e_name, hd.equipment_number as e_no, e.branch as e_branch,
                                hd.from_date as from_date, hd.to_date  as to_date,
                                hd.rate as rate, hd.idle_rate as idle_rate
                                from `tabEquipment Hiring Form` as h, `tabHiring Approval Details` hd, `tabProject` p, `tabEquipment` e
                                where h.name = hd.parent and  e.name = hd.equipment and
                                h.customer_branch = p.branch {1} and h.docstatus = 1 order by from_date, e_name
                                """.format(cond1, cond2))
	return data

def get_columns(filters):
	cols = [
		("Project Name") + ":Link/Project:120",
        	("Project Branch") + ":Data:120",
		("Equipment Name") + ":Link/Equipment:120",
		("Equipment Number") + ":Data:120",
		("Equipment Branch") + ":Data:120",
		("From") + ":Date:120",
		("To") + ":Date:120",
		("Rate") + ":Currency:120",
		("Idle Rate") + ":Currency:120",
	]
	return cols