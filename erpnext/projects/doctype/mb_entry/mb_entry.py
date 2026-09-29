# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, time_diff_in_hours, get_datetime, getdate, cint, get_datetime_str
from frappe.model.mapper import get_mapped_doc
from erpnext.controllers.accounts_controller import AccountsController


class MBEntry(AccountsController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.projects.doctype.mb_entry_boq.mb_entry_boq import MBEntryBOQ
		from frappe.types import DF

		amended_from: DF.Link | None
		boq: DF.Link
		boq_type: DF.Data | None
		branch: DF.Link | None
		check_all: DF.Check
		company: DF.Link | None
		cost_center: DF.Link | None
		currency: DF.Data | None
		customer: DF.Data | None
		entry_date: DF.Date
		mb_entry_boq: DF.Table[MBEntryBOQ]
		notes: DF.TextEditor | None
		party: DF.DynamicLink | None
		party_type: DF.Link | None
		project: DF.Link
		status: DF.Literal["Draft", "Invoiced", "Uninvoiced", "Cancelled"]
		subcontract: DF.Link | None
		total_balance_amount: DF.Currency
		total_entry_amount: DF.Currency
		total_invoice_amount: DF.Currency
		total_price_adjustment: DF.Currency
		total_received_amount: DF.Currency
	# end: auto-generated types
	def validate(self):
		self.set_status()
		self.default_validations()
		self.set_defaults()
			
	def on_submit(self):
		self.validate_boq_items()
		self.update_boq()
		self.make_gl_entries()

	def before_cancel(self):
		self.set_status()

	def on_cancel(self):
		self.ignore_linked_doctypes = (
			"GL Entry",
			"Payment Ledger Entry",
			"Stock Ledger Entry",
		)
		self.update_boq()
		self.make_gl_entries()
			
	def set_status(self):
		self.status = {
				"0": "Draft",
				"1": "Uninvoiced",
				"2": "Cancelled"
		}[str(self.docstatus or 0)]

	def default_validations(self):
		for rec in self.mb_entry_boq:
			#LEGACY CODE: for some reason it wasn't converting the entry rate to 2 decimal place after changing the quantity decimal value to 5. 
			# entry_amount = flt(rec.entry_quantity)*flt(rec.entry_rate)
			entry_quantity = float(rec.entry_quantity)
			#frappe.throw("entry_quantity:{}".format(entry_quantity))
			entry_rate = float(rec.entry_rate)
			#frappe.throw("entry_rate:{}".format(entry_rate))
			entry_amount = flt(entry_quantity) * flt(entry_rate)
			#frappe.throw("entry_amount:{}".format(entry_amount))
			#frappe.throw("new entry Amount:{}".format(self.entry_amount))
			
			# new = flt(rec.entry_amount,2)
			# frappe.throw("new:{}".format(new))
	
			
			# added by phuntsho on December 15. 
			#added by cety entry_rate and entry_amount 
			#entry_rate = "{:.2f}".format(rec.entry_rate)
			#entry_quantity = float("{:.2f}".format(rec.entry_quantity))
			#entry_amount = entry_quantity * float(entry_rate)
			if flt(rec.entry_quantity) > flt(rec.act_quantity):
					frappe.throw(_("Row{0}: Entry Quantity cannot be greater than Balance Quantity").format(rec.idx))
			elif flt(rec.entry_amount) > flt(rec.act_amount):
					frappe.throw(_("Row{0}: Entry Amount cannot be greater than Balance Amount").format(rec.idx))
			elif flt(rec.entry_quantity) < 0 or flt(rec.entry_amount) < 0:
					frappe.throw(_("Row{0}: Value cannot be in negative").format(rec.idx))
			'''
			else:
					if self.boq_type != "Milestone Based" and flt(rec.entry_amount,2) != flt(entry_amount,2):
							frappe.throw(_("Row{0}: Entry Amount should be {1}").format(rec.idx, flt(entry_amount)))
			'''
	
	def set_defaults(self):
		if self.project:
			base_project          = frappe.get_doc("Project", self.project)
			self.company          = base_project.company
			self.customer         = base_project.customer
			self.branch           = base_project.branch
			self.cost_center      = base_project.cost_center

			if base_project.status in ('Completed','Cancelled'):
				frappe.throw(_("Operation not permitted on already {0} Project.").format(base_project.status),title="MB Entry: Invalid Operation")
				
		if self.boq:
			base_boq              = frappe.get_doc("BOQ", self.boq)
			self.cost_center      = base_boq.cost_center
			self.branch           = base_boq.branch
			self.boq_type         = base_boq.boq_type

	def validate_boq_items(self):
		source_table = "Subcontract" if self.subcontract else "BOQ"
		source       = self.subcontract if self.subcontract else self.boq
		
		for rec in self.mb_entry_boq:
			if rec.is_selected == 1 and flt(rec.entry_amount) > 0:
				item = frappe.db.sql("""
					select
							ifnull(balance_quantity,0) as balance_quantity,
							ifnull(balance_amount,0) as balance_amount
					from
							`tab{1} Item`
					where   name = '{0}'
					""".format(rec.boq_item_name, source_table), as_dict=1)[0]

				if (flt(rec.entry_quantity) > flt(item.balance_quantity)) or \
					(flt(rec.entry_amount) > flt(item.balance_amount)):
						frappe.throw(_('Row{0}: Insufficient Balance. Please refer to {1}# <a href="#Form/{1}/{2}">{2}</a>').format(rec.idx, source_table,source))

	def update_boq(self):
		source_table = "Subcontract" if self.subcontract else "BOQ"
		source       = self.subcontract if self.subcontract else self.boq

		# Updating `tabBOQ Item`
		boq_list = frappe.db.sql("""
			select
					meb.boq_item_name,
					sum(
							case
							when '{0}' = 'Milestone Based' then 0
							else
									case
									when meb.docstatus < 2 then ifnull(meb.entry_quantity,0)
									else -1*ifnull(meb.entry_quantity,0)
									end
							end
					) as entry_quantity,
					sum(
							case
							when meb.docstatus < 2 then ifnull(meb.entry_amount,0)
							else -1*ifnull(meb.entry_amount,0)
							end
					) as entry_amount
			from  `tabMB Entry BOQ` as meb
			where meb.parent        = '{1}'
			and   meb.is_selected   = 1
			group by meb.boq_item_name
			""".format(self.boq_type, self.name), as_dict=1)

		for item in boq_list:
			frappe.db.sql("""
				update `tab{3} Item`
				set
						booked_quantity  = ifnull(booked_quantity,0) + ifnull({1},0),
						booked_amount    = ifnull(booked_amount,0) + ifnull({2},0),
						balance_quantity = ifnull(balance_quantity,0) - ifnull({1},0),
						balance_amount   = ifnull(balance_amount,0) - ifnull({2},0)
				where name = '{0}'
				""".format(item.boq_item_name, flt(item.entry_quantity), flt(item.entry_amount), source_table))

	#added by cety on 8/19/2021             
	def make_gl_entries(self):
		if self.total_entry_amount:
			from erpnext.accounts.general_ledger import make_gl_entries
			gl_entries = []
			self.posting_date = self.entry_date

			if self.party_type == "Customer":
				# inv_gl = frappe.db.get_value(doctype="Projects Accounts Settings",fieldname="project_invoice_account")
				# rec_gl = frappe.db.get_value(doctype="Company",filters=self.company,fieldname="default_receivable_account")
				inv_gl = frappe.db.get_value(doctype="Projects Accounts Settings",fieldname="project_accrued_income_account")
				rec_gl = frappe.db.get_value(doctype="Projects Accounts Settings",fieldname="project_invoice_account")
			elif self.party_type == "Supplier":
				# inv_gl = frappe.db.get_value(doctype="Projects Accounts Settings",fieldname="invoice_account_supplier")
				# rec_gl = frappe.db.get_value(doctype="Company",filters=self.company,fieldname="default_payable_account")
				inv_gl = frappe.db.get_value(doctype="Projects Accounts Settings",fieldname="invoice_account_supplier")
				rec_gl = frappe.db.get_value(doctype="Company",filters=self.company,fieldname="default_payable_account")
			else:
				inv_gl = frappe.db.get_value(doctype="Projects Accounts Settings",fieldname="invoice_account_internal")
				rec_gl = frappe.db.get_value(doctype="Company",filters=self.company,fieldname="default_receivable_account")

			if not inv_gl:
				frappe.throw(_("Project Invoice Account is not defined in Projects Accounts Settings."))

			if not rec_gl:
				frappe.throw(_("Default Receivable Account is not defined in Company Settings."))
			
			gl_entries.append(
				self.get_gl_dict({
					"account":  inv_gl,
					"party_type": self.party_type,
					"party": self.party,
					"against": rec_gl,
					"credit" if self.party_type == "Supplier" else "debit": self.total_entry_amount,
					"credit_in_account_currency" if self.party_type == "Supplier" else "debit_in_account_currency": self.total_entry_amount,
					"against_voucher": self.name,
					"against_voucher_type": self.doctype,
					"project": self.project,
					"cost_center": self.cost_center
				}, self.currency)
			)

			gl_entries.append(
				self.get_gl_dict({
					"account":  rec_gl,
					"against": self.party,
					"debit" if self.party_type == "Supplier" else "credit": self.total_entry_amount,
					"debit_in_account_currency" if self.party_type == "Supplier" else "credit_in_account_currency": self.total_entry_amount,
					"project": self.project,
					"cost_center": self.cost_center,
					"party_type": self.party_type if self.party_type == "Supplier" else "",
					"party": self.party if self.party_type == "Supplier" else ""
				}, self.currency)
			)
			make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)
	#end

@frappe.whitelist()
def make_mb_invoice(source_name, target_doc=None):
	def update_master(source_doc, target_doc, source_partent):
		#target_doc.project = source_doc.project
		target_doc.invoice_title = str(target_doc.project) + "(Project Invoice)"
		target_doc.reference_doctype = "MB Entry"
		target_doc.reference_name    = source_doc.name

	def update_reference(source_doc, target_doc, source_parent):
		pass
			
	doclist = get_mapped_doc("MB Entry", source_name, {
		"MB Entry": {
			"doctype": "Project Invoice",
			"field_map":{
				"project": "project",
				"branch": "branch",
				"customer": "customer"
			},
			"postprocess": update_master
		},
	}, target_doc)
	
	return doclist