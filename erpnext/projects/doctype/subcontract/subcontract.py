# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.model.naming import make_autoname
from frappe.utils import cstr, flt, getdate, today, nowdate, now_datetime


class Subcontract(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.projects.doctype.subcontract_history_item.subcontract_history_item import SubcontractHistoryItem
		from erpnext.projects.doctype.subcontract_item.subcontract_item import SubcontractItem
		from frappe.types import DF

		amended_from: DF.Link | None
		balance_amount: DF.Currency
		boq: DF.Link
		boq_date: DF.Date
		boq_history_item: DF.Table[SubcontractHistoryItem]
		boq_item: DF.Table[SubcontractItem]
		boq_type: DF.Literal["Item Based", "Milestone Based", "Piece Rate Work Based(PRW)"]
		branch: DF.Link | None
		claimed_amount: DF.Currency
		company: DF.Link | None
		cost_center: DF.Link | None
		notes: DF.TextEditor | None
		paid_amount: DF.Currency
		party: DF.DynamicLink
		party_type: DF.Link
		price_adjustment: DF.Currency
		project: DF.Link
		received_amount: DF.Currency
		remarks: DF.Data | None
		total_amount: DF.Currency
	# end: auto-generated types
	
	def validate(self):
		self.update_defaults()
		self.validate_defaults()
		self.update_boq_history()

	def on_submit(self):
		#self.update_project_value()
		self.update_boq()

	def on_cancel(self):
		#self.update_project_value()
		self.update_boq()

	def update_boq(self):
		factor = 1 if self.docstatus < 2 else -1
		for i in self.boq_item:
			if i.is_selected and flt(i.amount) and i.boq_item_name:
				doc = frappe.get_doc("BOQ Item", i.boq_item_name)
				if not doc.is_group:
					current_quantity = flt(doc.subcontract_quantity)
					current_amount   = flt(doc.subcontract_amount)
					new_quantity     = flt(current_quantity)+(factor*flt(0 if self.boq_type == "Milestone Based" else i.quantity))
					new_amount       = flt(current_amount)+(factor*flt(i.amount))
					new_rate         = new_amount / (new_quantity if flt(new_quantity) else 1)
					doc.subcontract_quantity = new_quantity if flt(new_quantity) > 0 else 0
					doc.subcontract_rate     = new_rate if flt(new_rate) > 0 else 0
					doc.subcontract_amount   = new_amount if flt(new_amount) > 0 else 0
					doc.save(ignore_permissions=True)

	def update_boq_history(self):
		# removing entries which are copied via "Duplicate" option
		for i in self.boq_history_item:
			if i.transaction_type != self.doctype or (i.transaction_name and i.transaction_name != self.name):
				self.remove(i)

		# make entry in history for the current BOQ if it doesn't already exist, else update the details
		if not self.boq_history_item:
			self.append("boq_history_item",{
					"transaction_type": self.doctype,
					"transaction_date": self.boq_date,
					"initial_amount": flt(self.total_amount),
					"adjustment_amount": 0,
					"final_amount": flt(self.total_amount),
					"owner": frappe.session.user,
					"creation": now_datetime(),
					"modified_by": frappe.session.user,
					"modified": now_datetime()
			})
		else:
			for i in self.boq_history_item:
				if i.transaction_type == self.doctype:
					i.transaction_name  = self.name
					i.transaction_date  = self.boq_date
					i.initial_amount    = flt(self.total_amount)
					i.adjustment_amount = 0
					i.final_amount      = flt(self.total_amount)

	def validate_defaults(self):
		if not self.project:
			frappe.throw("`Project` cannot be null.")
				
		if not self.branch:
			frappe.throw("`Branch` cannot be null.")

		if not self.cost_center:
			frappe.throw("`Cost Center` cannot be null.")

		if flt(self.total_amount,0) <= 0:
			frappe.throw(_("<b>Total Amount(A)</b> should be greater than zero"), title="Invalid Data")

	def update_defaults(self):
		item_group = ""
		self.total_amount     = 0.0
		self.price_adjustment = 0.0
		self.claimed_amount   = 0.0
		self.received_amount  = 0.0
		self.balance_amount   = 0.0

		for item in self.boq_item:
			if item.is_group:
				item_group              = item.item
				item.quantity           = 0.0
				item.rate               = 0.0
				item.amount             = 0.0
				item.claimed_quantity   = 0.0
				item.claimed_amount     = 0.0
				item.booked_quantity    = 0.0
				item.booked_amount      = 0.0
				item.balance_quantity   = 0.0
				item.balance_amount     = 0.0
			else:
				item.amount           = flt(item.quantity)*flt(item.rate)
				item.claimed_quantity = 0.0
				item.claimed_amount   = 0.0
				item.booked_quantity  = 0.0
				item.booked_amount    = 0.0
				item.balance_quantity = flt(item.quantity)
				item.balance_rate     = flt(item.rate)
				item.balance_amount   = flt(item.amount)

				if item.is_selected and flt(item.amount):
					self.total_amount    += flt(item.amount)
					self.balance_amount  += flt(item.amount)

			item.parent_item = item_group

			if flt(item.quantity) < 0:
					frappe.throw(_("Row#{0} : Invalid quantity"),title="Invalid Data")
			elif flt(item.rate) < 0:
					frappe.throw(_("Row#{0} : Invalid rate"),title="Invalid Data")
			elif flt(item.amount) < 0:
					frappe.throw(_("Row#{0} : Invalid amount"),title="Invalid Data")
				
						
		# Defaults
		base_project = frappe.get_doc("Project", self.project)
		
		if base_project.status in ('Completed','Cancelled'):
			frappe.throw(_("Operation not permitted on already {0} Project.").format(base_project.status),title="BOQ: Invalid Operation")
						
		if not self.branch:
			self.branch = base_project.branch

		if not self.cost_center:
			self.cost_center = base_project.cost_center

		if not self.boq_date:
			self.boq_date = today()

	def update_project_value(self):
		if self.total_amount:
			pro_doc = frappe.get_doc("Project", self.project)
			pro_doc.flags.dont_sync_tasks = True
			pro_doc.project_value = flt(pro_doc.project_value)+(-1*(self.total_amount) if self.docstatus==2 else flt(self.total_amount))
			pro_doc.save(ignore_permissions = True)

@frappe.whitelist()
def make_subcontract_adjustment(source_name, target_doc=None):
	def update_master(source_doc, target_doc, source_parent):
		target_doc.total_amount = 0.0
			
	def update_item(source_doc, target_doc, source_parent):
		target_doc.balance_rate         = flt(source_doc.balance_rate) if flt(source_doc.balance_rate) else flt(source_doc.rate)
		target_doc.balance_quantity_adj = flt(target_doc.balance_quantity)
		target_doc.balance_rate_adj     = flt(target_doc.balance_rate)
		target_doc.balance_amount_adj   = flt(target_doc.balance_amount)
		target_doc.adjustment_quantity  = 0
		target_doc.adjustment_rate      = 0
		target_doc.adjustment_amount    = 0
			
	doclist = get_mapped_doc("Subcontract", source_name, {
		"Subcontract": {
			"doctype": "Subcontract Adjustment",
			"field_map": {
				"name": "subcontract",
				"boq_date": "subcontract_date"
			},
			"postprocess": update_master
		},

		"Subcontract Item": {
			"doctype": "Subcontract Adjustment Item",
			"field_map": {
				"name": "boq_item_name",
				"balance_rate": "balance_rate",
			},
			"postprocess": update_item
		}
	}, target_doc)

	return doclist

@frappe.whitelist()
def make_direct_invoice(source_name, target_doc=None):
	def update_master(source_doc, target_doc, source_parent):
		#target_doc.invoice_title = str(source_doc.project) + "(Project Invoice)"
		target_doc.invoice_title = "Project Invoice ( {0} )".format(frappe.db.get_value("Project", source_doc.project, "project_name"))
		target_doc.invoice_type = "Direct Invoice"
		target_doc.check_all = 1
			
	def update_item(source_doc, target_doc, source_parent):
		target_doc.subcontract  = source_doc.parent
		target_doc.invoice_rate = flt(source_doc.balance_rate) if flt(source_doc.balance_rate) else flt(source_doc.rate)
		target_doc.act_quantity = flt(target_doc.invoice_quantity)
		target_doc.act_rate     = flt(target_doc.invoice_rate)
		target_doc.act_amount   = flt(target_doc.invoice_amount)
		target_doc.original_rate= flt(target_doc.invoice_rate)
			
	doclist = get_mapped_doc("Subcontract", source_name, {
		"Subcontract": {
			"doctype": "Project Invoice",
			"field_map": {
				"project": "project",
				"name": "subcontract"
			},
			"postprocess": update_master
		},

		"Subcontract Item": {
			"doctype": "Project Invoice BOQ",
			"field_map": {
				"name": "boq_item_name",
				"balance_quantity": "invoice_quantity",
				"balance_rate": "invoice_rate",
				"balance_amount": "invoice_amount",
				"quantity": "original_quantity",
				"amount": "original_amount"
			},
			"postprocess": update_item
		}
	}, target_doc)

	return doclist

@frappe.whitelist()
def make_mb_invoice(source_name, target_doc=None):
	def update_master(source_doc, target_doc, source_parent):
		#target_doc.invoice_title = str(target_doc.project) + " (Project Invoice)"
		target_doc.invoice_title = "Project Invoice ( {0} )".format(frappe.db.get_value("Project", source_doc.project, "project_name"))
		target_doc.invoice_type = "MB Based Invoice"
		target_doc.check_all_mb = 1
			
	doclist = get_mapped_doc("Subcontract", source_name, {
		"Subcontract": {
			"doctype": "Project Invoice",
			"field_map": {
				"project": "project"
			},
			"postprocess": update_master
		}
	}, target_doc)

	return doclist

@frappe.whitelist()
def make_book_entry(source_name, target_doc=None):
	def update_master(source_doc, target_doc, source_parent):
		target_doc.check_all = 1
			
	def update_item(source_doc, target_doc, source_parent):
		target_doc.entry_rate   = flt(source_doc.balance_rate) if flt(source_doc.balance_rate) else flt(source_doc.rate)
		target_doc.act_quantity = flt(target_doc.entry_quantity)
		target_doc.act_rate     = flt(target_doc.entry_rate)
		target_doc.act_amount   = flt(target_doc.entry_amount)
		target_doc.original_rate= flt(target_doc.entry_rate)
			
	doclist = get_mapped_doc("Subcontract", source_name, {
		"Subcontract": {
			"doctype": "MB Entry",
			"field_map": {
				"project": "project",
				"name": "subcontract"
			},
			"postprocess": update_master
		},

		"Subcontract Item": {
			"doctype": "MB Entry BOQ",
			"field_map": {
				"name": "boq_item_name",
				"balance_quantity": "entry_quantity",
				"balance_rate": "entry_rate",
				"balance_amount": "entry_amount",
				"quantity": "original_quantity",
				"amount": "original_amount"
			},
			"postprocess": update_item
		}
	}, target_doc)

	return doclist

@frappe.whitelist()
def make_subcontract_advance(source_name, target_doc=None):
	def update_master(source_doc, target_doc, source_partent):
		#target_doc.customer = source_doc.customer
		pass
	
	doclist = get_mapped_doc("Subcontract", source_name, {
		"Subcontract": {
			"doctype": "Project Advance",
			"field_map":{
				"project": "project",
				"party_type": "party_type",
				"party": "party",
				"party_address": "party_address"
			},
			"postprocess": update_master
		}
	}, target_doc)
	return doclist
