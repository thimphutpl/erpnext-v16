# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt
from erpnext.projects.custom_utils import get_month_details
from erpnext.projects.custom_utils import prepare_gl
from erpnext.accounts.general_ledger import make_gl_entries


class ProcessOvertimePayment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.projects.doctype.overtime_payment_item.overtime_payment_item import OvertimePaymentItem
		from frappe.types import DF

		amended_from: DF.Link | None
		applied_by: DF.Link | None
		approved_by: DF.Link | None
		assign_from_cheque_lot: DF.Check
		bank_name: DF.Link
		branch: DF.Link
		cheque_date: DF.Date | None
		cheque_lot: DF.Link | None
		cheque_no: DF.Data | None
		clearance_date: DF.Date | None
		company: DF.Link | None
		cost_center: DF.Link
		expense_bank_account: DF.Link | None
		fiscal_year: DF.Link
		items: DF.Table[OvertimePaymentItem]
		month: DF.Literal["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
		ot_account: DF.Link | None
		payment_jv: DF.ReadOnly | None
		posting_date: DF.Date
		remarks: DF.SmallText | None
		total_amount: DF.Currency
		verified_by: DF.Link | None
	# end: auto-generated types
	# pass
	def validate(self):
		if not self.fiscal_year or not self.month:
			frappe.throw("Fiscal Year/ Month is Required")
	
		if not self.cost_center:
			frappe.throw("Cost Center is not Selected")
	
		if not self.branch:
			frappe.throw(" Branch is Mandiatory")
	
		#set up expense bank account	
		expense_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		self.expense_bank_account = expense_bank_account
		if not self.expense_bank_account:
			frappe.throw("Expense Bank Account is Missing!. Refresh Cost Center Field")

		#set up Expense Account
		ot_account = frappe.db.get_single_value("HR Accounts Settings", "overtime_account")
		self.ot_account = ot_account
		if not self.ot_account:
			frappe.throw("Expense Account Not Found, Kindly set up Overtime Account in HR Accounts Settings")

		self.check_duplicate_entries()
		# set_user(self)

	def check_duplicate_entries(self):
		not_found = []
		found = []
		for a in self.items:
			if a.employee not in  found:
				not_found.append(a.employee)
			else:
				found.append(a.employee)
				frappe.throw("Double Entry is not allowed for {0}".format(found))

	def on_submit(self):
		self.post_general_ledger()

	def on_cancel(self):
		if self.clearance_date:
			frappe.throw("Already done bank reconciliation.")
		frappe.db.sql(""" update `tabOvertime Application` set payment_jv = '' where payment_jv = '{0}'""".format(self.name))
		frappe.db.sql(""" delete from `tabGL Entry` where voucher_type = '{0}' and voucher_no = '{1}'""".format(self.doctype, self.name))
	
	@frappe.whitelist()
	def get_ot_details(self):
		m = get_month_details(self.fiscal_year, self.month)
		from_date = m['month_start_date']
		to_date = m['month_end_date']

		query = """select name as reference_doc, employee, employee_name, rate as hourly_rate, total_hours, total_amount as total_ot_amount
			from `tabOvertime Application` where docstatus = 1 and workflow_state = 'Approved' 
			and ifnull(payment_jv, '') = ''
			and cost_center ='{2}'
			and posting_date >= '{0}' and posting_date <= '{1}'
			order by employee desc
		""".format(from_date, to_date, self.cost_center)
		
		entries = frappe.db.sql(query, as_dict=True)
		# frappe.throw(str(entries))
		if not entries:
			frappe.msgprint("OT Payment is already processed or there is no Approved OT to process")

		self.set('items', [])

		for d in entries:
			doc = frappe.get_doc("Employee", d.employee)
			row = self.append('items', {})
			row.bank_name = doc.bank_name
			row.bank_account = doc.bank_ac_no
			row.designation = doc.designation
			row.grade = doc.employee_subgroup
			row.cost_center = doc.cost_center	
			row.update(d)

		total = 0.0
		for a in self.get('items'):
			total += flt(a.total_ot_amount)
		self.total_amount = total

	
	def post_general_ledger(self):
		gl_entries = []
		ot_account = frappe.db.get_single_value("HR Accounts Settings", "overtime_account")
		expense_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		if not self.cost_center:
				frappe.throw("Cost Center Is Required")
		if not expense_bank_account:
				frappe.throw("Setup Default Expense Bank Account for your Branch")
		if not ot_account:
				frappe.throw("Setup Default Overtime Account in HR Account Setting")
	
		query = """select cost_center, sum(total_ot_amount) as total_ot_amount 
            from `tabOvertime Payment Item` 
			where docstatus = 1 
			and parent = '{0}'  
			group by cost_center
        """.format(self.name)
		for d in frappe.db.sql(query, as_dict = True):
			gl_entries.append(
				prepare_gl(self, {"account": expense_bank_account,
					"credit": flt(d.total_ot_amount),
					"credit_in_account_currency": flt(d.total_ot_amount),
					"voucher_no": self.name,
					"voucher_type": self.doctype,
					"cost_center": d.cost_center,
					"company": self.company
					})
			)
			gl_entries.append(
				prepare_gl(self, {"account": ot_account,
						"debit": flt(d.total_ot_amount),
						"debit_in_account_currency": flt(d.toatl_ot_amount),
						"voucher_no": self.name,
						"voucher_type": self.doctype,
						"cost_center": d.cost_center,
						"company": self.company
					})
				)
		make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=False)
		self.update_ot()


	def update_ot(self):
		for d in self.get('items'):
			doc = frappe.get_doc("Overtime Application", d.reference_doc)
			doc.db_set("payment_jv", self.name)
