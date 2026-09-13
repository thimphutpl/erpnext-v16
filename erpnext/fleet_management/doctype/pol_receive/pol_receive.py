# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, qb, throw
from frappe.utils import flt, cint, cstr, fmt_money, formatdate, nowtime, getdate
from erpnext.custom_utils import check_future_date
from erpnext.controllers.stock_controller import StockController
from erpnext.accounts.general_ledger import (
   get_round_off_account_and_cost_center,
   make_gl_entries,
   make_reverse_gl_entries,
   merge_similar_entries,
)
from erpnext.accounts.party import get_party_account


from erpnext.accounts.utils import get_fiscal_year
from erpnext.custom_utils import check_future_date, get_branch_cc, prepare_gl, prepare_sl, check_budget_available


class POLReceive(StockController):
   # begin: auto-generated types
   # This code is auto-generated. Do not modify anything in this block.


   from typing import TYPE_CHECKING


   if TYPE_CHECKING:
	   from erpnext.fleet_management.doctype.pol_receive_advance.pol_receive_advance import POLReceiveAdvance
	   from erpnext.fleet_management.doctype.pol_receive_item.pol_receive_item import POLReceiveItem
	   from frappe.types import DF


	   advances: DF.Table[POLReceiveAdvance]
	   amended_from: DF.Link | None
	   branch: DF.Link
	   company: DF.Link
	   cost_center: DF.Link | None
	   current_km: DF.Float
	   equipment: DF.Link
	   equipment_category: DF.Link | None
	   equipment_name: DF.Data | None
	   for_machineries: DF.Check
	   fuel_type: DF.Link
	   fuelbook: DF.Link | None
	   item_name: DF.Data | None
	   items: DF.Table[POLReceiveItem]
	   jv: DF.Data | None
	   km_difference: DF.Float
	   mileage: DF.Float
	   od_amount: DF.Currency
	   posting_date: DF.Date
	   posting_time: DF.Time | None
	   previous_km: DF.Float
	   remarks: DF.SmallText | None
	   supplier: DF.Link
	   total_allocated_amount: DF.Currency
	   total_amount: DF.Currency
	   total_qty: DF.Float
	   uom: DF.Link | None
   # end: auto-generated types


   def validate(self):
	   check_future_date(self.posting_date)
	   self.validate_advance()
	   self.set_allocated_amount()

   def on_submit(self):
	   self.update_pol_advance()
	   self.make_gl_entries()
	   # if not self.is_opening:
	   #   self.post_journal_entry()
	   #   self.update_pol_advance()
	   # else:
	   #   self.status = "Paid"
	  
   #Cancel
   def on_cancel(self):
	   self.update_pol_advance(cancel=True)
	   self.make_gl_entries(cancel=True)
	   self.ignore_linked_doctypes = (
			"GL Entry",
			"Payment Ledger Entry",
			"Stock Ledger Entry",
			"Repost Item Valuation",
			"Serial and Batch Bundle",
		)

   def make_gl_entries(self, cancel=False):
	   gl_entries = self.get_gl_entries()
	   if gl_entries:
		   make_gl_entries(
			 gl_entries,
			 cancel=cancel,
			 update_outstanding="No",   # since you're using advances, not payment ledger
		 )        


   def before_save(self):
	   if not self.advances:
		   frappe.throw("Advanced for POL is needed for the equipment", self.equipment)   

   def validate_advance(self):
	   if not self.get('advances'):
		   frappe.throw("POL Advance not found for select branch and equipment")
		
	   valid_advances = [
		   d for d in self.advances
		   if flt(d.balance_amount) > 0
	   ]

	   if not valid_advances:
		   frappe.throw("Balance amount must be greater than zero")
			
   def update_pol_advance(self, cancel=False):
	   for adv in self.advances:
		   allocated_amount = 0.0
		   if flt(adv.allocated_amount) > 0:
			   if flt(adv.balance_amount) < flt(adv.allocated_amount) and self.docstatus < 2:
				   frappe.throw(_("Advance#{0} : Allocated amount Nu. {1}/- cannot be more than Advance Balance Nu. {2}/-").format(adv.reference_name, "{:,.2f}".format(flt(adv.allocated_amount)),"{:,.2f}".format(flt(adv.balance_amount))))
			   else:
				   allocated_amount = -1 * flt(adv.allocated_amount) if cancel else flt(adv.allocated_amount)


				   adv_doc = frappe.get_doc("POL Advance", adv.reference_name)
				   adv_doc.adjusted_amount = flt(adv_doc.adjusted_amount) + flt(allocated_amount)
				   adv_doc.balance_amount    = flt(adv_doc.balance_amount) - flt(allocated_amount)
				   adv_doc.save(ignore_permissions = True)
	  
	   if flt(self.od_amount):
		   for d in self.get('advances'):
			   od = -1 * flt(self.od_amount) if cancel else flt(self.od_amount)
			   doc = frappe.get_doc("POL Advance", d.reference_name)
			   doc.od_amount = flt(doc.od_amount) + flt(od)
			   doc.od_balance = flt(doc.od_balance) + flt(od)
			   doc.save(ignore_permissions = True)


   def set_allocated_amount(self):
	   total_allocated = 0.0
	   if flt(self.total_amount):
		   allocated_amount = flt(self.total_amount)
		   for d in self.get("advances"):
			   if d.balance_amount >= allocated_amount:
				   d.allocated_amount = allocated_amount
				   total_allocated += flt(d.allocated_amount)
				   allocated_amount = 0
			   elif d.balance_amount < allocated_amount:
				   d.allocated_amount = d.balance_amount
				   total_allocated += flt(d.allocated_amount)
				   allocated_amount = flt(allocated_amount) - flt(d.balance_amount)


	   self.total_allocated_amount = flt(total_allocated)
	   if flt(self.total_amount) > flt(self.total_allocated_amount):
		   self.od_amount = flt(self.total_amount) - flt(self.total_allocated_amount)


   # Ver 2.0.190509, Following method created by SHIV on 2019/05/24
   def get_gl_entries(self):
	   gl_entries = []


	   # creditor_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_pol_advance_account")
	   creditor_account = frappe.db.get_value("Company", self.company, "pol_advance_account")
	   if not creditor_account:
		   frappe.throw("Set Default Payable Account in Company")


	   # expense_account = self.get_expense_account()
	   expense_account = frappe.db.get_value("Equipment Category", self.equipment_category, "pol_advance_account")
	   if not expense_account:
		   frappe.throw("Set Default expense Account in equipment category")



	   # if self.hiring_cost_center:
	   #     cost_center = self.hiring_cost_center
	   # else:
	   # cost_center = get_branch_cc(self.vehicle_branch)


	   # ba = get_equipment_ba(self.vehicle)
	   # default_ba = get_default_ba()


	   gl_entries.append(
		   prepare_gl(self, {"account": expense_account,
			   "debit": flt(self.total_amount),
			   "debit_in_account_currency": flt(self.total_amount),
			   "cost_center": self.cost_center,
			   # "business_activity": ba
			   })
	   )


	   gl_entries.append(
		   prepare_gl(self, {"account": creditor_account,
			   "credit": flt(self.total_amount),
			   "credit_in_account_currency": flt(self.total_amount),
			   "cost_center": self.cost_center,
			   "party_type": "Supplier",
			   "party": self.supplier,
			   "against_voucher": self.name,
			   "against_voucher_type": self.doctype,
			   # "business_activity": default_ba
			   })
	   )


	   return gl_entries              


   @frappe.whitelist()
   def get_previous_km_reading(self):
	   previous_km_reading = 0.0


	   previous_km_reading = self.get_previous_km()


	   if not previous_km_reading:
		   previous_km_reading = frappe.db.get_value("Equipment", self.equipment, "initial_km_reading")


	   self.previous_km = flt(previous_km_reading)


	   return previous_km_reading


   def get_previous_km(self):
	   pol_receive = frappe.qb.DocType("POL Receive")


	   query = (
		   frappe.qb.from_(pol_receive)
		   .select(pol_receive.current_km)
		   .where(
			   (pol_receive.docstatus == 1) &
			   (pol_receive.equipment == self.equipment)
		   )
		   .orderby(pol_receive.creation, order=frappe.qb.desc)
		   .limit(1)
	   ).run(as_dict=True)


	   return query[0].get("current_km") if query else 0
	  
   @frappe.whitelist()
   def get_pol_advance(self):
	   # self.set("advances", [])
	  
	   Advance = frappe.qb.DocType("POL Advance")
	   if not self.for_machineries:
		   query = (
			   frappe.qb.from_(Advance)
			   .select(
				   Advance.name.as_("reference_name"),
				   Advance.advance_amount,
				   Advance.balance_amount,
				   Advance.posting_date.as_("advance_date"),
			   )
			   .where(
				   (Advance.docstatus == 1)
				   & (Advance.balance_amount > 0)
				#    & (Advance.status == "Paid")
				   & (Advance.equipment == self.equipment)
				   & (Advance.fuelbook == self.fuelbook)
				   & (Advance.company == self.company)
			   )
		   )
		  
	   else:
		   query = (
			   frappe.qb.from_(Advance)
			   .select(
				   Advance.name.as_("reference_name"),
				   Advance.advance_amount,
				   Advance.balance_amount,
				   Advance.posting_date.as_("advance_date"),
			   )
			   .where(
				   (Advance.docstatus == 1)
				   & (Advance.balance_amount > 0)
				#    & (Advance.status == "Paid")
				   & (Advance.equipment == self.equipment)
				   & (Advance.supplier == self.supplier)
				   & (Advance.company == self.company)
			   )
		   )
	  
	   advances = query.run(as_dict=True)
	  
	   if advances:
		   self.set("advances", advances)
	   else:
		   frappe.msgprint("No advances found for this request.", alert=True)
