# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
	NA		  	NORBU		    NOV/03/2020       User now allocate the amount manually rather than automatic like before. 
		  
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, get_datetime
# from frappe.utils import flt, comma_or, nowdate, getdate,
from erpnext.custom_utils import prepare_gl, check_future_date
from frappe.model.mapper import get_mapped_doc
from erpnext.controllers.stock_controller import StockController

class HSDPayment(StockController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.fleet_management.doctype.hsd_payment_item.hsd_payment_item import HSDPaymentItem
		from frappe.types import DF

		actual_amount: DF.Currency
		amended_from: DF.Link | None
		amount: DF.Currency
		approver: DF.Link | None
		assign_from_cheque_lot: DF.Check
		bank_account: DF.Link
		bank_payment: DF.Data | None
		branch: DF.Link
		cheque__no: DF.Data | None
		cheque_date: DF.Date | None
		cheque_lot: DF.Link | None
		clearance_date: DF.Date | None
		company: DF.Link
		cost_center: DF.Link
		final_settlement: DF.Check
		fuelbook: DF.Link
		items: DF.Table[HSDPaymentItem]
		payment_status: DF.Data | None
		posting_date: DF.Date
		remarks: DF.SmallText | None
		status: DF.Literal["Draft", "Submitted", "Cancelled"]
		supplier: DF.Link
		verifier: DF.Link | None
	# end: auto-generated types
	def validate(self):
		check_future_date(self.posting_date)
		self.set_status()
		self.validate_allocated_amount()
		self.clearance_date = None
		# if self.workflow_state=="Verified":
		self.verifier=frappe.session.user

	def set_status(self):
                self.status = {
                        "0": "Draft",
                        "1": "Submitted",
                        "2": "Cancelled"
                }[str(self.docstatus or 0)]

	def validate_allocated_amount(self):
		# Code added by phuntsho on nov 3 2020
		# Manual amount allocation given the previous automatic method didn't allow users to select individual payment. 
		total = 0 
		to_remove = []
		for d in self.items:
			if not total > self.actual_amount:  
				if not d.allocated_amount > 0: 
					to_remove.append(d)
				else:  
					total += d.allocated_amount

				d.balance_amount = d.payable_amount - d.allocated_amount
			else: 
				frappe.throw("Total amount cannot be greater than actual amount")

		self.amount = total
		[self.remove(d) for d in to_remove]
		# --------- end of code --------

		# --------- legacy code -----------
		# if not self.amount > 0:
		# 	frappe.throw("Amount should be greater than 0")	
		# total = flt(self.amount)
		# to_remove = []

		# for d in self.items:
		# 	allocated = 0
		# 	if total > 0 and total >= d.payable_amount:
		# 		allocated = d.payable_amount
		# 	elif total > 0 and total < d.payable_amount:
		# 		allocated = total
		# 	else:
		# 		allocated = 0
		# 		to_remove.append(d)		

		# 	d.allocated_amount = allocated
		# 	d.balance_amount = d.payable_amount - allocated
		# 	total-=allocated

		# [self.remove(d) for d in to_remove]
		# ----------- end of legacy code ------------

	def on_submit(self):
		self.adjust_outstanding()
		self.update_general_ledger()
		self.approver=self.verifier=frappe.session.user

	def on_cancel(self):
		self.ignore_linked_doctypes = (
			"GL Entry",
			"Stock Ledger Entry",
			"Payment Ledger Entry",
			"Repost Payment Ledger",
			"Repost Payment Ledger Items",
			"Repost Accounting Ledger",
			"Repost Accounting Ledger Items",
			"Unreconcile Payment",
			"Unreconcile Payment Entries",
			"Advance Payment Ledger Entry",
		)
		super().on_cancel()
		if self.clearance_date:
                        frappe.throw("Already done bank reconciliation.")

		self.adjust_outstanding(cancel=True)
		self.update_general_ledger()
	
	def adjust_outstanding(self, cancel=False):
		for a in self.items:
			doc = frappe.get_doc("POL Receive", a.pol)
			if doc:
				if doc.docstatus != 1:
					frappe.throw("<b>"+ str(doc.name) +"</b> is not a submitted Issue POL Transaction")
				if cancel:
					doc.db_set("paid_amount", flt(doc.paid_amount) - flt(a.allocated_amount))
					doc.db_set("outstanding_amount", flt(doc.outstanding_amount) + flt(a.allocated_amount))	
				else:
					paid_amount = round(flt(doc.paid_amount) + flt(a.allocated_amount), 2)
					if flt(paid_amount) > flt(doc.total_amount,2):
						frappe.throw("Paid Amount cannot be greater than the Total Amount for Receive POl <b>"+str(a.pol)+"</b>")
					doc.db_set("paid_amount", paid_amount)
					doc.db_set("outstanding_amount", a.balance_amount)	


	def update_general_ledger(self):
		gl_entries = []
		
		creditor_account = frappe.db.get_value("Company", self.company, "default_payable_account")
		if not creditor_account:
			frappe.throw("Set Default Payable Account in Company")
		# frappe.throw(frappe.as_json(self))
		if self.final_settlement ==1:
			gl_entries.append(
				prepare_gl(self, {"account": self.bank_account,
					 "credit": flt(self.amount),
					 "credit_in_account_currency": flt(self.amount),
					 "cost_center": self.cost_center,
					"party_type": "Supplier",
                                         "party": self.supplier,
					})
			)
		else:
			gl_entries.append(
                                prepare_gl(self, {"account": self.bank_account,
                                         "credit": flt(self.amount),
                                         "credit_in_account_currency": flt(self.amount),
                                         "cost_center": self.cost_center,
                                        })
                        )
		# frappe.throw(frappe.as_json(self))
		gl_entries.append(
			prepare_gl(self, {"account": creditor_account,
					 "debit": flt(self.amount),
					 "debit_in_account_currency": flt(self.amount),
					 "cost_center": self.cost_center,
					 "party_type": "Supplier",
					 "party": self.supplier,
					})
			)

		from erpnext.accounts.general_ledger import make_gl_entries
		# frappe.throw(str(gl_entries))
		make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=False)
  
	# @frappe.whitelist()
	# def get_invoices(self):
	# 	if not self.fuelbook:
	# 		frappe.throw("Select a Fuelbook to Proceed")
	# 	query = "select name as pol, pol_type as pol_item_code, outstanding_amount as payable_amount, item_name, memo_number from `tabPOL Receive` where docstatus = 1 and outstanding_amount > 0 and fuelbook = %s and is_opening =! Yes order by posting_date, posting_time"
	# 	entries = frappe.db.sql(query, self.fuelbook, as_dict=True)
	# 	self.set('items', [])

	# 	total_amount = 0
	# 	for d in entries:
	# 		total_amount+=flt(d.payable_amount)
	# 		d.allocated_amount = d.payable_amount
	# 		d.balance_amount = 0
	# 		row = self.append('items', {})
	# 		row.update(d)
	# 	self.amount = total_amount
	# 	self.actual_amount = total_amount

	@frappe.whitelist()
	def get_invoices(self):
		# Check if fuelbook is selected
		if not self.fuelbook:
			frappe.throw("Select a Fuelbook to Proceed")

		# SQL query to fetch POL Receive entries
		query = """
			SELECT 
				name AS pol, 
				pol_type AS pol_item_code, 
				outstanding_amount AS payable_amount, 
				item_name, 
				memo_number 
			FROM 
				`tabPOL Receive` 
			WHERE 
				docstatus = 1 
				AND outstanding_amount > 0 
				AND fuelbook = %s 
				AND is_opening != 'Yes' 
			ORDER BY 
				posting_date, 
				posting_time
		"""

		# Execute the query
		entries = frappe.db.sql(query, self.fuelbook, as_dict=True)

		# Clear existing items in the child table
		self.set('items', [])

		# Initialize total amount
		total_amount = 0

		# Process each entry
		for d in entries:
			total_amount += flt(d.payable_amount)
			d.allocated_amount = d.payable_amount
			d.balance_amount = 0

			# Append the entry to the child table
			row = self.append('items', {})
			row.update(d)

		# Update total amount and actual amount
		self.amount = total_amount
		self.actual_amount = total_amount	
  
  
  
	# ePayment Begins
@frappe.whitelist()
def make_bank_payment(source_name, target_doc=None):
    def set_missing_values(obj, target, source_parent):
        target.payment_type = None
        target.transaction_type = "HSD Payment"
        target.posting_date = get_datetime()
        target.from_date = None
        target.payment_type ="One-One Payment"
        target.to_date = None

    doc = get_mapped_doc("HSD Payment", source_name, {
            "HSD Payment": {
                "doctype": "Bank Payment",
                "field_map": {
                    "name": "transaction_no",
                    "bank_account": "paid_from"
                },
                "postprocess": set_missing_values,
            },
    }, target_doc, ignore_permissions=True)
    return doc
# ePayment Ends