# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.custom_utils import check_future_date, get_branch_cc, prepare_gl, prepare_sl, check_budget_available
from frappe.utils import flt, cint, getdate
from erpnext.controllers.stock_controller import StockController
# from erpnext.fleet_management.fleet_utils import get_pol_till, get_previous_km
from erpnext.accounts.general_ledger import (
	get_round_off_account_and_cost_center,
	make_gl_entries,
	make_reverse_gl_entries,
	merge_similar_entries,
)
from frappe.desk.reportview import get_match_cond
from erpnext.accounts.utils import get_fiscal_year
# from erpnext.fleet_management.report.hsd_consumption_report.fleet_management_report import get_pol_tills, get_pol_consumed_tills

# from erpnext.fleet_management.report.fleet_management_report import get_pol_till
from erpnext.stock.utils import get_stock_balance
# from erpnext.fleet_management.fleet_utils import get_without_fuel_hire
# from erpnext.fleet_management.maintenance_utils import get_without_fuel_hire
class POLIssue(StockController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.fleet_management.doctype.pol_issue_item.pol_issue_item import POLIssueItem
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		company: DF.Link
		cost_center: DF.Link | None
		item_name: DF.ReadOnly | None
		items: DF.Table[POLIssueItem]
		pol_type: DF.Link
		posting_date: DF.Date
		posting_time: DF.Time
		project: DF.Link | None
		purpose: DF.Literal["", "Issue", "Transfer"]
		registration_number: DF.ReadOnly | None
		remarks: DF.SmallText | None
		stock_uom: DF.ReadOnly | None
		tank_balance: DF.Float
		total_quantity: DF.Float
		warehouse: DF.Link
	# end: auto-generated types
	# def before_save(self):
	# 	if not self.tanker:
	# 		return
	# 	# received_till = get_pol_till("Stock", self.tanker, self.posting_date, self.pol_type)
	# 	# issue_till = get_pol_till("Issue", self.tanker, self.posting_date, self.pol_type)
	# 	# balance = flt(received_till) - flt(issue_till)
	# 	# if flt(self.total_quantity) > flt(balance):
	# 	# 	frappe.throw("Not enough balance in tanker to issue. The balance is " + str(balance))

	# 	# # Ensure tank balance does not exceed tank capacity
	# 	if flt(self.tank_balance) < flt(self.total_quantity):
	# 		frappe.throw(
    #             ("Cannot issue quantity ({}) more than the tanker quantity balance ({}).").format(
    #                 self.total_quantity, self.tank_balance
    #             )
    #         )

		# for item in self.get("items"):
		# 	# Ensure tank capacity is greater than or equal to the sum of equipment balance and quantity
		# 	if flt(item.tank_capacity) < flt(cint(item.equipment_balance) + cint(item.qty)):
		# 		frappe.throw(
		# 			("Tank capacity ({0}) should be greater than or equal to the sum of equipment balance and quantity ({1}) in row {2}.").format(
		# 				item.tank_capacity, flt(item.equipment_balance + item.qty), item.idx
		# 			)
		# 		)			


	def validate(self):
		check_future_date(self.posting_date)
		# self.validate_branch()
		#self.populate_data()
		self.validate_warehouse()
		self.validate_data()
		# self.validate_posting_time()
		self.validate_uom_is_integer("stock_uom", "qty")
		# self.check_on_dry_hire()
		""" ++++++++++ Ver 2.0.190509 Begins ++++++++++ """
        # Ver 2.0.190509, following method added by SHIV on 2019/05/21
		self.update_items()

	def validate_branch(self):
		if self.purpose == "Issue":
			frappe.throw("For HSD Issues, Tanker is Mandatory")

		if not self.is_hsd_item:
			self.tanker = ""

		# if self.tanker and self.branch != frappe.db.get_value("Equipment", self.tanker, "branch"):
		# 	frappe.throw("Selected Branch and Equipment Branch does not match")
	
	def validate_warehouse(self):
		self.validate_warehouse_branch(self.warehouse, self.branch)

	def populate_data(self):
		cc = get_branch_cc(self.branch)
		self.cost_center = cc
		warehouse = frappe.db.get_value("Cost Center", cc, "warehouse")
		if not warehouse:
			frappe.throw(str(cc) + " is not linked to any Warehouse")
		self.warehouse = warehouse

	def validate_data(self):
		if not self.purpose:
			frappe.throw("Purpose is Missing")
		if not self.cost_center or not self.warehouse:
			frappe.throw("Cost Center and Warehouse are Mandatory")
		total_quantity = 0
		for a in self.items:
			# no_tank = frappe.db.get_value("Equipment Type", frappe.db.get_value("Equipment", a.equipment, "equipment_type"), "no_own_tank")
			# if no_tank and self.purpose == "Issue":
				# frappe.throw("Cannot Issue to Equipments without own tank " + str(a.equipment))
			if not a.equipment_warehouse or not a.equipment_cost_center:
				frappe.throw("<b>"+str(a.equipment) + "</b> does have a Warehouse and Cost Center Defined")
			if not flt(a.qty) > 0:
				frappe.throw("Quantity for <b>"+str(a.registration_number)+"</b> should be greater than 0")
			total_quantity = flt(total_quantity) + flt(a.qty)
		self.total_quantity = total_quantity

	def check_on_dry_hire(self):
		for a in self.items:
				record = get_without_fuel_hire(a.equipment, self.posting_date, self.posting_time)
				if record:
						data = record[0]
						a.hiring_cost_center = data.cc
						a.hiring_branch =  data.br
						a.hiring_warehouse = frappe.db.get_value("Cost Center", data.cc, "warehouse")
				else:
						a.hiring_cost_center = None
						a.hiring_branch =  None
						a.hiring_warehouse = None

	def on_submit(self):
		if not self.items:
			frappe.throw("Should have a POL Issue Details to Submit")
		self.validate_data()
		# self.check_on_dry_hire()
		# self.check_tanker_hsd_balance()
		""" ++++++++++ Ver 2.0.190509 Begins ++++++++++ """
                # Following lines commented by SHIV on 2019/05/09
		#self.update_stock_gl_ledger(1, 1)
                
		# Following lines added by SHIV on 2019/05/09
		self.update_stock_ledger()
		self.make_gl_entries()
		""" ++++++++++ Ver 2.0.190509 Ends ++++++++++++ """
		
		self.make_pol_entry()

	def on_cancel(self):
		""" ++++++++++ Ver 2.0.190509 Begins ++++++++++ """
		# Following lines commented by SHIV on 2019/05/09
		# self.update_stock_gl_ledger(1, 1)

		# Following lines added by SHIV on 2019/05/09
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
		self.update_stock_ledger()
		self.make_gl_entries_on_cancel()        
		self.delete_pol_entry()

        # Ver 2.0.190509, following method created by SHIV on 2019/05/21
	def update_items(self):
		for a in self.items:
			a.item_code = self.pol_type

			# Cost Center
			# if a.hiring_cost_center:
			# 	a.cost_center = a.hiring_cost_center
			# else:
			# 	a.cost_center = a.equipment_cost_center

			# # Warehouse
			# if a.hiring_warehouse:
			# 	a.warehouse = a.hiring_warehouse
			# else:
			# 	a.warehouse = a.equipment_warehouse

			# Expense Account
			a.equipment_category = frappe.db.get_value("Equipment", a.equipment, "equipment_category")
			# if self.is_hsd_item:
			# 	budget_account = frappe.db.get_value("Equipment Category", a.equipment_category, "budget_account")
			# else:
			# 	budget_account = frappe.db.get_value("Item Default", {'parent': self.pol_type}, "expense_account")
			
			# if not budget_account:
			# 	frappe.throw("Set Budget Account in Equipment Category")
			
			a.expense_account = frappe.db.get_value("Equipment Category", a.equipment_category, "pol_advance_account")


			
    # Ver 2.0.190509, following method added by SHIV on 2019/05/09
	def update_stock_ledger(self):
		sl_entries = []
		for a in self.items:
			if self.purpose == "Issue":
				sl_entries.append(self.get_sl_entries(a, {
					"actual_qty": -1 * flt(a.qty),
					"warehouse": self.warehouse,
					"incoming_rate": 0
				}))
			else:
				# Transfer only if different warehouse
				if a.warehouse != self.warehouse:
					stock_qty, map_rate = get_stock_balance(
						self.pol_type,
						self.warehouse,
						self.posting_date,
						self.posting_time,
						with_valuation_rate=True
					)
					valuation_rate = flt(a.qty) * flt(map_rate)

					# Make SL entries for source warehouse first, then for target warehouse
					sl_entries.append(self.get_sl_entries(a, {
						"actual_qty": -1 * flt(a.qty),
						"warehouse": self.warehouse,
						"incoming_rate": 0
					}))

					sl_entries.append(self.get_sl_entries(a, {
						"actual_qty": flt(a.qty),
						"warehouse": a.warehouse,
						"incoming_rate": flt(map_rate)
					}))

		if self.docstatus == 2:
			sl_entries.reverse()
		# frappe.throw(frappe.as_json(self.__dict__))
		
		self.make_sl_entries(sl_entries, 'Yes' if self.amended_from else 'No')


    # Ver 2.0.190509, following method added by SHIV on 2019/05/21
	def get_gl_entries(self, warehouse_account):
		gl_entries = []
		
		# wh_account = frappe.db.get_value("Account", {"account_type": "Stock", "warehouse": self.warehouse}, "name")
		wh_account = frappe.db.get_value("Warehouse", {"name": self.warehouse}, "account")
		if not wh_account:
			frappe.throw(str(self.warehouse) + " is not linked to any account.")
			
		for a in self.get("items"):
			if a.hiring_branch:
				comparing_branch = a.hiring_branch
			else:
				comparing_branch = a.equipment_branch
			

			# Valuation rate
			stock_qty, map_rate = get_stock_balance(self.pol_type, self.warehouse, self.posting_date, self.posting_time, with_valuation_rate=True)
			valuation_rate = flt(a.qty) * flt(map_rate)

			if self.purpose == "Issue":
				gl_entries.append(
					self.get_gl_dict({
						"account": wh_account,
						"credit": flt(valuation_rate),
						"credit_in_account_currency": flt(valuation_rate),
						"cost_center": self.cost_center,
					})
				)
			
				gl_entries.append(
					self.get_gl_dict({
						"account": a.expense_account,
						"debit": flt(valuation_rate),
						"debit_in_account_currency": flt(valuation_rate),
						"cost_center": a.cost_center,
					})
				)
			elif self.purpose == "Transfer":
				gl_entries.append(
					self.get_gl_dict({
						"account": wh_account,
						"credit": flt(valuation_rate),
						"credit_in_account_currency": flt(valuation_rate),
						"cost_center": self.cost_center,
					})
				)
				debit_account = frappe.db.get_value("Warehouse", {"name": a.warehouse}, "account")
				gl_entries.append(
					self.get_gl_dict({
						"account": debit_account,
						"debit": flt(valuation_rate),
						"debit_in_account_currency": flt(valuation_rate),
						"cost_center": a.cost_center,
					})
				)
				# frappe.throw(frappe.as_json(gl_entries))

			# Do IC Accounting Entry if different branch
			elif comparing_branch != self.branch:
				ic_account = frappe.db.get_single_value("Accounts Settings", "intra_company_account")
				if not ic_account:
					frappe.throw("Setup Intra-Company Account in Accounts Settings")

				gl_entries.append(
					self.get_gl_dict({
						"account": ic_account,
						"debit": flt(valuation_rate),
						"debit_in_account_currency": flt(valuation_rate),
						"cost_center": self.cost_center,
					})
				)

				gl_entries.append(
					self.get_gl_dict({
						"account": ic_account,
						"credit": flt(valuation_rate),
						"credit_in_account_currency": flt(valuation_rate),
						"cost_center": a.cost_center,
					})
				)
				
			else:  # Do IC Accounting Entry if different warehouse within same branch
				if comparing_branch != self.branch:
					ic_account = frappe.db.get_single_value("Accounts Settings", "intra_company_account")
					if not ic_account:
						frappe.throw("Setup Intra-Company Account in Accounts Settings")
						
					twh_account = frappe.db.get_value("Account", {"account_type": "Stock", "warehouse": a.warehouse}, "name")
					if not twh_account:
						frappe.throw(str(a.warehouse) + " is not linked to any account.")

					gl_entries.append(
						self.get_gl_dict({
							"account": wh_account,
							"credit": flt(valuation_rate),
							"credit_in_account_currency": flt(valuation_rate),
							"cost_center": self.cost_center,
						})
					)

					gl_entries.append(
						self.get_gl_dict({
							"account": twh_account,
							"debit": flt(valuation_rate),
							"debit_in_account_currency": flt(valuation_rate),
							"cost_center": a.cost_center,
						})
					)

					gl_entries.append(
						self.get_gl_dict({
							"account": ic_account,
							"debit": flt(valuation_rate),
							"debit_in_account_currency": flt(valuation_rate),
							"cost_center": self.cost_center,
						})
					)

					gl_entries.append(
						self.get_gl_dict({
							"account": ic_account,
							"credit": flt(valuation_rate),
							"credit_in_account_currency": flt(valuation_rate),
							"cost_center": a.cost_center,
						})
					)
		
		# frappe.throw("<pre>{}</pre>".format(frappe.as_json(gl_entries)))
		return gl_entries


	def check_tanker_hsd_balance(self):
		if not self.tanker:
			return
		received_till = get_pol_till("Stock", self.tanker, self.posting_date, self.pol_type)
		issue_till = get_pol_till("Issue", self.tanker, self.posting_date, self.pol_type)
		balance = flt(received_till) - flt(issue_till)
		if flt(self.total_quantity) > flt(balance):
			frappe.throw("Not enough balance in tanker to issue. The balance is " + str(balance))	

	def make_pol_entry(self):
		if getdate(self.posting_date) <= getdate("2024-03-31"):
			return
		# if self.tanker:
		# 	con = frappe.new_doc("POL Entry")
		# 	con.flags.ignore_permissions = 1
		# 	con.equipment = self.tanker
		# 	con.pol_type = self.pol_type
		# 	con.branch = self.branch
		# 	con.posting_date = self.posting_date
		# 	con.posting_time = self.posting_time
		# 	con.qty = self.total_quantity
		# 	con.reference_type = "POL Issue"
		# 	con.reference_name = self.name
		# 	con.type = "Issue"
		# 	con.is_opening = 0
		# 	con.submit()

		for a in self.items:
			if self.branch == a.equipment_branch:
				own = 1
			else:
				own = 0
			con = frappe.new_doc("POL Entry")
			con.flags.ignore_permissions = 1
			con.equipment = a.equipment
			con.pol_type = self.pol_type
			con.branch = a.equipment_branch
			con.posting_date = self.posting_date
			con.posting_time = self.posting_time
			con.qty = a.qty
			con.reference_type = "POL Issue"
			con.reference_name = self.name
			con.own_cost_center = own
			if self.purpose == "Issue":
				con.type = "Receive"
			else:
				con.type = "Stock"
			con.is_opening = 0
			con.submit()

	def delete_pol_entry(self):
		frappe.db.sql("delete from `tabPOL Entry` where reference_name = %s", self.name)


# @frappe.whitelist(allow_guest=True)
# def equipment_query(doctype, txt, searchfield, start, page_len, filters):
#     if not filters.get('branch'):
#         frappe.throw(_("Branch is required to fetch the equipment."))

#     return frappe.db.sql("""
#         SELECT
#             e.name,
#             e.equipment_type,
#             e.registration_number
#         FROM `tabEquipment` e
#         WHERE e.branch = %(branch)s
#           AND e.is_disabled != 1
#           AND e.not_cdcl = 0
#           AND EXISTS (
#               SELECT 1
#               FROM `tabEquipment Type` t
#               WHERE t.name = e.equipment_type
#                 AND t.is_container = 1
#           )
#           AND (
#               {key} LIKE %(txt)s
#               OR e.equipment_type LIKE %(txt)s
#               OR e.registration_number LIKE %(txt)s
#           )
#         {mcond}
#         ORDER BY
#             IF(LOCATE(%(_txt)s, e.name), LOCATE(%(_txt)s, e.name), 99999),
#             IF(LOCATE(%(_txt)s, e.equipment_type), LOCATE(%(_txt)s, e.equipment_type), 99999),
#             IF(LOCATE(%(_txt)s, e.registration_number), LOCATE(%(_txt)s, e.registration_number), 99999),
#             idx DESC,
#             e.name, e.equipment_type, e.registration_number
#         LIMIT %(start)s, %(page_len)s
#     """.format(
#         key=searchfield,
#         mcond=get_match_cond(doctype)
#     ), {
#         "txt": f"%{txt}%",
#         "_txt": txt.replace("%", ""),
#         "start": start,
#         "page_len": page_len,
#         "branch": filters['branch']
#     })


@frappe.whitelist()
def get_equipment_data(equipment_name, all_equipment=0, branch=None):
    data = []
    
    query = """
        SELECT e.name, e.branch, e.registration_number, e.equipment_type
        FROM `tabEquipment` e
        JOIN `tabEquipment Type` et ON e.equipment_type = et.name
    """

    if not all_equipment:
        query += " WHERE et.is_container = 1"
    else:
        query += " WHERE 1=1"
    
    # if branch:
    #     query += " AND e.branch = %(branch)s"
    if equipment_name:
        query += " AND e.name = %(equipment_name)s"
    
    # query += " ORDER BY e.branch"
    
    items = frappe.db.sql("""
        SELECT item_code, item_name, stock_uom 
        FROM `tabItem`
        WHERE is_hsd_item = 1 AND disabled = 0
    """, as_dict=True)
    
    equipment_details = frappe.db.sql(query, {
        # 'branch': branch,
        'equipment_name': equipment_name
    }, as_dict=True)
    
    for eq in equipment_details:
        for item in items:
            received = issued = 0
            if all_equipment:
                if eq.hsd_type == item.item_code:
                    received = get_pol_tills("Receive", eq.name, item.item_code)
                    issued = get_pol_consumed_tills(eq.name,)
            else:
                received = get_pol_tills("Stock", eq.name, item.item_code)
                issued = get_pol_tills("Issue", eq.name, item.item_code)
						
            
            if received or issued:
                data.append({
                    'received': received,
                    'issued': issued,
                    'balance': flt(received) - flt(issued)
                })

			# if received or issued:
			# 		row = [received, issued, flt(received) - flt(issued)]
			# 		data.append(row)	
    
    return data


# @frappe.whitelist()
# def get_tanker_balance(tanker, posting_date, pol_type):
#     received_till = get_pol_till("Stock", tanker, posting_date, pol_type)
#     issue_till = get_pol_till("Issue", tanker, posting_date, pol_type)
#     balance = flt(received_till) - flt(issue_till)
#     return balance


@frappe.whitelist()
def get_tanker_data(doctype, txt, searchfield, start, page_len, filters):
    if not filters.get('branch'):
        frappe.throw(_("Branch is required to fetch the equipment."))
    
    tanker_data = frappe.db.sql("""
        SELECT
            e.name, e.equipment_type, e.registration_number
        FROM `tabEquipment` e
        WHERE e.branch = %(branch)s
          AND e.is_disabled != 1
          AND e.not_cdcl = 0
          AND EXISTS (
              SELECT 1
              FROM `tabEquipment Type` t
              WHERE t.name = e.equipment_type
                AND t.is_container = 1
          )
          AND ({key} LIKE %(txt)s
               OR e.equipment_type LIKE %(txt)s
               OR e.registration_number LIKE %(txt)s)
        {mcond}
        ORDER BY
            IF(LOCATE(%(_txt)s, e.name), LOCATE(%(_txt)s, e.name), 99999),
            IF(LOCATE(%(_txt)s, e.equipment_type), LOCATE(%(_txt)s, e.equipment_type), 99999),
            IF(LOCATE(%(_txt)s, e.registration_number), LOCATE(%(_txt)s, e.registration_number), 99999),
            idx DESC,
            e.name, e.equipment_type, e.registration_number
        LIMIT %(start)s, %(page_len)s
    """.format(
        key=searchfield,
        mcond=get_match_cond(doctype)
    ), {
        "txt": f"%{txt}%",
        "_txt": txt.replace("%", ""),
        "start": start,
        "page_len": page_len,
        "branch": filters['branch']
    })

    return tanker_data

@frappe.whitelist()
def get_tanker_details(tanker, posting_date, pol_type):
    received_till = get_pol_till("Stock", tanker, posting_date, pol_type)
    issue_till = get_pol_till("Issue", tanker, posting_date, pol_type)
    balance = flt(received_till) - flt(issue_till)
    return {"balance": balance}

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles: 
		return

	return """(
		`tabPOL Issue`.owner = '{user}'
		or
		exists(select 1
			from `tabEmployee` as e
			where e.branch = `tabPOL Issue`.branch
			and e.user_id = '{user}')
		or
		exists(select 1
			from `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
			where e.user_id = '{user}'
			and ab.employee = e.name
			and bi.parent = ab.name
			and bi.branch = `tabPOL Issue`.branch)
	)""".format(user=user)


# Equipment Balance
@frappe.whitelist()
def get_equipment_datas(equipment, all_equipment=0, equipment_branch=None):
    """
    Fetch equipment balance details based on the provided parameters.
    """
    # frappe.throw("Fetching Equipment Data")
    data = []

    # Query to fetch equipment details
    query = """
        SELECT e.name, e.branch, e.registration_number, e.equipment_type
        FROM `tabEquipment` e
        JOIN `tabEquipment Type` et ON e.equipment_type = et.name
    """
    if not all_equipment:
        query += " WHERE et.is_container = 1"
    else:
        query += " WHERE 1=1"

    if equipment_branch:
        query += " AND e.equipment_branch = %(equipment_branch)s"
    if equipment:
        query += " AND e.name = %(equipment)s"

    query += " ORDER BY e.branch"

    # Query to fetch items
    items = frappe.db.sql("""
        SELECT item_code, item_name, stock_uom 
        FROM `tabItem`
        WHERE disabled = 0
    """, as_dict=True)

    equipment_details = frappe.db.sql(query, {
        'equipment_branch': equipment_branch,
        'equipment': equipment
    }, as_dict=True)

    for eq in equipment_details:
        for item in items:
            received = issued = 0
            # if all_equipment:
            #     # if eq.hsd_type == item.item_code:
            #         received = get_pol_tills("Receive", eq.name, item.item_code)
            #         issued = get_pol_consumed_tills(eq.name)
            # else:
            #     received = get_pol_tills("Stock", eq.name, item.item_code)
            #     issued = get_pol_tills("Issue", eq.name, item.item_code)

            # Append balance details
            if received or issued:
                data.append({
                    'received': received,
                    'issued': issued,
                    'balance': flt(received) - flt(issued)
                })

    return data
