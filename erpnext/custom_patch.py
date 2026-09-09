import frappe
from erpnext.setup.doctype.employee.employee import create_user
# import pandas as pd
import csv
from frappe.utils import flt, cint, nowdate, getdate, formatdate
import math
from datetime import timedelta
from frappe.query_builder.functions import Sum
from frappe.utils import date_diff, flt, cint, nowdate, getdate
# from erpnext.integrations.bps import process_files
from erpnext.assets.doctype.asset.depreciation import make_depreciation_entry
# from hrms.hr.hr_custom_functions import post_leave_credits
import pandas as pd
from datetime import datetime, timedelta, date

def update_aid_asset_journal_entry():
	asset = frappe.db.sql("""
								select name from `tabAsset Issue Details` where docstatus = 1 and is_existing_asset = 1;
									""",as_dict=1)
	count = 1
	for a in asset:
		asset = frappe.get_doc("Asset", {"asset_issue_details": a.name})
		journal_entry = frappe.db.sql("""
									select distinct je.name from `tabJournal Entry` je, `tabJournal Entry Account` jea where je.user_remark like '%Asset Issued%' and jea.parent = je.name and jea.reference_name = '{}'
									""".format(asset.name),as_dict=1)
		for je in journal_entry:
			frappe.db.sql("update `tabJournal Entry` set posting_date = '{}' where name = '{}'".format(asset.available_for_use_date, je.name))
			frappe.db.sql("update `tabGL Entry` set posting_date = '{}' where voucher_no = '{}'".format(asset.available_for_use_date, je.name))
		print(str(count)+". "+a.name)
		count += 1

#  start
import frappe

def safe_cancel_docs(doctype, filters, cancel_message):
	try:
		docs = frappe.get_all(doctype, filters=filters)
		for d in docs:
			doc = frappe.get_doc(doctype, d.name)
			print(cancel_message.format(name=doc.name))
			doc.cancel()
	except Exception as e:
		print(f"Skipping {doctype}: {e}")

def cancel_journal_entry_with_workflow_fix(je_name):
	try:
		je_doc = frappe.get_doc("Journal Entry", je_name)
		if je_doc.docstatus == 1:
			print(f"Cancelling Journal Entry {je_doc.name}")
			je_doc.cancel()
			# Forcefully set workflow_state and status to Cancelled
			frappe.db.set_value("Journal Entry", je_doc.name, "workflow_state", "Cancelled")
			frappe.db.set_value("Journal Entry", je_doc.name, "workflow_state", "Cancelled")
	except Exception as e:
		print(f"Skipping Journal Entry {je_name}: {e}")

def cancel_linked_journal_entries(asset_name):
	je_names = frappe.db.get_all(
		"Journal Entry Account",
		filters={"reference_type": "Asset", "reference_name": asset_name, "docstatus": 1},
		pluck="parent"
	)
	je_names = list(set(je_names))  # Remove duplicates
	for je in je_names:
		cancel_journal_entry_with_workflow_fix(je)

def bulk_cancel_selected_assets():
    asset_list = [
        "ASSET210700037",
        "ASSET210700055",
        "ASSET210700057",
        "ASSET210700058",
        "ASSET210700059",
        "ASSET210700060",
        "ASSET210700062",
        "ASSET210800018",
        "ASSET210800019",
        "ASSET210800021",
        "ASSET210800022",
        "ASSET210800023",
        "ASSET210800027",
        "ASSET210800029",
        "ASSET210800033",
        "ASSET210800035",
        "ASSET210800036",
        "ASSET210800037",
        "ASSET210800038",
        "ASSET210800039",
        "ASSET210800040",
        "ASSET210800041",
        "ASSET210800042",
        "ASSET210800043",
        "ASSET210800048",
        "ASSET210800052",
        "ASSET210800054",
        "ASSET210800055",
        "ASSET210800056",
        "ASSET210800057",
        "ASSET210800067",
        "ASSET210800068",
        "ASSET210800069",
        "ASSET210800070",
        "ASSET210800073",
        "ASSET210800075",
        "ASSET210800077",
        "ASSET210800079",
        "ASSET210800080",
        "ASSET210800081",
        "ASSET210800082",
        "ASSET210800088",
        "ASSET210800090",
        "ASSET210800091",
        "ASSET210800092",
        "ASSET210800093",
        "ASSET210800094",
        "ASSET210800102",
        "ASSET210900021",
        "ASSET210900022",
        "ASSET210900023",
        "ASSET211000021",
        "ASSET211000098",
        "ASSET211000099",
        "ASSET211000100",
        "ASSET211000101",
        "ASSET211000102",
        "ASSET211000103",
        "ASSET211000104",
        "ASSET211000107",
        "ASSET211000110",
        "ASSET211200098",
        "ASSET220100032",
        "ASSET220100033",
        "ASSET220100034",
        "ASSET220100035",
        "ASSET220200030",
        "ASSET220200031",
        "ASSET220300040",
        "ASSET220400009",
        "ASSET220400010",
        "ASSET220400011",
        "ASSET220400012",
        "ASSET220400013",
        "ASSET220500044",
        "ASSET220500068",
        "ASSET220500069",
        "ASSET220500083",
        "ASSET220700005",
        "ASSET220700026",
        "ASSET220700030",
        "ASSET220700031",
        "ASSET220700034",
        "ASSET220700036",
        "ASSET220800012",
        "ASSET220800019",
        "ASSET220800058",
        "ASSET220900005",
        "ASSET220900006",
        "ASSET220900012",
        "ASSET220900017",
        "ASSET220900018",
        "ASSET220900019",
        "ASSET220900031",
        "ASSET220900032",
        "ASSET220900033",
        "ASSET221000002",
        "ASSET221000006",
        "ASSET221000015",
        "ASSET221000017",
        "ASSET221000027",
        "ASSET221000028",
        "ASSET221000029",
        "ASSET221000041",
        "ASSET221000042",
        "ASSET221000044",
        "ASSET221100016",
        "ASSET221100022",
        "ASSET221100024",
        "ASSET221100027",
        "ASSET221100028",
        "ASSET221100030",
        "ASSET221100038",
        "ASSET221100039",
        "ASSET221100040",
        "ASSET221100048",
        "ASSET221100050",
        "ASSET221100051",
        "ASSET221100053",
        "ASSET221100057",
        "ASSET221100065",
        "ASSET221100066",
        "ASSET221100067",
        "ASSET221100068",
        "ASSET221100069",
        "ASSET221100070",
        "ASSET221200013",
        "ASSET221200014",
        "ASSET221200015",
        "ASSET221200029",
        "ASSET221200105",
        "ASSET221200106",
        "ASSET221200109",
        "ASSET221200110",
        "ASSET221200111",
        "ASSET221200112",
        "ASSET221200113",
        "ASSET221200114",
        "ASSET221200115",
        "ASSET221200116",
        "ASSET221200117",
        "ASSET221200121",
        "ASSET221200127",
        "ASSET221200188",
        "ASSET230100204",
        "ASSET230100205-1",
        "ASSET230100206",
        "ASSET230100207",
        "ASSET230100208",
        "ASSET230100209",
        "ASSET230100210",
        "ASSET230100214",
        "ASSET230200001",
        "ASSET230200002",
        "ASSET230200003",
        "ASSET230200004",
        "ASSET230200025",
        "ASSET230200026",
        "ASSET230200028",
        "ASSET230200095",
        "ASSET230200096",
        "ASSET230200098",
        "ASSET230200099",
        "ASSET230200101",
        "ASSET230300002",
        "ASSET230300003",
        "ASSET230300005",
        "ASSET230300006",
        "ASSET230300009",
        "ASSET230300010",
        "ASSET230300011",
        "ASSET230300012",
        "ASSET230300013",
        "ASSET230300017",
        "ASSET230300018",
        "ASSET230300019",
        "ASSET230300020",
        "ASSET230300022",
        "ASSET230300030",
        "ASSET230300031",
        "ASSET230300033",
        "ASSET230300037",
        "ASSET230300038",
        "ASSET230300046",
        "ASSET230300051",
        "ASSET230300059",
        "ASSET230300062",
        "ASSET230300065",
        "ASSET230400001",
        "ASSET230400002",
        "ASSET230500003",
        "ASSET230500005",
        "ASSET230500013",
        "ASSET230500014",
        "ASSET230500015",
        "ASSET230500019",
        "ASSET230500020",
        "ASSET230500021",
        "ASSET230500023"
    ]

    for asset_name in asset_list:
        asset = frappe.get_doc("Asset", asset_name)
        if asset.docstatus != 1:
            print(f"Asset {asset_name} is not submitted. Skipping.")
            continue

        # Cancel Journal Entries directly linked to Asset
        cancel_linked_journal_entries(asset_name)

        # Cancel Asset Depreciation Schedules (and Journal Entries if link exists)
        dep_schedules = frappe.get_all("Asset Depreciation Schedule", filters={"asset": asset_name, "docstatus": 1})
        for dep in dep_schedules:
            dep_doc = frappe.get_doc("Asset Depreciation Schedule", dep.name)
            if hasattr(dep_doc, "journal_entry") and dep_doc.journal_entry:
                cancel_journal_entry_with_workflow_fix(dep_doc.journal_entry)
            print(f"Cancelling Depreciation Schedule {dep_doc.name}")
            dep_doc.cancel()

        # Cancel Asset Movements
        safe_cancel_docs("Asset Movement", {"asset": asset_name, "docstatus": 1}, "Cancelling Asset Movement {name}")

        # Cancel Asset Value Adjustments (will skip if missing)
        safe_cancel_docs("Asset Value Adjustment", {"asset": asset_name, "docstatus": 1}, "Cancelling Asset Value Adjustment {name}")

        # Cancel Asset Transfers (will skip if missing)
        safe_cancel_docs("Asset Transfer", {"asset": asset_name, "docstatus": 1}, "Cancelling Asset Transfer {name}")

        # Cancel linked Asset Issue Details (if present in field)
        aid_name = getattr(asset, "asset_issue_details", None)
        if aid_name:
            try:
                aid_doc = frappe.get_doc("Asset Issue Details", aid_name)
                if aid_doc.docstatus == 1:
                    print(f"Cancelling Asset Issue Details {aid_doc.name}")
                    aid_doc.cancel()
                    frappe.db.set_value("Asset Issue Details", aid_doc.name, "workflow_state", "Cancelled")
            except Exception as e:
                print(f"Skipping Asset Issue Details {aid_name}: {e}")

        print(f"Cancelling Asset {asset.name}")
        asset.reload()
        asset.cancel()
        print(f"Asset {asset.name} and all linked docs cancelled.")


# end


def update_leave_policy_assignment_la():
	count = 1
	for lpa in frappe.db.sql("""
						  select name, employee from `tabLeave Policy Assignment` where year(effective_from) = 2025 and docstatus = 1;
						  """,as_dict=1):
		for la in frappe.db.sql("""
							select name from `tabLeave Allocation` where year(from_date) = 2025 and leave_type in ('Casual Leave', 'Earned Leave') and docstatus = 1 and employee = '{}';
						  """.format(lpa.employee),as_dict=1):
			frappe.db.sql("update `tabLeave Allocation` set leave_policy_assignment = '{}' where name = '{}'".format(lpa.name, la.name))
			print(str(count)+". "+lpa.employee+" "+str(la.name))
			count += 1


def submit_approved_vehicle_requests():
	# Fetch all Vehicle Request docs with workflow_state='Approved' and docstatus=0
	vehicle_requests = frappe.get_all(
		"Vehicle Request",
		filters={"workflow_state": "Approved", "docstatus": 0},
		fields=["name"]
	)
	for vr in vehicle_requests:
		try:
			doc = frappe.get_doc("Vehicle Request", vr.name)
			doc.submit()
			frappe.db.commit()
			print(f"Submitted Vehicle Request: {vr.name}")
		except Exception as e:
			print(f"Error submitting {vr.name}: {e}")

def update_payment_entry_tax_gl():
	for pe in frappe.db.sql("""
						 select pe.name, ptc.account_head, ptc.party_type, ptc.party from `tabPayment Entry` pe, `tabAdvance Taxes and Charges` ptc where
						 ptc.parent = pe.name and pe.docstatus = 1 and ptc.party is not null
						 """,as_dict=1):
		for gl in frappe.db.get_all("GL Entry", {"voucher_no": pe.name, "account": pe.account_head}):
			if pe.party:
				frappe.db.sql("update `tabGL Entry` set party_type = '{}', party = '{}' where name = '{}'".format(pe.party_type, pe.party, gl.name))
		print(pe.name)

def update_pi_tax_gl():
	for pe in frappe.db.sql("""
						 select pe.name, ptc.account_head, ptc.party_type, ptc.party from `tabPurchase Invoice` pe, `tabPurchase Taxes and Charges` ptc where
						 ptc.parent = pe.name and pe.docstatus = 1 and ptc.party is not null
						 """,as_dict=1):
		for gl in frappe.db.get_all("GL Entry", {"voucher_no": pe.name, "account": pe.account_head}):
			if pe.party:
				frappe.db.sql("update `tabGL Entry` set party_type = '{}', party = '{}' where name = '{}'".format(pe.party_type, pe.party, gl.name))
		print(pe.name)

def update_project_purchase():
	for a in frappe.db.get_all("Purchase Order", {"docstatus":1}, ["status", "name"]):
		po = frappe.get_doc("Purchase Order", a.name)
		project = None
		po_count = pi_count = 1
		for poi in po.items:
			if po_count == 1:
				project = poi.project
			po_count += 1
		frappe.db.sql("update `tabPurchase Order` set project = '{}' where name = '{}'".format(project, a.name))
		for poi in frappe.db.get_all("Purchase Invoice Item", {"purchase_order":a.name}, ["parent"]):
			if project:
				frappe.db.sql("update `tabPurchase Invoice` set project = '{}' where name = '{}'".format(project, poi.parent))
				frappe.db.sql("update `tabGL Entry` set project = '{}' where voucher_no = '{}'".format(project, poi.parent))
				print("poi done")
		for pri in frappe.db.get_all("Purchase Receipt Item", {"purchase_order":a.name}, ["parent"]):
			if project:
				frappe.db.sql("update `tabPurchase Receipt` set project = '{}' where name = '{}'".format(project, pri.parent))
				frappe.db.sql("update `tabGL Entry` set project = '{}' where voucher_no = '{}'".format(project, pri.parent))
				print("pri done")
		print(po.name)

def change_asset_cc():
	# count = 0
	# for a in frappe.db.get_all("Asset", {"disable_depreciation": 1, "value_after_depreciation": [">", 1], "docstatus":1, "disposal_date": None}):
	#	 frappe.db.sql("""
	#				   update `tabAsset` set disable_depreciation = 0, asset_status = NULL where name = '{}'
	#				   """.format(a.name))
	#	 count += 1
	#	 print(str(count)+". "+a.name)
	# print(count)
	df = pd.read_excel(r"/home/frappe/erp/gelephu_asset.xlsx")
	df = df.to_dict()
	row1 = row2 = 0
	count  = 1
	for a in df.get('asset_code'):
		frappe.db.sql("update `tabAsset` set branch = 'GI - Liaison Office Gelephu', cost_center = 'GI - Liaison Office Gelephu - GYALSUNG' where name = '{}'".format(df.get("asset_code")[a]))
		for jea in frappe.db.get_all("Journal Entry Account", {"reference_name": df.get("asset_code")[a], "docstatus": 1}, ["name", "parent"]):
			frappe.db.sql("update `tabJournal Entry Account` set cost_center = 'GI - Liaison Office Gelephu - GYALSUNG' where name = '{}'".format(jea.name))
			if frappe.db.get_value("Journal Entry", jea.parent, "branch") != "GI - Liaison Office Gelephu":
				frappe.db.sql("update `tabJournal Entry` set branch = 'GI - Liaison Office Gelephu' where name = '{}'".format(jea.parent))
				frappe.db.sql("update `tabGL Entry` set cost_center = 'GI - Liaison Office Gelephu - GYALSUNG' where voucher_no = '{}'".format(jea.parent))
		print(str(count)+". "+str(df.get("asset_code")[a]))
		count += 1
		# if df.get('difference')[a]
		# if flt(df.get('Difference')[a])

def ttttttt():
	post_leave_credits()
	print("Done")
def test_test():
	today_date = date.today()
	
	print(today_date)

def add_travel_detail():
	claim_doc=frappe.get_doc("Travel Claim","TC241100003")
	doc=frappe.get_doc("Travel Authorization",'TA241100003-2')

	# for child_doc in claim_doc.get_all_children():
	# 	doc.append("items",
	# 	{
	# 		"idx":child_doc.idx,
	# 		"date":child_doc.date,
	# 		"till_date":child_doc.till_date,
	# 		"halt":child_doc.halt,
	# 		"halt_at":child_doc.halt_at,
	# 		"from_place":child_doc.from_place,
	# 		"to_place":child_doc.to_place,
	# 		"no_days":child_doc.no_days,
	# 		"country":child_doc.country
	# 	})
	# 	doc.save()
	# for child_doc in claim_doc.get_all_children():
		# frappe.db.sql("insert into `tabTravel Authorization Detail`(idx, date, till_date, halt, halt_at, temp_from_place, temp_to_place,no_days) values({},'{}','{}',{},'{}','{}','{}',{})".format(child_doc.idx,child_doc.date,child_doc.till_date,child_doc.halt,child_doc.halt_at,child_doc.from_place,child_doc.to_place,child_doc.no_days,))
	try:
		for child_doc in claim_doc.get_all_children():
			doc.append("details", {
				"date": child_doc.date, 
				"halt": child_doc.halt, 
				"till_date": child_doc.till_date, 
				"no_days": child_doc.no_days, 
				"from_place": child_doc.from_place, 
				"halt_at": child_doc.halt_at
				})	
			doc.save()
	except Exception as e:
		print("error", e)

def get_employees():
	
	query = """
			select e.name as employee, e.employee_name, e.branch, e.designation, e.employment_type, e.grade,
			e.employee_group, e.bank_name, e.bank_ac_no, 
			from `tabEmployee` as e 
			join `tabSalary Structure` as ss on ss.employee=e.name
			
			where e.status = 'Active' limit 3
	"""
	print(str(query))
	
	entries = frappe.db.sql(query, as_dict=True)
	print(entries)

def update_attendance():
	auth_doc=frappe.get_doc("Travel Authorization", "TA241100002-1")
	claim_doc=frappe.get_doc("Travel Claim", "TC241100002")

	for auth in auth_doc.get_all_children():
			if auth.doctype=="Travel Authorization Item":
				if auth.date==auth.till_date:
					frappe.db.sql("update `tabAttendance` set docstatus=2 where attendance_date='{}' and employee='{}'".format(auth.date, auth_doc.employee))
				else:
					all_dates = get_dates_between(auth.date, auth.till_date)
					for date_s in all_dates:
						frappe.db.sql("update `tabAttendance` set docstatus=2 where attendance_date='{}' and employee='{}'".format(date_s.strftime("%Y-%m-%d"), auth_doc.employee))

	# for claim in claim_doc.get_all_children():
	#	 if claim.date==claim.till_date:
	#		 print(claim.date)
	#		 frappe.db.sql("update `tabAttendance` set status='Present' where attendance_date='{}' and employee='{}'".format(claim.date, auth_doc.employee))
	#	 else:
	#		 all_dates = get_dates_between(claim.date, claim.till_date)
	#		 for date_s in all_dates:
	#			 print(date_s.strftime("%Y-%m-%d"))
	#			 frappe.db.sql("update `tabAttendance` set status='Present' where attendance_date='{}' and employee='{}'".format(date_s.strftime("%Y-%m-%d"), auth_doc.employee))

def get_dates_between(start_date, end_date):
	# Convert start_date and end_date to datetime.date if they are strings
	if isinstance(start_date, str):
		start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
	if isinstance(end_date, str):
		end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
	
	dates = []
	current_date = start_date
	while current_date <= end_date:
		dates.append(current_date)
		current_date += timedelta(days=1)
	return dates

def save_emp():
	for emp in frappe.db.sql("select name from `tabEmployee`", as_dict=True):
		# print(emp.name)
		try:
			frappe.delete_doc("Employee", emp.name)
			print("Success")
		except Exception:
			pass
		# # print(doc.designation)
		# # doc.designation=None
		# # # doc.designation=""
		# doc.save()


def clean_designation():
	for emp in frappe.db.sql("select name from `tabEmployee` where designation is not null", as_dict=True):
		doc=frappe.get_doc("Employee", emp.name)
		
		print(doc.designation)
		doc.designation=None
		# doc.designation=""
		doc.save()

	# for des in frappe.db.sql("select name from `tabDesignation`", as_dict=True):
	#	 doc=frappe.delete_doc("Designation", des.name)


def update_asset_journal_entry():
	journal_entries = frappe.db.sql("""
									select name, title from `tabJournal Entry` where creation > '2024-02-01' and title like '%Legacy%'
								or title like '%Accumulated%' and posting_date = '2022-12-31';
									""",as_dict=1)
	for je in journal_entries:
		count = 0
		fixed_asset_account = accumulated_depreciation_account = None
		je = frappe.get_doc("Journal Entry", je.name)
		gles = frappe.db.sql("""
									select name from `tabGL Entry` where voucher_no = '{}'
									""".format(je.name),as_dict=1)
		for d in je.accounts:
			if 'Legacy Clearing' not in d.account and 'Legacy Clearing' in je.title:
				fixed_asset_account = frappe.get_value("Asset Category Account", {"parent":frappe.db.get_value("Asset", d.reference_name, "asset_category")}, "fixed_asset_account")
				frappe.db.sql("""
							  update `tabJournal Entry Account` set account = '{}' where name = '{}'
							  """.format(fixed_asset_account, d.name))
				gle = frappe.db.sql("""
									select name from `tabGL Entry` where account not like '%Legacy Clearing%' and voucher_no = '{}'
									""".format(je.name),as_dict=1)
				if gle:
					frappe.db.sql("""
								update `tabGL Entry` set account = '{}' where name = '{}'
								""".format(fixed_asset_account, gle[0].name))
			if 'Legacy Clearing' not in d.account and 'Accumulated' in je.title:
				accumulated_depreciation_account = frappe.get_value("Asset Category Account", {"parent":frappe.db.get_value("Asset", d.reference_name, "asset_category")}, "accumulated_depreciation_account")
				frappe.db.sql("""
							  update `tabJournal Entry Account` set account = '{}' where name = '{}'
							  """.format(accumulated_depreciation_account, d.name))
				gle = frappe.db.sql("""
									select name from `tabGL Entry` where account not like '%Legacy Clearing%' and voucher_no = '{}'
									""".format(je.name),as_dict=1)
				if gle:
					frappe.db.sql("""
								update `tabGL Entry` set account = '{}' where name = '{}'
								""".format(accumulated_depreciation_account, gle[0].name))

		frappe.db.sql("""
					update `tabJournal Entry` set posting_date = '2023-01-01' where name = '{}'
					  """.format(je.name))
		for gl in gles:
			frappe.db.sql("""
						update `tabGL Entry` set posting_date = '2023-01-01' where name = '{}'
						""".format(gl.name))
		print(je.name)
# def save_asset():
#	 count = 1
# 	assets = frappe.db.sql("""
#						 select name from `tabAsset` where docstatus = 0
#						 """,as_dict=1)
# 	for a in assets:
# 		print(a.name)
# 		asset = frappe.get_doc("Asset", a.name)
# 		asset.save(ignore_permissions=1)
#		 if count % 100 == 0:
#			 frappe.db.commit()
#		 count += 1

def depreciate_asset():
	count=0	
	for a in frappe.db.sql("""
							select name from `tabAsset` where status not in ('Draft', 'Fully Depreciated') and docstatus = 1
							and purchase_date < '2024-01-01'
						   """,as_dict = 1):
		for ds in frappe.db.sql("""
							select d.schedule_date 
							from `tabAsset` a inner join
							`tabDepreciation Schedule` d
							where d.schedule_date <= '2024-01-31'
							and (d.journal_entry is null or d.journal_entry ='')
							and d.parent = '{}' order by d.schedule_date desc limit 1
							""".format(a.name),as_dict=1):
			count+=1
			# make_depreciation_entry(a.name, a.schedule_date)

def change_asset_status():
	asset_id = frappe.db.sql(""" select a.name as asset_name, b.name as book_name from `tabAsset` a inner join `tabAsset Finance Book` b on a.name=b.parent where a.docstatus=1 and a.is_fully_depreciated=0 and b.value_after_depreciation !=1 and b.total_number_of_depreciations < b.total_number_of_booked_depreciations""", as_dict=True)
	count=0
	for row in asset_id:
		count=count+1
		frappe.db.sql("""update `tabAsset Finance Book` set value_after_depreciation=1 where name='{}'""".format(row.book_name))
		frappe.db.sql("""update `tabAsset` set status='Fully Depreciated' where name='{}'""".format(row.asset_name))
		print(row.asset_name)
	print(count)
def delete_asset_related_data():
	# Fetch voucher_no values to delete
	print('STARTED')
	voucher_nos = frappe.db.sql_list("""
		SELECT je.name
		FROM `tabJournal Entry` je, `tabJournal Entry Account` jea 
		WHERE jea.parent=je.name
		AND jea.reference_type = 'Asset'
		GROUP BY je.name
		LIMIT 5000
	""")

	count=0
	
	if not voucher_nos:
		return

	voucher_no_values = ",".join(["'{}'".format(d) for d in voucher_nos])

	# Use a single SQL query to delete related data from all tables
	frappe.db.sql("""
		DELETE gl, jea, je
		FROM `tabGL Entry` gl
		LEFT JOIN `tabJournal Entry Account` jea ON jea.parent = gl.voucher_no
		LEFT JOIN `tabJournal Entry` je ON je.name = jea.parent
		WHERE gl.voucher_no IN ({})
	""".format(voucher_no_values))
	print('DONE')


def delete_cogm_gl():
	# Fetch voucher_no values to delete
	voucher_nos = frappe.db.sql_list("""
		SELECT voucher_no
		FROM `tabGL Entry`
		WHERE account = 'Cost of Goods Manufactured - SMCL' AND posting_date <= '2023-12-31'
		AND is_cancelled = 1
		AND voucher_no LIKE '%%MI%%'
		GROUP BY voucher_no
		LIMIT 1000
	""")

	print(str(voucher_nos))

	# Delete records based on voucher_no
	# count = frappe.db.sql("""
	#	 DELETE FROM `tabGL Entry`
	#	 WHERE voucher_no IN (%s)
	# """ % ', '.join(['%s'] * len(voucher_nos)), tuple(voucher_nos), as_dict=1)

	count = frappe.db.sql("""
		UPDATE `tabGL Entry`
		SET is_cancelled = 0
		WHERE voucher_no IN (%s)
	""" % ', '.join(['%s'] * len(voucher_nos)), tuple(voucher_nos), as_dict=1)

	print("DONE: Cancelled {} records.".format(count))

def delete_mines_inventory_gl():
	accounts = [
		'CDM Warehouse 1 - Mines - SMCL',
		'CDM Warehouse 2 - Crushing & Screen Plant - SMCL',
		'CDM Warehouse 3 - Lhamokhola Crusher - SMCL',
		'CDM Warehouse 4 - Lhamokhola Stockyard - SMCL',
		'Chunaikhola Dolomite Mine Warehouse - SMCL',
		'DSQ Warehouse 1 - Dzongthung Crusher - SMCL',
		'DSQ Warehouse 2 - Dzungdi Crusher - SMCL',
		'Habrang Coal Stockyard - SMCL',
		'Khothakpa Gypsum Mine - SMCL',
		'Majuwa Coal Warehouse - SMCL',
		'Motanga Stockyard - SMCL',
		'Rangia Stockyard - SMCL',
		'Rishore Coal Warehouse - SMCL',
		'Round Off - SMCL',
		'Samdrup Jongkhar Gypsum Stockyard - SMCL',
		'Tshophangma Coal Warehouse - SMCL'
	]

	# Use a single SQL DELETE statement with an IN clause
	# frappe.db.sql("""
	#	 DELETE FROM `tabGL Entry`
	#	 WHERE account IN (%s)
	#	 AND posting_date BETWEEN '2023-01-01' AND '2023-12-31'
	# """ % ', '.join(['%s'] * len(accounts)), tuple(accounts))

	frappe.db.sql("""
		UPDATE `tabGL Entry`
		SET is_cancelled = 1
		WHERE account IN (%s)
		AND posting_date BETWEEN '2023-01-01' AND '2023-12-31'
	""" % ', '.join(['%s'] * len(accounts)), tuple(accounts))

	print('DONE')

def test_bank_payment():
	# ack_file = "/home/frappe/erp/apps/erpnext/PEMSPAY_20231127_SL2023112700000003_VALERR.csv"
	# file_name = 'PEMSPAY_20231127_SL2023112700000003.csv'
	# file_status = 'Failed'
	# bank ='BOBL'
	doc = frappe.get_doc("Bank Payment", "BPO23110306")
	doc.append_bank_response_in_bpi()

#change
def update_salary_structure():
	count = 1
	ss = frappe.db.sql("""
		select ss.name, ss.employee_grade, ss.employment_type, ss.employee_group from `tabSalary Structure` ss,
		`tabEmployee` e where e.name = ss.employee
		and e.status = 'Active' and ss.is_active = 'Yes'
	""",as_dict=1)
	if ss:
		for s in ss:
			sal_struct = frappe.get_doc("Salary Structure", s.name)
			if s.employee_group not in ("Temporary"):
				sal_struct.eligible_for_fixed_allowance = 1
				sal_struct.eligible_for_cash_handling = 0
				for e in sal_struct.earnings:
					if e.salary_component == "Basic Pay":
						if s.employee_grade not in ("S1","S2","S3","O1","O2","O3","O4","O5","O6","O7","GS1","GS2","ESP"):
							e.amount += e.amount * 0.02
						else:
							e.amount += e.amount * 0.05
						e.amount = flt(e.amount,0)
						e.amount = math.ceil(e.amount)
						if flt(str(e.amount)[len(str(e.amount))-1]) > 0 and flt(str(e.amount)[len(str(e.amount))-1]) <= 5:
							e.amount = flt(str(e.amount)[0:len(str(e.amount))-1]+"5")
						elif flt(str(e.amount)[len(str(e.amount))-1]) > 5 and flt(str(e.amount)[len(str(e.amount))-1]) <= 9:
							value_to_add = 10 - flt(str(e.amount)[len(str(e.amount))-1])
							e.amount = e.amount + value_to_add
				sal_struct.save(ignore_permissions=1)
				print(str(count)+". "+sal_struct.employee)
				count += 1

def check_dn():
	doc = frappe.get_doc("Delivery Note","DN2304050001")
	doc.make_gl_entries()

def update_sle_gl():
	i = 0
	production = []
	for a in frappe.db.sql("""select name, actual_qty, incoming_rate,
								valuation_rate, qty_after_transaction,
								stock_value_difference, stock_value, voucher_no
								from `tabStock Ledger Entry` 
								where voucher_type="Production"
								and posting_date between '2023-07-31' and '2023-08-28' 
								and is_cancelled=0
								order by posting_date, posting_time
							""", as_dict=True):
		stock_value = abs(a.qty_after_transaction) * a.valuation_rate
		rate = abs(a.incoming_rate) if a.actual_qty > 0 else abs(a.valuation_rate)
		stock_value_difference = abs(a.actual_qty) * rate 
		val_diff = flt(abs(a.stock_value_difference) - stock_value_difference,2)
		val = flt(a.stock_value - stock_value,2)

		act_stock_value = stock_value if val > 1 or val < -1 else a.stock_value
		act_stock_value_diff = stock_value_difference if val_diff > 1 or val_diff < -1 else a.stock_value_difference
		if val_diff > 1 or val_diff < -1 or val > 1 or val < -1:
			i += 1
			if a.voucher_no not in production:
				production.append(a.voucher_no)
			print(i, a.voucher_no)
			frappe.db.sql("""  update `tabStock Ledger Entry`
				set stock_value='{}', stock_value_difference='{}'
				where name ='{}'
			""".format(act_stock_value, act_stock_value_diff, a.name))
	j=0
	for b in production:
		j+=1
		print(j, b, i)
		frappe.db.sql("delete from `tabGL Entry` where voucher_type='Production' and voucher_no='{}'".format(b))
		doc = frappe.get_doc("Production", b)
		doc.make_gl_entries()
		print("Done for Production No: " + str(b))
	frappe.db.commit()

def correct_dn():
	for b in ("DN2302070020",):
		frappe.db.sql("delete from `tabGL Entry` where voucher_type='Delivery Note' and voucher_no='{}'".format(b))
		for a in frappe.db.sql("""select name, actual_qty, incoming_rate,
									valuation_rate, qty_after_transaction
									from `tabStock Ledger Entry` 
									where voucher_no="{}"
								""".format(b), as_dict=True):
			stock_value = a.qty_after_transaction * a.valuation_rate
			stock_value_difference = a.actual_qty * a.incoming_rate
			
			frappe.db.sql("""  update `tabStock Ledger Entry`
							set stock_value='{}', stock_value_difference='{}'
							where name ='{}'
						""".format(stock_value, stock_value_difference, a.name))
			
		doc = frappe.get_doc("Delivery Note", b)
		doc.make_gl_entries()
		frappe.db.commit()
		print("Done for DN No: " + str(b))


def get_wrong_dn():
	i=0
	for a in frappe.db.sql("""
					select is_cancelled docstatus, voucher_no, credit, posting_date, account from `tabGL Entry`
					where voucher_type="Delivery Note"
					and account="Cost of Goods Manufactured - SMCL"
					and credit > 0
					and is_cancelled = 0
					order by posting_date 
				""", as_dict=True):
		i+=1
		print(str(i) + ", " + str(a.voucher_no))
		
def rename_asset():
	i = 0
	abbr = "SMCL-BCS-23-"
	for d in frappe.db.sql("select name, asset_category, creation from `tabAsset` \
			where asset_category in ('Building & Civil Structure') and docstatus = 0 order by creation",as_dict=True):
		name  = ""
		if len(str(i)) == 1:
			name = abbr +"000"+ str(i)
		elif len(str(i)) == 2:
			name = abbr +"00"+ str(i)
		elif len(str(i)) == 3:
			name = abbr +"0"+ str(i)
		else:
			name = abbr + str(i)
			
		print(name)
		i += 1
def delete_asset_gl():
	for d in frappe.db.sql("select name, asset_category from `tabAsset` \
			where asset_category in ('Furniture & Fixture', 'Plant & Machinery','Building & Civil Structure') and docstatus = 2",as_dict=True):
		frappe.db.sql("delete from `tabGL Entry` where against_voucher_type='Asset' and against_voucher= '{}'".format(d.name))
		for je in frappe.db.sql("select distinct(parent) as name from `tabJournal Entry Account` where reference_name= '{}'".format(d.name),as_dict=1):
			je_doc = frappe.get_doc("Journal Entry",je.name)
			print(je_doc.name)
			je_doc.delete()
	# 	asset = frappe.get_doc("Asset",d.name)
	# 	print(asset.name, ' ',asset.asset_category,' ', asset.docstatus)
	# 	asset.cancel()
	print("Done")
	frappe.db.commit()
def detete_pol_receive_gl():
	name = frappe.db.sql("""select name
			from `tabPOL Receive`
			where direct_consumption=1
			and use_common_fuelbook =1
			and is_opening =0
			and docstatus=1
		""",as_dict=True)
	for x in name:
		frappe.db.sql("delete from `tabGL Entry` where against_voucher_type='POL Receive' and against_voucher= '{}'".format(x.name))
		print(x.name)
def pol_issue_double_equipment_issue():
	from_date = '01-01-2023'
	to_date = '11-10-2023'
	name=frappe.db.sql("""
			select name
			from `tabPOL Issue`
			where docstatus =1
			and posting_date between '{0}' and '{1}'
		""".format(from_date, to_date),as_dict=True)
	print(name)
def create_pol_receive_gl():
	name = frappe.db.sql("""select name
			from `tabPOL Receive`
			where direct_consumption=1
			and use_common_fuelbook =1
			and is_opening =0
			and docstatus=1
		""",as_dict=True)
	for x in name:
		gl_entry = frappe.db.sql("select name from `tabGL Entry` where against_voucher_type='POL Receive' and against_voucher= '{}'".format(x.name))
		if gl_entry:
			print(gl_entry)
		else:
			doc = frappe.get_doc("POL Receive",x.name)
			doc.make_gl_entries()
			print(doc.name)
	frappe.db.commit()

def find_transaction_with_cancelled_gl():
	
	name = frappe.db.sql("""select name
			from `tabDelivery Note`
			where docstatus=1
		""",as_dict=True)
	
	for x in name:
		print(str(name))
		gl_entry = frappe.db.sql("select name from `tabGL Entry` where voucher_no='{}' and is_cancelled=1 ".format(x.name))
		if gl_entry:
			print(x.name)
	   


def pol_entry_correction():
	for d in frappe.bd.sql("select name,reference_type,reference,equipment from `tabPOL Entry` where rate <= 0"):
		if d.reference_type == "POL Receive":
			doc = frappe.get_doc(d.reference_type,d.reference)
			if doc.name:
				frappe.db.sql('''
					update `tabPOL Entry` set fuelbook = '{}', supplier='{}', item_name='{}',
					memo_number = '{}', pol_slip_no = '{}', mileage = '{}', km_difference = '{}',
					current_km = '{}', rate = {} where name = '{}'
					'''.format(doc.fuelbook,doc.supplier,doc.item_name, doc.memo_number, 
				doc.pol_slip_no, doc.mileage, doc.km_difference, doc.cur_km_reading, doc.rate, d.name))
		elif d.reference_type == "POL Issue":
			doc = frappe.get_doc("POL Issue Items",{"parent":d.reference,"equipment":d.equipment})
			if doc.name:
				frappe.db.sql('''
					update `tabPOL Entry` set fuelbook = '{}', mileage = '{}', km_difference = '{}',
					current_km = '{}', rate = {} where name = '{}' and equipment = '{}'
					'''.format(doc.fuelbook, doc.mileage, doc.km_difference, doc.cur_km_reading, doc.rate, d.name, doc.equipment))
	
def cost_center_correction_budget():
	for d in frappe.db.get_list("Committed Budget",filters={"reference_type":"Journal Entry"},fields=["cost_center","name"]):
		parent_cost_center = frappe.db.get_value("Cost Center",{"name":d.cost_center,"use_budget_from_parent":1},["budget_cost_center"])
		if parent_cost_center:
			frappe.db.sql("update `tabCommitted Budget` set cost_center = '{}' where name = '{}'".format(parent_cost_center,d.name))
			print(d.cost_center,' ',d.name)
	print('<===================================================>')
	for d in frappe.db.get_list("Consumed Budget",filters={"reference_type":"Journal Entry"},fields=["cost_center",'name']):
		parent_cost_center = frappe.db.get_value("Cost Center",{"name":d.cost_center,"use_budget_from_parent":1},["budget_cost_center"])
		if parent_cost_center:
			frappe.db.sql("update `tabConsumed Budget` set cost_center = '{}' where name = '{}'".format(parent_cost_center,d.name))
			print(parent_cost_center,' ',d.name)
	print('done')
	frappe.db.commit()

def create_gl_for_previous_production():
	for p in frappe.db.get_list("Production",filters={"creation":["<=","2023-03-02"],"docstatus":1}, fields=["name","creation"]):
		doc = frappe.get_doc("Production",p.name)
		if len(doc.raw_materials) > 0:
			frappe.db.sql("delete from `tabGL Entry` where voucher_no = '{}' and voucher_type = 'Production'".format(doc.name))
			doc.make_gl_entries()
			print(doc.name)
	frappe.db.commit()
	print('done')
def create_leave_ledger_entry():
	for e in frappe.db.sql('''select name from `tabEmployee` where status = "Active"''',as_dict=1):
		if frappe.db.exists("Leave Allocation",{"employee":e.name,"leave_type":"Earned Leave","docstatus":1}):
			leave_allocation = frappe.get_doc("Leave Allocation",{"employee":e.name,"leave_type":"Earned Leave","docstatus":1})
			print(leave_allocation.employee, ' : ', leave_allocation.name, ' : ', leave_allocation.leave_type)
			leave_ledger_entry = frappe.new_doc("Leave Ledger Entry")
			leave_ledger_entry.flags.ignore_permissions=1
			leave_ledger_entry.update({
				"employee":leave_allocation.employee,
				"employee_name":leave_allocation.employee_name,
				"leave_type":leave_allocation.leave_type,
				"transaction_type":"Leave Allocation",
				"transaction_name":leave_allocation.name,
				"leaves":2.5,
				"company":leave_allocation.company,
				"from_date":"2023-01-01",
				"to_date":'2023-12-31'
			})
			leave_ledger_entry.insert()
			leave_ledger_entry.submit()

# def post_payment_je_leave_encashment():
#	 le = frappe.db.sql("""
#		 select expense_claim from `tabLeave Encashment` where
#		 docstatus = 1
#	 """,as_dict=1)
#	 for a in le:
#		 expense_claim = frappe.get_doc("Expense Claim", a.expense_claim)
#		 if expense_claim.docstatus = 1:
#			 expense_claim.post_accounts_entry()
#			 print(expense_claim.name)
#	 frappe.db.commit()

def change_account_name():
	# print('here')
	for d in		[
					{
					"old_name": "Tshophhangma Consumable Warehouse",
					"new_name": "Tshophangma Consumable Warehouse - SMCL"
					}
					]:
		if frappe.db.exists("Account",{"account_name":d.get("old_name")}):
			doc = frappe.get_doc("Account",{"account_name":d.get("old_name")})
			print('old : ',doc.account_name,'\nNew Name : ' ,d.get("new_name"))
			doc.account_name = d.get("new_name")
			doc.save()

def assign_je_in_invoice():
	print('<------------------------------------------------------------------------------------------------>')
	for d in frappe.db.sql('''
				select reference_name, reference_type, parent from `tabJournal Entry Account` where reference_type in ('Transporter Invoice','EME Invoice')
				''', as_dict=True):
		if d.reference_type and d.reference_name and frappe.db.exists(d.reference_type, d.reference_name):
			doc = frappe.get_doc(str(d.reference_type),str(d.reference_name))
			doc.db_set("journal_entry",d.parent)
	print('Done')
def assign_ess_role():
	users = frappe.db.sql("""
		select name from `tabUser` where name not in ('Guest', 'Administrator')
	""",as_dict=1)
	for a in users:
		user = frappe.get_doc("User", a.name)
		user.flags.ignore_permissions = True
		if "Employee Self Service" not in frappe.get_roles(a.name):
			user.add_roles("Employee Self Service")
			print("Employee Self Service role added for user {}".format(a.name))


def delete_salary_detail_salary_slip():
	ssd = frappe.db.sql("""
		select name from `tabSalary Detail` where parenttype = 'Salary Slip'
	""",as_dict=1)
	for a in ssd:
		frappe.db.sql("delete from `tabSalary Detail` where name = '{}'".format(a.name))
		print(a.name)

def create_users():
	print("here")

	employees = frappe.db.sql("""
		select name from `tabEmployee` where company_email is not NULL and user_id is NULL
	""",as_dict=1)
	if employees:
		for a in employees:
			employee = frappe.get_doc("Employee", a.name)
			if not frappe.db.exists("User",employee.company_email):
				create_user(a.name, email = employee.company_email)
				print("User created for employee {}".format(a.name))
				employee.db_set("user_id", employee.company_email)
	frappe.db.commit()

def update_employee_user_id():
	print()
	users = frappe.db.sql("""
		select name from `tabUser`
	""",as_dict=1)
	if users:
		for a in users:
			employee = frappe.db.get_value("Employee",{"company_email":a.name},"name")
			if employee:
				employee_doc = frappe.get_doc("Employee",employee)
				employee_doc.db_set("user_id",a.name)
				print("Updated email for "+str(a.name))
	frappe.db.commit()

def update_benefit_type_name():
	bt = frappe.db.sql("""
		select name, benefit_type from `tabEmployee Benefit Type`;
	""", as_dict=True)
	if bt:
		for a in bt:
			frappe.db.sql("update `tabEmployee Benefit Type` set name = '{}' where name = '{}'".format(a.benefit_type, a.name))
			print(a.name)

def update_department():
	el = frappe.db.sql("""
		select name from `tabEmployee`
		where department = 'Habrang & Tshophangma Coal Mine - SMCL'
		and status = 'Active'
	""",as_dict=1)
	if el:
		for a in el:
			frappe.db.sql("""
				update `tabEmployee` set department = 'PROJECTS & MINES DEPARTMENT - SMCL'
				where name = '{}'
			""".format(a.name))
			print(a.name)

def update_user_pwd():
	user_list = frappe.db.sql("select name from `tabUser` where name not in ('Administrator', 'Guest')", as_dict=1)
	c = 1
	non_employee = []
	for i in user_list:
		print("NAME '{}':  '{}'".format(c,str(i.name)))
		if not frappe.db.exists("Employee", {"user_id":i.name}):
			non_employee.append({"User ID":i.name, "User Name":frappe.db.get_value("User",i.name,"full_name")})
		ds = frappe.get_doc("User", i.name)
		ds.new_password = 'erp@2024'
		ds.save(ignore_permissions=1)
		c += 1
	# df = pd.DataFrame(data = non_employee) # convert dict to dataframe
	# df.to_excel("Users Without Employee Data.xlsx", index=False)
	# print("Dictionery Converted in to Excel")

def update_ref_doc():
	for a in frappe.db.sql("""
							select name 
							from 
								`tabExpense Claim` 
							where 
								docstatus != 2
							"""):
		print(a[0])
		reference = frappe.db.sql("""
							select expense_type
							from 
								`tabExpense Claim Detail` 
							where 
							parent = "{}"
							""".format(a[0]))
		print(reference[0][0])
		frappe.db.sql("""
			update 
				`tabExpense Claim`
			set ref_doc ="{0}"
			where name ="{1}"
		""".format(reference[0][0],a[0]))

	
def update_overtime_application_in_ss():
	with open("/home/frappe/erp/apps/Overtime.csv") as f:
		reader = csv.reader(f)
		mylist = list(reader)
		c = 0
		for i in mylist:
			ss = frappe.db.sql("select name, employee, employee_name, branch, is_active from `tabSalary Structure` where employee='{}'and name='{}'".format(i[1], i[0]), as_dict=1)		
			for d in ss:
				ss_doc = frappe.get_doc("Salary Structure", {"name": d.name})
				if ss_doc.employee == i[1]:
					row = ss_doc.append('earnings',{})
					row.salary_component = "Overtime Allowance"
					row.amount = flt(i[3])
					row.from_date = "2023-04-01"
					row.to_date = "2023-04-30"
				ss_doc.save(ignore_permissions=True)
				
				# rem_list = []
				# for a in ss_doc.get("earnings"):
				# 	if ss_doc.employee == i[1] and a.salary_component == "Overtime Allowance":
				# 		rem_list.append(a)

				# [ss_doc.remove(a) for a in rem_list]
				# ss_doc.save(ignore_permissions=True)
			c += 1
		print('DONE')
		print(str(c))


def earned_leave_deletion_manual():
	count=0
	for d in frappe.db.sql("select name, employee, from_date, leaves, transaction_name from `tabLeave Ledger Entry` where from_date='2023-06-21'", as_dict=1):
		# print(str(d.transaction_name))	
		# print(str(d.from_date))	
		leave_all = frappe.get_doc("Leave Allocation", d.transaction_name)
		leave_all.total_leaves_allocated = flt(leave_all.total_leaves_allocated) - flt(2.5)
		leave_all.save(ignore_permissions=True)
		frappe.db.sql("delete from `tabLeave Ledger Entry` where from_date='2023-06-21' and name='{}'".format(d.name))
		count+=1
	print(str(count))

# def update_sales_target():
# 	name= frappe.db.sql(""" 
# 			select name from `tabSales Target Item` where parent="Dolomite-2022-2036"
# 		""")
# 	frappe.print(str(name))
	
def delivery_note_gl_correction():
	# name = ["DN2302100195-1","DN2302170551","DN2302170624","DN2303010130","DN2303010518","DN2303010549","DN2303030567","DN2303110492","DN2306150492","DN2306190574","DN2306290125","DN2306300067","DN2306300218","DN2306300275","DN2306300304","DN2306300350","DN2306300354"]
	# name = ["DN2307050440","DN2307050550","DN2307060124","DN2307060204","DN2307130051","DN2307130058","DN2307130081","DN2307140140","DN2307200109","DN2310120416","DN2310130582","DN2311060206","DN2311220002"]
	name = ["DN2312070608","DN2312080182","DN2312080524","DN2312110196","DN2312110574","DN2312110577","DN2312130221","DN2312260474","DN2312280183","DN2312280221","DN2312280286","DN2312280306","DN2312290223","DN2312290267","DN2312300175","DN2312300245"]
	for x in name:
		gl_entry = frappe.db.sql("""select name
			from `tabGL Entry`
			where voucher_no='{vn}' 
			and is_cancelled=1
		""".format(vn=x),as_dict=True)
		for y in gl_entry:
			frappe.db.sql("update`tabGL Entry`set is_cancelled =0 where name='{}' ".format(y.name))
	

def production_note_gl_correction():
	name = frappe.db.sql("""
		select name 
		from `tabDelivery Note`
		where docstatus=1
	""",as_dict=1)
	for x in name:
		gl_entry = frappe.db.sql("""select name
			from `tabGL Entry`
			where voucher_no='{vn}' 
			and is_cancelled=1
		""".format(vn=x.name),as_dict=True)
		if gl_entry:
			print(x.name)
		# for y in gl_entry:
			# frappe.db.sql("update`tabGL Entry`set is_cancelled =0 where name='{}' ".format(y.name))
def repair_and_services_update_invoice():
	name = frappe.db.sql("""
		select repair_and_services
		from `tabRepair And Service Invoice`
		where docstatus=1
	""",as_dict=1)
	for x in name:
		if x.repair_and_services:
			frappe.db.sql("""Update `tabRepair And Services`
				set invoice_created=1
				where name='{}'
			""".format(x.repair_and_services))
			print(x.repair_and_services)
def update_user_pwd():
	user_list = frappe.db.sql("select name from `tabUser` where name not in ('Administrator')", as_dict=1)
	c = 1
	# print(user_list)
	for i in user_list:
		print("NAME '{}':  '{}'".format(c,str(i.name)))
		ds = frappe.get_doc("User", i.name)
		ds.new_password = 'erp@2025'
		ds.save(ignore_permissions=1)
		c += 1

def make_for_project_req():
	st_id = frappe.db.sql("""select s.name
		from `tabStock Entry` s
		inner join `tabStock Entry Detail` si
		on s.name=si.parent 
		where s.docstatus!=2
		and s.project is not NULL
		and s.for_project =0
		""", as_dict=True)
	
	for row in st_id:
		frappe.db.sql("""update `tabStock Entry` set for_project=1 where name='{name}'""".format(name=row.name))
		print(row.name)

def update_tax_witholding_in_mp():
	mid = frappe.db.sql("""select name, tds_account, tds_amount, tax_withholding_category
		from `tabMechanical Payment` 
		where docstatus!=2
		and tds_amount >0
		""", as_dict=True)
	count =0
	for row in mid:
		if not row.tax_withholding_category:
			# if row.tds_account=="L202030003 - TDS (5%) - GYALSUNG":
			count = count+1
			# 	frappe.db.sql("""update `tabMechanical Payment` set tax_withholding_category='TDS - 5%' where name='{name}'""".format(name=row.name))
			print(row.name)
	print(count)
def submit_stock_entry():
	doc = frappe.get_doc("Stock Entry", "SEMI25034518")
	doc.submit()
	frappe.db.commit()
	print('done')

def create_attendance_for_approved_travel_request():
	name = frappe.db.sql("""
		select name
		from `tabTravel Request`
		where docstatus=1
		and purpose_of_travel !='Training'
	""",as_dict=1)
	for x in name:
		print(x.name)
		doc = frappe.get_doc("Travel Request", x.name)
		d = getdate(doc.itinerary[0].from_date)
		if doc.itinerary[len(doc.itinerary) - 1].halt and doc.itinerary[len(doc.itinerary) - 1].to_date:
			e = getdate(doc.itinerary[len(doc.itinerary) - 1].to_date)
		else:
			e = getdate(doc.itinerary[len(doc.itinerary) - 1].from_date)
		days = date_diff(e, d) + 1
		for a in (d + timedelta(n) for n in range(days)):
			al = frappe.db.sql("select name from tabAttendance where docstatus = 1 and employee = %s and attendance_date = %s", (doc.employee, a), as_dict=True)
			if al:
				doc = frappe.get_doc("Attendance", al[0].name)
				doc.flags.ignore_permissions = 1
				doc.cancel()

			attendance = frappe.new_doc("Attendance")
			attendance.flags.ignore_permissions = 1
			attendance.employee = doc.employee
			attendance.employee_name = doc.employee_name 
			attendance.attendance_date = a
			attendance.status = "Tour"
			# attendance.branch = doc.branch
			attendance.company = frappe.db.get_value("Employee", doc.employee, "company")
			attendance.reference_name = doc.name
			attendance.submit()

def make_aob_je():
	doc = frappe.get_doc("Abstract Bill", "AOB2024070001")
	doc.post_journal_entry()


def create_branch_from_cc():

	for cc in frappe.db.sql("""select * from `tabCost Center` where is_group=0""", as_dict=True):
	#	 print(cc.name)
		# doc = frappe.get_doc("Cost Center", cc.name)
		# doc.on_update()
		# print("done")
		doc = frappe.new_doc("Branch")
		doc.branch = cc.cost_center_name.strip()
		doc.cost_center = cc.name
		doc.company = cc.company
		doc.save()
	print("DONE")

def create_asset_receive():
	doc = frappe.get_doc("Purchase Receipt", "MAT-PRE-2024-00018")
	doc.update_asset_receive_entries()
	
def post_pol_gl():
	count = 0
	for d in frappe.db.sql("select * from `tabPOL Receive` where docstatus=1 and is_opening='Yes' and book_type='Common' and name not in ('POLR-25-02-12-2420-1')", as_dict=1):
		print(d.name)
		count += 1
		doc = frappe.get_doc("POL Receive", d.name)
		# doc.update_stock_ledger()
		doc.make_gl_entries()
	print(count)

def update_attendance_others_branch():
	aat_oth = frappe.db.sql("""select name
		from `tabAttendance Others`  
		where docstatus!=2
		and branch='GI - Khotokha'
		""", as_dict=True)
	count =0
	for row in aat_oth:
		count = count +1
		frappe.db.sql("""update `tabAttendance Others` set branch='Gyalsup for Gyalsung (GI-K)', cost_center='Gyalsup for Gyalsung (GI-K) - GYALSUNG' where name='{name}'""".format(name=row.name))
		print(row.name)
	print(count)

def update_hsd_account():
	aat_oth = frappe.db.sql("""select name
		from `tabHire Charge Invoice`
		where docstatus!=0
		""", as_dict=True)
	count =0
	for row in aat_oth:
		# count = count +1
		gl_l=frappe.db.sql("""select name
		from `tabGL Entry`
		where voucher_no='{v_no}'
		and account='E202040003 - HSD - Machinery Equipment - GYALSUNG'
		""".format(v_no=row.name), as_dict=True)

		for g in gl_l:
			count = count +1
			frappe.db.sql("""update `tabGL Entry` set account='E202040002 - Hire Charges for Machinery  Equipment - GYALSUNG' where name='{name}'""".format(name=g.name))
			print(row.name)
	print(count)

def check_stock_ledger_diff():
	st_id = frappe.db.sql("""select name, actual_qty, valuation_rate, stock_value_difference
		from `tabStock Ledger Entry`
		where item_code ='100143'
		""", as_dict=True)
	# print(st_id)
	count =0
	for row in st_id:
		acutal_value = flt(row.actual_qty)*flt(row.valuation_rate)
		difference_value = flt(acutal_value) - flt (row.stock_value_difference)
		if difference_value > 1 or difference_value < -1:
			count = count + 1
			print(row.name)
	print(count)

def find_wrong_balance_val_100143():
	count = 1
	sles = []
	psvd_count = psv_count = nsvd_count = nsv_count = 1
	opening = frappe.db.sql("""
		select qty_after_transaction, stock_value, valuation_rate 
		from `tabStock Ledger Entry` 
		where warehouse = 'GI - Pemathang - GYALSUNG' 
		and item_code = '100143' and year(posting_date) < 2026 
		and is_cancelled = 0 order by timestamp(posting_date, posting_time) desc limit 1
		""",as_dict=1)
	if len(opening) > 0:
		previous_stock_value = opening[0].stock_value
		previous_valuation_rate = opening[0].valuation_rate
		qty_after_transaction = opening[0].qty_after_transaction
	else:
		previous_stock_value = 0
		previous_valuation_rate = 0
		qty_after_transaction = 0
	print(opening)

def update_assets():
	with open("/home/frappe/erp/scrap_gi_asset.csv") as f:
		reader = csv.reader(f)
		mylist = list(reader)
		c = 0
		for i in mylist:
			# if c == 23:
			# 	break

			if 'Scrapped' == frappe.db.get_value('Asset', i[0], 'status'):
				continue

			dep_schedule = frappe.db.get_all('Depreciation Schedule',
								filters = {
									'docstatus': 1,
									'parent': frappe.db.get_value('Asset Depreciation Schedule',
													{
														'docstatus': 1,
														'asset': i[0]
													},
													'name'
												),
									'schedule_date': ['>=', '2024-12-31'],
									'journal_entry': ['!=', '']
								},
								fields = ['idx', 'journal_entry', 'schedule_date', 'name'],
								order_by='idx desc'
							)
			if dep_schedule:
				for d in dep_schedule:
					if getdate(d.schedule_date) > getdate('2024-12-31'):
						frappe.db.sql("delete from `tabJournal Entry Account` where parent='{}'".format(d.journal_entry))
						frappe.db.sql("delete from `tabJournal Entry` where name='{}'".format(d.journal_entry))
						frappe.db.sql("delete from `tabGL Entry` where voucher_no='{}'".format(d.journal_entry))
						frappe.db.sql("update `tabDepreciation Schedule` set journal_entry=Null where name='{}'".format(d.name))
						# print("dec")
						# print(f"{d.idx} - {d.journal_entry} - {d.schedule_date}")
					# else:
					# 	print("others")
						# print(f"{d.idx} - {d.journal_entry} - {d.schedule_date}")

			frappe.db.sql("update tabAsset set status='Scrapped', disable_depreciation=1 where name='{}'".format(i[0]))
			c += 1
			# print(i[0])
		print('DONE')
		print(str(c))

def remove_asset():
	with open("/home/frappe/erp/Bomzang.csv") as f:
		reader = csv.reader(f)
		mylist = list(reader)
		c = 0
		for i in mylist:
			c+=1
			assetName = str(i[0])
			print(assetName)
			frappe.db.sql("delete from `tabAsset Activity` where asset='{}'".format(assetName))

			for d in frappe.db.sql("""select distinct(parent) as je from `tabJournal Entry Account` 
				where reference_name = '{0}' and reference_type = 'Asset'""".format(assetName), as_dict=1):
				# print(d.je)
				frappe.db.sql("delete from `tabGL Entry` where voucher_no='{}'".format(d.je))
				frappe.db.sql("delete from `tabJournal Entry Account` where parent='{}'".format(d.je))
				frappe.db.sql("delete from `tabJournal Entry` where name = '{}'".format(d.je))

			for ad in frappe.db.sql("""select * from `tabAsset Depreciation Schedule` 
				where asset='{0}'""".format(assetName), as_dict=1):
				# print(ad.name)
				frappe.db.sql("delete from `tabDepreciation Schedule` where parent='{}'".format(ad.name))
				frappe.db.sql("delete from `tabAsset Depreciation Schedule` where name='{}'".format(ad.name))

			for am in frappe.db.sql("""select distinct(parent) as parent from `tabAsset Movement Item` 
				where asset='{0}'""".format(assetName), as_dict=1):
				# print(am.parent)
				frappe.db.sql("delete from `tabAsset Movement Item` where parent='{}'".format(am.parent))
				frappe.db.sql("delete from `tabAsset Movement` where name='{}'".format(am.parent))
				
			frappe.db.sql("delete from `tabAsset Finance Book` where parent='{}'".format(assetName))
			# frappe.db.sql("delete from `tabAsset` where name='{}'".format(assetName))

			frappe.db.sql("update `tabAsset` set docstatus=0, status='Draft', disable_depreciation=0 where name='{}'".format(assetName))
		print(c)
def get_metabase_iframe_link():
	import jwt
	import time

	METABASE_SITE_URL = "https://erp.ns.bt/metabase"
	METABASE_SECRET_KEY = "f71dae595b626196b8ba5394e2f18646d14cc7b17fb859edfc15d2b330ef72ae"

	payload = {
	"resource": {"dashboard": 3},
	"params": {
		
	},
	# "exp": round(time.time()) + (60 * 10) # 10 minute expiration
	}
	token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")

	iframeUrl = METABASE_SITE_URL + "/embed/dashboard/" + token + "#theme=night&bordered=true&titled=true"
	
	print(iframeUrl)

def check_hsd_transaction_exist():
	aat_oth = frappe.db.sql("""select voucher_no
		from `tabStock Ledger Entry`
		where is_cancelled=0
		and voucher_type='Stock Entry'
		""", as_dict=True)
	count =0
	for row in aat_oth:
		test_tar = frappe.db.sql("""select branch
				from `tabStock Entry` 
				where name='{}'
			""".format(row.voucher_no))
		if not test_tar:
			count =count +1
	print(count)

def update_imprest_account():
	aat_oth = frappe.db.sql("""select name, branch
		from `tabImprest Recoup`
		where docstatus=1
		""", as_dict=True)
	count =0
	for row in aat_oth:
		count =count +1
		account_expense = frappe.db.get_value("Branch", row.branch, "expense_bank_account")
		if account_expense:
			frappe.db.sql("""update `tabImprest Recoup` set expense_account='{account}' where name='{name}'""".format(account=account_expense, name=row.name))
			print(row.name)
	print(count)

def check_project_material_exist():
	stock_entry= frappe.db.sql("""select t.name, t.reference_type, t.reference_name
		from `tabTask Material Item` t
		inner join `tabStock Entry` s
		on t.reference_name = s.name
		where s.docstatus =2
		and t.reference_type='Stock Entry'
		""", as_dict=True)
	if stock_entry:
		print(stock_entry)
def update_imprest():
	doc = frappe.get_doc("Imprest Recoup","IMR2025000054")
	doc.submit()
	print("done")

def change_is_existing_asset_credit_account():
	asset_id= frappe.db.sql("""select name
		from `tabAsset`
		where docstatus =1
		and is_existing_asset = 1
		and status !='Fully Depreciated'
		and name not in ('ASSET220500787','ASSET221200001')
		and credit_account = 'A202024001 - Stock Assets - GYALSUNG' 
		""", as_dict=True)
	count = 0
	j_count =0
	for row in asset_id:
		count=count + 1
		# journal_entry = frappe.db.sql("""select je.name as je_name, jea.name as jea_name
		# 	from `tabJournal Entry` je
		# 	inner join `tabJournal Entry Account` jea
		# 	on je.name = jea.parent
		# 	where jea.reference_type = 'Asset'
		# 	and jea.reference_name='{}'
		# 	and jea.account = 'A202024001 - Stock Assets - GYALSUNG'
		# 	and je.docstatus = 1
		# 	""".format(row.name),as_dict=True)
		# for j in journal_entry:
			# gl_id= frappe.db.sql("""select name
			# 	from `tabGL Entry`
			# 	where voucher_no = '{v_no}'
			# 	and voucher_type = 'Journal Entry'
			# 	and is_cancelled = 0
			# 	and account = 'A202024001 - Stock Assets - GYALSUNG'
			# 	""".format(v_no=j.je_name), as_dict=True)

			# for gl in gl_id:
			# 	frappe.db.sql("""update `tabGL Entry` set account='Legacy Clearing Account - GYALSUNG' where name='{name}'""".format(name=gl.name))
			# 	print(gl.name)
			
			# frappe.db.sql("""update `tabJournal Entry Account` set account='Legacy Clearing Account - GYALSUNG' where name='{name}' and parent='{parent}'""".format(name=j.jea_name, parent=j.je_name))
			# print(j.je_name)
		
		frappe.db.sql("""update `tabAsset` set credit_account='Legacy Clearing Account - GYALSUNG' where name='{name}'""".format(name=row.name))
		
		# j_count = j_count + 1
	# print(j_count)
	print(count)

def update_hsd_fuelbook():
	pol_receive = frappe.db.sql("""
		select name from `tabPOL Receive`
		where docstatus !=2
		and fuelbook='16053-6(Petrol)'
		and pol_type='100143'
		and branch = 'GI - Gyalposhing - GYALSUNG'
		and equipment = 'EQUIP251479'
	""", as_dict=True)
	count = 0
	for raw in pol_receive:
		count = count + 1
		print(raw.name)	
	print(count)

def repost_job_cards_gl():
	job_card_id = frappe.db.sql("""select name
		from `tabJob Cards`
		where docstatus=1
		and total_amount > 0
	""",as_dict=True)
	count=0
	for x in job_card_id:
		gl_entry = frappe.db.sql("select name from `tabGL Entry` where voucher_type='Job Cards' and voucher_no= '{}'".format(x.name), as_dict=True)
		if not gl_entry:
			count = count+ 1
			doc = frappe.get_doc("Job Cards", x.name)
			doc.make_gl_entries()
			frappe.db.commit()
			print(x.name)
	print(count)
	
def repost_journal_entry_workflow_state():
	journal_entry = frappe.db.sql("""select name
		from `tabJournal Entry`
		where docstatus=2
		and workflow_state != 'Cancelled'
	""",as_dict=True)
	count=0
	for x in journal_entry:
		count = count + 1
		# print(x.name)
		frappe.db.sql("update `tabJournal Entry` set workflow_state='Cancelled' where name='{}'".format(x.name))
	print(count)

def remove_project_from_pr_pi():
	gl_name = frappe.db.sql("""
		SELECT name FROM `tabGL Entry`
		WHERE voucher_type = 'Purchase Invoice'
		AND account = 'L202030301 - Stock received but Not billed - GYALSUNG'
		AND COALESCE(project, '') != ''
	""", as_dict=True)
	count = 0
	for raw in gl_name:
		count = count + 1
		frappe.db.sql("""
			UPDATE `tabGL Entry`
			SET project =''
			WHERE name = '{name}'
		""".format(name=raw.name))
		print(raw.name)
	print("Total GL Entries updated: ", count)

def remove_project_from_tax_account():
	gl_name = frappe.db.sql("""
		SELECT name FROM `tabGL Entry`
		WHERE account in ('L202030001 - TDS (2%) - GYALSUNG', 'L202030002 - TDS (3%) - GYALSUNG','L202030003 - TDS (5%) - GYALSUNG')
		AND COALESCE(project, '') != ''
	""", as_dict=True)
	count = 0
	for raw in gl_name:
		count = count + 1
		frappe.db.sql("""
			UPDATE `tabGL Entry`
			SET project =''
			WHERE name = '{name}'
		""".format(name=raw.name))
		print(raw.name)
	print("Total GL Entries updated: ", count)

def remove_project_from_advance_to_supplier_account():
	gl_name = frappe.db.sql("""
		SELECT name FROM `tabGL Entry`
		WHERE account in ('A202022004 - Advance to Supplier - GYALSUNG')
		AND COALESCE(project, '') != ''
	""", as_dict=True)
	count = 0
	for raw in gl_name:
		count = count + 1
		frappe.db.sql("""
			UPDATE `tabGL Entry`
			SET project =''
			WHERE name = '{name}'
		""".format(name=raw.name))
		print(raw.name)
	print("Total GL Entries updated: ", count)

def remove_gce_earned_leave():
	ledger_id= frappe.db.sql("""select l.name, l.leaves
		from `tabLeave Ledger Entry` l
		inner join `tabEmployee` e
		on l.employee = e.name
		where l.leave_type ='Earned Leave'
		and e.employment_type='GCE'
		and l.leaves >0
		""", as_dict=True)
	count = 0
	for raw in ledger_id:
		count = count + 1
		frappe.db.sql("""
			delete from `tabLeave Ledger Entry`
			WHERE name = '{name}'
		""".format(name=raw.name))
		print(raw.name)
	print("Total GL Entries deleted: ", count)

def change_mr_account():
	ledger_id= frappe.db.sql("""select name
		from `tabGL Entry`
		where account='Legacy Clearing Account - GYALSUNG'
		and voucher_type='Material Return'
		""", as_dict=True)
	count = 0
	for raw in ledger_id:
		count = count + 1
		frappe.db.sql("""
			update `tabGL Entry`
			set account='A202026001 - Internal Company Transaction - GYALSUNG'
			WHERE name = '{name}'
		""".format(name=raw.name))
		print(raw.name)
	print("Total GL Entries count: ", count)
def update_leave_allocation_date():
	ledger_id= frappe.db.sql("""select name
		from `tableave Allocation`
		where from_date='2025-08-01'
		and to_date='2025-08-31'
		""", as_dict=True)
	count = 0
	for raw in ledger_id:
		count = count + 1
		frappe.db.sql("""
			update `tabLeave Allocation`
			set to_date='2025-12-31'
			WHERE name = '{name}'
		""".format(name=raw.name))
		print(raw.name)
	print("Total Leave Allocation count: ", count)

def set_value_afetr_derpreciation():
	asset_id= frappe.db.sql("""select name
		from `tabAsset`
		where docstatus =1
		and status ='Partially Depreciated'
		and disable_depreciation = 0
		""", as_dict=True)
	count = 0
	for row in asset_id:
		print(row.name)
		count=count + 1
		asset_dep_schedule = frappe.db.get_value("Asset Depreciation Schedule", {"asset": row.name, "docstatus": 1}, "name")
		if asset_dep_schedule:
			value_after_depreciation_amount = frappe.db.sql(""" select sum(depreciation_amount) as total from `tabDepreciation Schedule` where parent = '{}' and docstatus = 1 and (journal_entry ='' or journal_entry is NULL) """.format(asset_dep_schedule))[0][0]
			value_after = flt(value_after_depreciation_amount) + 1
			if not value_after_depreciation_amount:
				print(row.name)
			# else:
				frappe.db.sql("""update `tabAsset Finance Book` set value_after_depreciation = {value} where parent = '{name}' """.format(value=value_after, name=row.name))
	print(count)

def update_asset_status():
	asset_id= frappe.db.sql("""select name
		from `tabAsset`
		where (status IS NULL OR status = '') 
		and docstatus=1 
		and income_tax_opening_depreciation_amount=opening_accumulated_depreciation 
		and is_fully_depreciated=0
		""", as_dict=True)
	count =0
	for row in asset_id:
		frappe.db.sql("""update `tabAsset` set is_fully_depreciated=1, status='Fully Depreciated' where name='{}'""".format(row.name))
		count +=1
	print(count)
def update_employment_type():
	data = frappe.db.sql("""select gl.name as name, gl.employee as employee, em.employment_type as employment_type
		from `tabLeave Ledger Entry` gl 
		inner join `tabEmployee` em
		on em.name=gl.employee
		where gl.docstatus  =1
	""", as_dict=1)
	count=0
	for raw in data:
		frappe.db.sql(""" update `tabLeave Ledger Entry` set employment_type='{0}' where name='{1}'
		""".format(raw.employment_type, raw.name))
		count +=1
	print (count)

def update_salary_tax():
	count =0
	salary_structure= frappe.db.sql("""select name from `tabSalary Structure` where is_active='Yes' """,as_dict=True)
	if salary_structure:
		
		for row in salary_structure:
			count +=1
			doc = frappe.get_doc("Salary Structure", row.name)
			# if getdate(row.from_date) < getdate(frappe.db.get_value("Employee",row.employee,"date_of_joining")):
			# 	frappe.throw("from date cannot be earlier to employee joining date")
			doc.save()
			print(count)

def update_leave_merg():
	leave_id = frappe.db.sql("""select name
			from `tabLeave Ledger Entry` 
			where docstatus=1 
			and leave_type='Earned Leave' 
			and transaction_type='Merge CL To EL'
	""",as_dict=True)
	count = 0
	for row in leave_id:
		count = count + 1
		frappe.db.sql("""
				update `tabLeave Ledger Entry` set from_date='2026-01-01', to_date='2026-12-31' where name='{name}'
				""".format(name=row.name))
	print(count)

def update_leaves_colsing_balance():
	leave_id = frappe.db.sql("""select name, employee
		from `tabLeave Ledger Entry` 
		where docstatus=1 
		and leave_type='Earned Leave' 
		and transaction_type='Merge CL To EL'
	""",as_dict=True)

def remove_all_task_detail_from_project():
	task = frappe.db.sql("""select name
		from `tabTask` 
		where docstatus!=2
		and project ='1.8.1 Administrative Building (GI-T) - GYALSUNG'
	""",as_dict=True)
	count = stock_entry_count =mr_count = 0
	for row in task:
		count = count + 1
		# stock_entry = frappe.db.sql("""select name, parent
		# 	from `tabStock Entry Detail` 
		# 	where docstatus=1 
		# 	and task ='{}'
		# """.format(row.name),as_dict=True)
		# for x in stock_entry:
		# 	stock_entry_count = stock_entry_count + 1
		# 	frappe.db.sql("""
		# 		update `tabStock Entry Detail` set task='' where name='{}'
		# 		""".format(x.name))
		# 	frappe.db.sql("""
		# 		update `tabGL Entry` set task='' where voucher_no='{}'
		# 		""".format(x.parent))
		mr_id = frappe.db.sql("""select name
			from `tabMaterial Request Item` 
			where docstatus!=2 
			and task ='{}'
		""".format(row.name),as_dict=True)
		for x in mr_id:
			mr_count = mr_count + 1
			print(x.name)
			frappe.db.sql("""
				update `tabMaterial Request Item` set task='' where name='{}'
				""".format(x.name))
	print(count)
	print(stock_entry_count)
	print(mr_count)



def execute():
    old_email = "sukmansubba16@gmail.com"
    new_email = "sukmansubba@gyalsunginfra.bt"

    # Check if old user exists
    if not frappe.db.exists("User", old_email):
        frappe.log_error(f"User {old_email} does not exist", "User Email Patch")
        return

    # Prevent conflict if new email already exists
    if frappe.db.exists("User", new_email):
        frappe.log_error(f"User {new_email} already exists", "User Email Patch")
        return

    # Rename user (correct way)
    frappe.rename_doc("User", old_email, new_email, merge=False)

    frappe.db.commit()


def update_pol_issue_jamtsholing():
	data = frappe.db.sql("""select name from `tabPOL Issue` where tanker='EQUIP251117' and docstatus=1 and pol_type='100167' and purpose='Issue'
		""", as_dict=1)
	count= pol_count=0
	
	for raw in data:
		# pol_entry_id = frappe.db.sql("""select name from `tabPOL Entry` where reference_name='{}' and pol_type='100167' and equipment='EQUIP251117'
		# """.format(raw.name), as_dict=1)
		# for x in pol_entry_id:
		# 	frappe.db.sql("""update `tabPOL Entry` set equipment='EQUIP251630', equipment_type='Skid Tank(Petrol)' where name='{}' """.format(x.name))
		# 	pol_count +=1

		frappe.db.sql("""update `tabPOL Issue` set tanker='EQUIP251630', registration_number='Skid Tank(Petrol)' where name='{}' """.format(raw.name))
		count +=1
	print (count)
	print(pol_count)