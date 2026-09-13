# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, money_in_words
# from erpnext.accounts.doctype.business_activity.business_activity import get_default_ba
from erpnext.accounts.party import get_party_account
from erpnext.controllers.accounts_controller import AccountsController

class InsuranceandRegistration(AccountsController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.fleet_management.doctype.bluebook_and_emission.bluebook_and_emission import BluebookandEmission
		from erpnext.fleet_management.doctype.claim_details.claim_details import ClaimDetails
		from erpnext.fleet_management.doctype.insurance_details.insurance_details import InsuranceDetails
		from erpnext.fleet_management.doctype.registration_details.registration_details import RegistrationDetails
		from frappe.types import DF

		amended_from: DF.Link | None
		asset: DF.Link | None
		asset_category: DF.Data | None
		asset_name: DF.Data | None
		asset_sub_category: DF.Data | None
		bluebookfitnessemission: DF.Check
		branch: DF.Link | None
		claim: DF.Check
		claim_item: DF.Table[ClaimDetails]
		company: DF.Link | None
		cost_center: DF.Link
		designation: DF.Data | None
		employee: DF.Link | None
		employee_name: DF.Data | None
		equipment: DF.Link | None
		imprest_party: DF.Link | None
		insurance: DF.Check
		insurance_for: DF.Literal["Vehicle"]
		insurance_item: DF.Table[InsuranceDetails]
		items: DF.Table[BluebookandEmission]
		posting_date: DF.Date | None
		reference: DF.Data | None
		registration: DF.Check
		registration_item: DF.Table[RegistrationDetails]
		settle_imprest_advance: DF.Check
		vehicle_model: DF.Data | None
		vehicle_type: DF.Link | None
	# end: auto-generated types
	def validate(self):
		self.check_transaction()
		self.prevent_row_remove()
   
	def on_submit(self):
		self.make_gl_entry()
  
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
		
		self.make_gl_entry()
  
	def check_transaction(self):
		true_count = sum([bool(self.insurance), bool(self.registration), bool(self.claim), bool(self.bluebookfitnessemission)])
		if true_count > 1:
			frappe.throw('Please choose only one option per transaction')
   
	def make_gl_entry(self):
		from erpnext.accounts.general_ledger import make_gl_entries

		bank_account = frappe.db.get_value("Company", "Thimphu Techpark Limited", "default_bank_account")
		if not bank_account:
			frappe.throw("Setup Bank Account in Company")

		

		gl_entries = []

		# Process insurance items
		if self.insurance:
			insurance_expense_account = frappe.db.get_value("Company", "Thimphu Techpark Limited", "insurance_expense_account")
			if not insurance_expense_account:
				frappe.throw("Setup Insurance Expense Account in Company")
			if self.insurance_item:
				for i in self.insurance_item:
					# Debit Entry - Insurance Expense
					gl_entries.append(
						self.get_gl_dict({
							"account": insurance_expense_account,
							"debit": flt(i.total_amount),
							"debit_in_account_currency": flt(i.total_amount),
							"cost_center": self.cost_center,
							"reference_type": self.doctype,
							"reference_name": self.name,
							"remarks": f"Insurance payment for {self.equipment}"
						})
					)

					# Credit Entry - Bank Account
					gl_entries.append(
						self.get_gl_dict({
							"account": bank_account,
							"credit": flt(i.total_amount),
							"credit_in_account_currency": flt(i.total_amount),
							"cost_center": self.cost_center,
							"remarks": f"Insurance payment for {self.equipment}"
						})
					)
		if self.registration:
			registration_expense_account = frappe.db.get_value("Company", "Green Bhutan Corporation Limited", "registration_expense_account")
			if not registration_expense_account:
				frappe.throw("Setup Insurance Expense Account in Company")
			if self.registration_item:
				for i in self.registration_item:
					gl_entries.append(
							self.get_gl_dict({
								"account": registration_expense_account,
								"debit": flt(i.registration_amount),
								"debit_in_account_currency": flt(i.registration_amount),
								"cost_center": self.cost_center,
								"reference_type": self.doctype,
								"reference_name": self.name,
								"remarks": f"Insurance payment for {self.equipment}"
							})
						)

					# Credit Entry - Bank Account
					gl_entries.append(
							self.get_gl_dict({
								"account": bank_account,
								"credit": flt(i.registration_amount),
								"credit_in_account_currency": flt(i.registration_amount),
								"cost_center": self.cost_center,
								"remarks": f"Insurance payment for {self.equipment}"
							})
						)
		if self.claim:
			motor_claim_account = frappe.db.get_value("Company", "Green Bhutan Corporation Limited", "insurance_claim_expense_account")
			if not motor_claim_account:
				frappe.throw("Setup Insurance Claim Expense Account in Company")
			if self.claim_item:
				for i in self.claim_item:
					gl_entries.append(
							self.get_gl_dict({
								"account": motor_claim_account,
								"credit": flt(i.claim_amount),
								"credit_in_account_currency": flt(i.claim_amount),
								"cost_center": self.cost_center,
								"reference_type": self.doctype,
								"reference_name": self.name,
								"remarks": f"Insurance payment for {self.equipment}"
							})
						)

					# Credit Entry - Bank Account
					gl_entries.append(
							self.get_gl_dict({
								"account": bank_account,
								"debit": flt(i.claim_amount),
								"debit_in_account_currency": flt(i.claim_amount),
								"cost_center": self.cost_center,
								"remarks": f"Insurance payment for {self.equipment}"
							})
						)
			
		if self.bluebookfitnessemission:
			if self.items:
				for i in self.items:
					if i.type == "Registration Certificate":
						expense_account = frappe.db.get_value("Company", "Green Bhutan Corporation Limited", "registration_certificate_expense_account")
					if i.type == "Fitness":
						expense_account = frappe.db.get_value("Company", "Green Bhutan Corporation Limited", "fitness_expense_account")
					if i.type == "Emission":
						expense_account = frappe.db.get_value("Company", "Green Bhutan Corporation Limited", "emission_expense_account")
					if i.type == "Offense":
						expense_account = frappe.db.get_value("Company", "Green Bhutan Corporation Limited", "offence_expense_account")
					gl_entries.append(
							self.get_gl_dict({
								"account": expense_account,
								"debit": flt(i.total_amount),
								"debit_in_account_currency": flt(i.total_amount),
								"cost_center": self.cost_center,
								"reference_type": self.doctype,
								"reference_name": self.name,
								"remarks": f"Insurance payment for {self.equipment}"
							})
						)

					# Credit Entry - Bank Account
					gl_entries.append(
							self.get_gl_dict({
								"account": bank_account,
								"credit": flt(i.total_amount),
								"credit_in_account_currency": flt(i.total_amount),
								"cost_center": self.cost_center,
								"remarks": f"Insurance payment for {self.equipment}"
							})
						)


		make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=False)	

	def prevent_row_remove(self):
		unsafed_record = [d.name for d in self.insurance_item]
		if flt(len(unsafed_record)) <= 0:
			unsafed_record = ["Dummy"]
		for d in frappe.db.sql(
			"select name, journal_entry, idx from `tabInsurance Details` where parent = '{}'".format(
				self.name
			),
			as_dict=True,
		):
			if d.name not in unsafed_record and d.journal_entry:
				je = frappe.get_doc("Journal Entry", d.journal_entry)
				if je.docstatus != 2:
					frappe.throw(
						"You cannot delete row {} from Insurance Detail as \
						accounting entry is booked".format(
							frappe.bold(d.idx)
						)
					)

		unsafed_record = [d.name for d in self.items]
		if flt(len(unsafed_record)) <= 0:
			unsafed_record = ["Dummy"]
		for d in frappe.db.sql(
			"select name, journal_entry, idx from `tabBluebook and Emission` where parent = '{}'".format(
				self.name
			),
			as_dict=True,
		):
			if d.name not in unsafed_record and d.journal_entry:
				je = frappe.get_doc("Journal Entry", d.journal_entry)
				if je.docstatus != 2:
					frappe.throw(
						"You cannot delete row {} from Bluebook Fitness \
							and Emission Details as accounting entry is booked".format(
							frappe.bold(d.idx)
						)
					)

	@frappe.whitelist()
	def create_je(self):
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1
		
		bank_account = frappe.db.get_value("Company", "Green Bhutan Corporation Limited", "default_bank_account")
		if not bank_account:
			frappe.throw("Setup Bank Account in Company")
		
		insurance_expense_account = frappe.db.get_value("Company", "Green Bhutan Corporation Limited", "insurance_expense_account")
		if not insurance_expense_account:
			frappe.throw("Setup Insurance Expense Account in Company")

		total_amount = sum(flt(i.total_amount) for i in self.insurance_item)  # Calculate total amount for validation

		# Set the main Journal Entry fields
		je.update({
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"naming_series": "Journal Voucher",
			"user_remark": f"Note: Charge paid against Vehicle {self.equipment}",
			"posting_date": self.posting_date,
			"company": self.company,
			"total_amount_in_words": money_in_words(total_amount),
			"branch": self.branch,
		})

		# Append debit entries (Expense Entries)
		for i in self.insurance_item:
			je.append("accounts", {
				"account": insurance_expense_account,
				"debit_in_account_currency": i.total_amount,
				"debit": i.total_amount,
				"cost_center": self.cost_center,
				"party_type": "Supplier",
				"party": i.party,
				"reference_type": self.doctype,
				"reference_name": self.name,
			})

		# Append a single credit entry (Bank Payment)
		je.append("accounts", {
			"account": bank_account,
			"credit_in_account_currency": total_amount,
			"credit": total_amount,
			"cost_center": self.cost_center,
		})

		# Insert the Journal Entry once, outside the loop
		je.insert()

			

	@frappe.whitelist()
	def post_to_account(self, args):
		if args.journal_entry and frappe.db.exists("Journal Entry", args.journal_entry):
			doc = frappe.get_doc("Journal Entry", args.journal_entry)
			if doc.docstatus != 2:
				frappe.throw(
					"Journal Entry exists for this transaction {}".format(
						frappe.get_desk_link("Journal Entry", args.journal_entry)
					)
				)

		if flt(args.registration_amount) <= 0:
			frappe.throw(_("Amount should be greater than zero"))

		default_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		imprest_advance_account = frappe.db.get_value(
			"Company", self.company, "imprest_advance_account"
		)
		if self.settle_imprest_advance == 1 and not imprest_advance_account:
			frappe.throw("Please set Imprest Advance Account in company settings")

		debit_account = frappe.db.get_single_value("Maintenance Settings", "registration_account")
		if not debit_account:
			frappe.throw("Please set Account in maintenance settings")

		# Posting to JE
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1
		je.update(
			{
				"doctype": "Journal Entry",
				"voucher_type": "Bank Entry" if self.settle_imprest_advance == 0 else "Journal Entry",
				"naming_series": "Bank Payment Voucher" if self.settle_imprest_advance == 0 else "Journal Voucher",
				"title": " Registration - " + self.equipment,
				"user_remark": "Note: Registration paid against Vehicle "+ self.equipment,
				"posting_date": args.registration_date,
				"company": self.company,
				"total_amount_in_words": money_in_words(args.registration_amount),
				"branch": self.branch,
				"total_debit": args.registration_amount,
				"total_credit": args.registration_amount,
				"settle_project_imprest": self.settle_imprest_advance,
			}
		)
		je.append("accounts",
			{
				"account": debit_account,
				"debit_in_account_currency": args.registration_amount,
				"debit": args.registration_amount,
				"cost_center": frappe.db.get_value("Branch", self.branch, "cost_center"),
				"party_check": 0,
				"party_type": "Supplier",
				"party": args.party,
				"reference_type": self.doctype,
				"reference_name": self.name,
			},
		)
		if self.settle_imprest_advance == 0:
			je.append(
				"accounts",
				{
					"account": default_bank_account,
					"credit_in_account_currency": args.registration_amount,
					"credit": args.registration_amount,
					"cost_center": frappe.db.get_value("Branch", self.branch, "cost_center"),
				},
			)
		else:
			je.append(
				"accounts",
				{
					"account": imprest_advance_account,
					"party_type": "Employee",
					"party": self.imprest_party,
					"credit_in_account_currency": args.registration_amount,
					"credit": args.registration_amount,
					"cost_center": frappe.db.get_value("Branch", self.branch, "cost_center"),
				},
			)

		je.insert()
		frappe.msgprint(
			_("Journal Entry {0} posted to accounts").format(
				frappe.get_desk_link("Journal Entry", je.name)
			)
		)
		return je.name

	@frappe.whitelist()
	def post_je(self):
		if self.reference:
			frappe.throw(
				"Journal Entry exists for this transaction {}".format(
					frappe.get_desk_link("Journal Entry", self.reference)
				)
			)
		if len(self.items) <= 0:
			frappe.throw(_("There must be at least one or more item in the table"))

		total_amount = 0.00
		for i in self.items:
			total_amount += flt(i.total_amount)

		if flt(total_amount) <= 0:
			frappe.throw(_("Amount should be greater than zero"))

		default_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		imprest_advance_account = frappe.db.get_value(
			"Company", self.company, "imprest_advance_account"
		)
		if self.settle_imprest_advance == 1 and not imprest_advance_account:
			frappe.throw("Please set Imprest Advance Account in company settings")
		# Posting Journal Entry
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1
		posting_date = self.get("posting_date")
		# debit_account = frappe.db.get_value(
		#     "Company", self.company, "repair_and_service_expense_account"
		# )
		# if not debit_account:
		#     frappe.throw("Setup Fleet Expense Account in Company".format())
		if not default_bank_account:
			frappe.throw("Setup Default Bank Account in Branch {}".format(self.branch))

		fine_and_penalty_account = frappe.db.get_value(
			"Company", self.company, "fine_and_penalty_account"
		)

		if not fine_and_penalty_account:
			frappe.throw("Fines and Penalty Account not set in company setting")

		je.update(
			{
				"doctype": "Journal Entry",
				"voucher_type": "Bank Entry"
				if self.settle_imprest_advance == 0
				else "Journal Entry",
				"naming_series": "Bank Payment Voucher"
				if self.settle_imprest_advance == 0
				else "Journal Voucher",
				"title": " Bluebook Fitness and Emission Charge - " + self.equipment,
				"user_remark": "Note: Bluebook Fitness and Emission Charge "
				+ " Charge paid against Vehicle "
				+ self.equipment,
				"posting_date": posting_date,
				"company": self.company,
				"total_amount_in_words": money_in_words(total_amount),
				"branch": self.branch,
				"total_debit": total_amount,
				"total_credit": total_amount,
				"settle_project_imprest": self.settle_imprest_advance,
			}
		)
		# debit
		for args in self.items:
			account = ""
			if args.get("type") == "Bluebook":
				account = frappe.db.get_single_value("Maintenance Settings", "bluebook")
			elif args.get("type") == "Emission":
				account = frappe.db.get_single_value("Maintenance Settings", "emission")
			elif args.get("type") == "Fitness":
				account = frappe.db.get_single_value("Maintenance Settings", "fitness")
			elif args.get("type") == "Offense":
				account = frappe.db.get_single_value("Maintenance Settings", "offense")

			if not account:
				frappe.throw(
					"GL not set in maintenance setting for type {} ".format(args.get("type"))
				)

			je.append(
				"accounts",
				{
					"account": account,
					"debit_in_account_currency": args.amount,
					"debit": args.amount,
					"cost_center": frappe.db.get_value("Branch", self.branch, "cost_center"),
					"party_check": 0,
					"party_type": "Supplier",
					"party": args.party,
					"reference_type": self.doctype,
					"reference_name": self.name,
				},
			)

			if args.penalty_amount > 0:
				je.append(
					"accounts",
					{
						"account": fine_and_penalty_account,
						"debit_in_account_currency": args.penalty_amount,
						"debit": args.penalty_amount,
						"cost_center": frappe.db.get_value("Branch", self.branch, "cost_center"),
						"party_check": 0,
						"party_type": "Supplier",
						"party": args.party,
						"reference_type": self.doctype,
						"reference_name": self.name,
					},
				)

		if self.settle_imprest_advance == 0:
			je.append(
				"accounts",
				{
					"account": default_bank_account,
					"credit_in_account_currency": total_amount,
					"credit": total_amount,
					"cost_center": frappe.db.get_value("Branch", self.branch, "cost_center"),
				},
			)
		else:
			je.append(
				"accounts",
				{
					"account": imprest_advance_account,
					"party_type": "Employee",
					"party": self.imprest_party,
					"credit_in_account_currency": total_amount,
					"credit": total_amount,
					"cost_center": frappe.db.get_value("Branch", self.branch, "cost_center"),
				},
			)
		je.insert()
		frappe.msgprint(
			_("Journal Entry {0} posted to accounts").format(
				frappe.get_desk_link("Journal Entry", je.name)
			)
		)
		frappe.db.set_value("Insurance and Registration", self.name, "reference", je.name)
		return je.name
