# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from frappe.utils import cint, cstr, flt, formatdate, get_link_to_form, getdate, nowdate, now_datetime


class POLAdvance(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		adjusted_amount: DF.Currency
		advance_amount: DF.Currency
		amended_from: DF.Link | None
		balance_amount: DF.Currency
		branch: DF.Link
		company: DF.Link | None
		cost_center: DF.Link | None
		equipment: DF.Link
		equipment_name: DF.Data | None
		for_machineries: DF.Check
		fuelbook: DF.Link | None
		is_opening: DF.Check
		journal_entry: DF.Data | None
		journal_entry_status: DF.Data | None
		od_adjusted: DF.Currency
		od_amount: DF.Currency
		od_balance: DF.Currency
		posting_date: DF.Date
		posting_time: DF.Time
		status: DF.Literal["Draft", "Paid", "Unpaid", "Cancelled"]
		supplier: DF.Link
	# end: auto-generated types
	
	def validate(self):
		self.set_status()
		self.validate_advance_amount()

	def before_save(self):
		self.validate_previous_advance()

	def on_submit(self):
		if not self.is_opening:
			self.post_journal_entry()
			# self.update_pol_advance()
		else:
			self.status = "Paid"

	def on_cancel(self):
		self.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry")

	def validate_previous_advance(self):
		if self.docstatus != 0:
			return
		
		advances = self.get_pol_advance()
		
		if advances and getdate(self.posting_date) < getdate(advances[0]['posting_date']):
			frappe.throw(f"Posting date cannot be less than {advances[0]['posting_date']}")

		# if advances and flt(advances[0]['od_balance']):
		# 	self.adjusted_amount = flt(advances[0]['od_balance'])
		# 	self.balance_amount = flt(self.balance_amount) - flt(advances[0]['od_balance'])

	def get_pol_advance(self):
		query = (
			frappe.db.sql("""
				SELECT name AS reference_name, advance_amount, balance_amount,
					posting_date, od_balance
				FROM `tabPOL Advance`
				WHERE docstatus = 1 AND equipment = %s AND fuelbook = %s AND company = %s AND name != %s
				ORDER BY posting_date, posting_time DESC
				LIMIT 1
			""", (self.equipment, self.fuelbook, self.company, self.name), as_dict=True)
		)
		
		return query
	
	def validate_advance_amount(self):
		if flt(self.balance_amount) < 0:
			frappe.throw("The balance advance amount cannot be less than 0")

	def set_status(self, status=None):
		if self.is_new():
			if self.get("amended_from"):
				self.status = "Draft"
			return

		if not status:
			if self.docstatus == 2:
				status = "Cancelled"
			elif self.docstatus == 1:
				if self.is_opening:
					status = "Paid"
				elif self.journal_entry and frappe.db.get_value(
					"Journal Entry", self.journal_entry, "docstatus"
				) == 1:
					status = "Paid"
				else:
					status = "Unpaid"

		self.status = status
				

	def update_pol_advance(self):
		advances = self.get_pol_advance()
		if advances:
			doc = frappe.get_doc("POL Advance", advances[0]['reference_name'])
			doc.od_adjusted = flt(doc.od_adjusted) + flt(advances[0]['od_balance'])
			doc.od_balance = flt(doc.od_balance) - flt(advances[0]['od_balance'])
			doc.save(ignore_permissions = True)


	def post_journal_entry(self):
		default_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		advance_account = frappe.db.get_value("Company", self.company, "pol_advance_account")

		if not default_bank_account:
			frappe.throw(
				"Default Expense Bank Account is not set for {}. Please configure it in the Branch.".format(
					frappe.get_desk_link("Branch", self.branch)
				),
				title="Missing Account"
			)

		if not advance_account:
			frappe.throw(
				"POL Advance Account is not set for {}. Please configure it in the Company.".format(
					frappe.get_desk_link("Company", self.company)
				),
				title="Missing Account"
			)

		# Posting Journal Entry
		accounts = []
		accounts.append({
			"account": advance_account,
			"debit": flt(self.advance_amount),
			"debit_in_account_currency": flt(self.advance_amount),
			"cost_center": self.cost_center,
			"party_check": 1,
			"party_type": "Supplier",
			"party": self.supplier,
			"is_advance": "Yes",
			"reference_type": self.doctype,
			"reference_name": self.name,
		})

		accounts.append({
			"account": default_bank_account,
			"credit": flt(self.advance_amount),
			"credit_in_account_currency": flt(self.advance_amount),
			"cost_center": self.cost_center,
		})

		je = frappe.new_doc("Journal Entry")
		voucher_type = "Bank Entry"
		naming_series = "Bank Payment Voucher"
		
		je.update({
				"doctype": "Journal Entry",
				"voucher_type": voucher_type,
				"naming_series": naming_series,
				"title": "POL Advance - "+self.equipment,
				"user_remark": "POL Advance - "+self.equipment,
				"posting_date": nowdate(),
				"company": self.company,
				"accounts": accounts,
				"branch": self.branch
		})

		je.save(ignore_permissions = True)
		self.db_set("journal_entry", je.name)
		self.db_set("journal_entry_status", "Forwarded to accounts for processing payment on {0}".format(now_datetime().strftime('%Y-%m-%d %H:%M:%S')))
		frappe.msgprint(_('{} posted to accounts').format(frappe.get_desk_link(je.doctype,je.name)))

def update_pol_advance_status_on_je_submit(doc, method=None):
		"""Sync POL Advance status when its linked Journal Entry is submitted/cancelled."""
		pol_advances = frappe.get_all(
			"POL Advance",
			filters={"journal_entry": doc.name, "docstatus": 1},
			pluck="name",
		)
		for name in pol_advances:
			pol = frappe.get_doc("POL Advance", name)
			pol.set_status()
			pol.db_set("status", pol.status)