# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from email_reply_parser import EmailReplyParser
from frappe import _, qb
from frappe.desk.reportview import get_match_cond
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.query_builder import Interval
from frappe.query_builder.functions import Count, CurDate, Date, Sum, UnixTimestamp
from frappe.utils import add_days, flt, get_datetime, get_time, get_url, nowtime, today, getdate, date_diff
from frappe.utils.user import is_website_user

from erpnext import get_default_company
from erpnext.controllers.queries import get_filters_cond
from erpnext.controllers.website_list_for_contact import get_customers_suppliers
from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
from frappe.utils.user import get_users_with_role


class Project(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from erpnext.projects.doctype.project_user.project_user import ProjectUser

		actual_end_date: DF.Date | None
		actual_start_date: DF.Date | None
		actual_time: DF.Float
		collect_progress: DF.Check
		company: DF.Link
		copied_from: DF.Data | None
		cost_center: DF.Link | None
		customer: DF.Link | None
		daily_time_to_send: DF.Time | None
		day_to_send: DF.Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
		department: DF.Link | None
		estimated_costing: DF.Currency
		expected_end_date: DF.Date | None
		expected_start_date: DF.Date | None
		first_email: DF.Time | None
		frequency: DF.Literal["Hourly", "Twice Daily", "Daily", "Weekly"]
		from_time: DF.Time | None
		gross_margin: DF.Currency
		holiday_list: DF.Link | None
		is_active: DF.Literal["Yes", "No"]
		message: DF.Text | None
		naming_series: DF.Literal["PROJ-.####"]
		notes: DF.TextEditor | None
		per_gross_margin: DF.Percent
		percent_complete: DF.Percent
		percent_complete_method: DF.Literal["Manual", "Task Completion", "Task Progress", "Task Weight"]
		priority: DF.Literal["Medium", "Low", "High"]
		project_name: DF.Data
		project_template: DF.Link | None
		project_type: DF.Link | None
		sales_order: DF.Link | None
		second_email: DF.Time | None
		status: DF.Literal["Open", "Completed", "Cancelled"]
		to_time: DF.Time | None
		total_billable_amount: DF.Currency
		total_billed_amount: DF.Currency
		total_consumed_material_cost: DF.Currency
		total_costing_amount: DF.Currency
		total_purchase_cost: DF.Currency
		total_sales_amount: DF.Currency
		users: DF.Table[ProjectUser]
		weekly_time_to_send: DF.Time | None
	# end: auto-generated types

	def onload(self):
		if not self.get('__unsaved'):
			if not self.get("activity_tasks"):
				self.load_activity_tasks()

			if not self.get("additional_tasks"):
				self.load_additional_tasks()
					
		self.set_onload(
			"activity_summary",
			frappe.db.sql(
				"""select activity_type,
			sum(hours) as total_hours
			from `tabTimesheet Detail` where project=%s and docstatus < 2 group by activity_type
			order by total_hours desc""",
				self.name,
				as_dict=True,
			),
		)

		# self.update_costing()

	def before_print(self, settings=None):
		self.onload()

	def validate(self):
		self.validate_dates()
		self.validate_branch_cc()
		self.validate_project_type_and_party()
		self.update_party_info()
		# set_status method created by SHIV on 03/11/2017
		self.set_status()
		self.validate_target_quantity()
		self.validate_work_quantity()
		
		if self.status in ('Planning','Ongoing'):
			self.sync_activity_tasks()
			self.sync_additional_tasks()
		self.activity_tasks = []
		self.additional_tasks = []

		self.validate_branch_change()
		self.send_welcome_email()
		self.check_timesheet_status()

		# if not self.is_new():
		# 	self.copy_from_template()
		# self.send_welcome_email()
		# self.update_costing()
		# self.update_percent_complete()
		# self.validate_from_to_dates("expected_start_date", "expected_end_date")
		# self.validate_from_to_dates("actual_start_date", "actual_end_date")
	def on_update(self):
		self.load_activity_tasks()
		self.load_additional_tasks()
		if self.status in ('Planning','Ongoing'):
			self.sync_activity_tasks()
			self.sync_additional_tasks()
		self.update_task_progress()
		self.update_project_progress()
		self.update_group_tasks()
		self.update_branch_change()

	def update_branch_change(self):
		if self.flags.dont_sync_tasks: return
		
		for doctype in ["MB Entry", "BOQ Adjustment", "BOQ", "Timesheet", "Task"]:
			for t in frappe.get_all(doctype, ["name"], {"project": self.name}):
				doc = frappe.get_doc(doctype, t.name)
				if self.branch != doc.branch:
					doc.branch      = self.branch
					doc.cost_center = self.cost_center
					doc.save(ignore_permissions = True)

	def update_group_tasks(self):
		if self.flags.dont_sync_tasks: return
		
		# Activity Tasks
		group_list = frappe.db.sql("""
							select t1.name, t1.task_idx, t1.subject, t1.is_group,
									(select ifnull(min(t2.task_idx),9999)
										from  `tabTask` as t2
										where t2.project  = t1.project
										and   t2.is_group = t1.is_group
										and   t2.task_idx > t1.task_idx
									) as max_idx
							from `tabTask` as t1
							where t1.project = "{0}"
							and   t1.is_group = 1
							and   t1.additional_task = 0
							order by t1.task_idx
						""".format(self.name), as_dict=1)
		
		for item in group_list:
			values = frappe.db.sql("""
							select min(exp_start_date) as min_start_date,
									max(exp_end_date) as max_end_date,
									sum(ifnull(work_quantity,0)) as tot_work_quantity,
									sum(ifnull(work_quantity_complete,0)) as tot_work_quantity_complete
								from   `tabTask`
								where  project = "{0}"
								and    task_idx > {1}
								and    task_idx < {2}
								and    additional_task = 0
					""".format(self.name, item.task_idx, item.max_idx), as_dict=1)[0]

			frappe.db.sql("""
							update `tabTask`
							set
								grp_exp_start_date = '{0}',
								grp_exp_end_date = '{1}',
								grp_work_quantity = {4},
								grp_work_quantity_complete = {5}
							where project = "{2}"
							and name = '{3}'
					""".format(values.min_start_date, values.max_end_date, self.name, item.name, flt(values.tot_work_quantity), flt(values.tot_work_quantity_complete)))

		# Additional Tasks
		group_list = frappe.db.sql("""
								select t1.name, t1.task_idx, t1.subject, t1.is_group,
										(select ifnull(min(t2.task_idx),9999)
											from  `tabTask` as t2
											where t2.project  = t1.project
											and   t2.is_group = t1.is_group
											and   t2.task_idx > t1.task_idx
										) as max_idx
								from `tabTask` as t1
								where t1.project = "{0}"
								and   t1.is_group = 1
								and   t1.additional_task = 1
								order by t1.task_idx
						""".format(self.name), as_dict=1)
		
		for item in group_list:
			values = frappe.db.sql("""
							select min(exp_start_date) as min_start_date,
									max(exp_end_date) as max_end_date,
									sum(ifnull(work_quantity,0)) as tot_work_quantity,
									sum(ifnull(work_quantity_complete,0)) as tot_work_quantity_complete
								from   `tabTask`
								where  project = "{0}"
								and    task_idx > {1}
								and    task_idx < {2}
								and    additional_task = 1
					""".format(self.name, item.task_idx, item.max_idx), as_dict=1)[0]

			frappe.db.sql("""
							update `tabTask`
							set
								grp_exp_start_date = '{0}',
								grp_exp_end_date = '{1}',
								grp_work_quantity = {4},
								grp_work_quantity_complete = {5}
							where project = "{2}"
							and name = '{3}'
					""".format(values.min_start_date, values.max_end_date, self.name, item.name, flt(values.tot_work_quantity), flt(values.tot_work_quantity_complete)))                        

	def update_project_progress(self):
		if self.flags.dont_sync_tasks: return
		
		# Following code added by SHIV on 2017/08/16
		total = frappe.db.sql("""
				select
						sum(
								case
								when additional_task = 0 and status in ('Closed', 'Cancelled') then 1
								else 0
								end
						) as completed_count,
						sum(
								case
								when additional_task = 0 then 1
								else 0
								end
						) as count,
						sum(
								case
								when additional_task = 1 and status in ('Closed', 'Cancelled') then 1
								else 0
								end
						) as add_completed_count,
						sum(
								case
								when additional_task = 1 then 1
								else 0
								end
						) as add_count,
						sum(
								case
								when additional_task = 0 then ifnull(work_quantity,0)
								else 0
								end
						) as tot_work_quantity,
						sum(
								case
								when additional_task = 1 then ifnull(work_quantity,0)
								else 0
								end
						) as tot_add_work_quantity,
						sum(
								case
								when additional_task = 0 then ifnull(work_quantity_complete,0)
								else 0
								end
						) as tot_work_quantity_complete,
						sum(
								case
								when additional_task = 1 then ifnull(work_quantity_complete,0)
								else 0
								end
						) as tot_add_work_quantity_complete
				from tabTask
				where project=%s
				and is_group=0
		""", self.name, as_dict=1)[0]

		# Following code commented by SHIV on 09/11/2017
		self.percent_complete           = 0.0
		self.add_percent_complete       = 0.0
		self.tot_wq_percent             = 0.0
		self.tot_wq_percent_complete    = 0.0
		self.tot_add_wq_percent         = 0.0
		self.tot_add_wq_percent_complete= 0.0

		if total.count:
				self.percent_complete   = flt(flt(total.completed_count) / total.count * 100, 2)
				self.tot_wq_percent     = flt(total.tot_work_quantity,2)
				self.tot_wq_percent_complete = flt(total.tot_work_quantity_complete,2)

		if total.add_count:
				self.add_percent_complete = flt(flt(total.add_completed_count) / total.add_count * 100, 2)
				self.tot_add_wq_percent = flt(total.tot_add_work_quantity,2)
				self.tot_add_wq_percent_complete = flt(total.tot_add_work_quantity_complete,2)
		# +++++++++++++++++++++ Ver 2.0 ENDS +++++++++++++++++++++                

	def update_task_progress(self):
		if self.flags.dont_sync_tasks: return
		
		task_list = frappe.db.sql("""
				select name
				from `tabTask`
				where project = "{0}"
				""".format(self.name), as_dict=1)

		if task_list:
			for task in task_list:
				values = frappe.db.sql("""
							select sum(ifnull(target_quantity_complete,0)) as target_quantity_complete,
									sum(ifnull(work_quantity_complete,0)) as work_quantity_complete
							from `tabTimesheet`
							where task = '{0}'
							and docstatus < 2
							""".format(task.name), as_dict=1)[0]
		
				frappe.db.sql("""
					update `tabTask`
					set target_quantity_complete = {0},
							work_quantity_complete = {1},
							status = case
											when {0} >= target_quantity then 'Completed'
											else status
										end
					where name = '{2}'
				""".format(flt(values.target_quantity_complete), flt(values.work_quantity_complete), task.name))

	def load_activity_tasks(self):
		#frappe.msgprint(_("load_activity_task is called from onload"))
		"""Load `activity_tasks` from the database"""
		self.activity_tasks = []
		for task in self.get_activity_tasks():
			self.append("activity_tasks", {
				"activity": task.activity,
				"task": task.subject,
				"is_group": task.is_group,
				"status": task.status,
				"start_date": task.exp_start_date,
				"end_date": task.exp_end_date,
				"description": task.description,
				"work_quantity": task.work_quantity,
				"work_quantity_complete": task.work_quantity_complete,
				"target_uom": task.target_uom,
				"target_quantity": task.target_quantity,
				"target_quantity_complete": task.target_quantity_complete,
				"task_id": task.name,
				"grp_exp_start_date": task.grp_exp_start_date,
				"grp_exp_end_date": task.grp_exp_end_date,
				"grp_work_quantity": task.grp_work_quantity,
				"grp_work_quantity_complete": task.grp_work_quantity_complete
			})

	def load_additional_tasks(self):
		#frappe.msgprint(_("load_activity_task is called from onload"))
		"""Load `additional_tasks` from the database"""
		self.additional_tasks = []
		for task in self.get_additional_tasks():
			self.append("additional_tasks", {
				"activity": task.activity,
				"task": task.subject,
				"is_group": task.is_group,
				"status": task.status,
				"start_date": task.exp_start_date,
				"end_date": task.exp_end_date,
				"description": task.description,
				"work_quantity": task.work_quantity,
				"work_quantity_complete": task.work_quantity_complete,
				"target_uom": task.target_uom,
				"target_quantity": task.target_quantity,
				"target_quantity_complete": task.target_quantity_complete,
				"task_id": task.name,
				"grp_exp_start_date": task.grp_exp_start_date,
				"grp_exp_end_date": task.grp_exp_end_date,
				"grp_work_quantity": task.grp_work_quantity,
				"grp_work_quantity_complete": task.grp_work_quantity_complete
			})

	def get_activity_tasks(self):
		return frappe.get_all("Task", "*", {"project": self.name, "additional_task": 0}, order_by="task_idx, exp_start_date")

	def get_additional_tasks(self):
		return frappe.get_all("Task", "*", {"project": self.name, "additional_task": 1}, order_by="task_idx, exp_start_date")	

	def get_project_advance(self):
		return frappe.get_all("Project Advance", "*", {"project": self.name, "docstatus": 1}, order_by="advance_date")

	def get_project_boq(self):
		return frappe.get_all("BOQ", "*", {"project": self.name, "docstatus": 1}, order_by="boq_date")

	def get_project_invoice(self):
		return frappe.get_all("Project Invoice", "*", {"project": self.name, "docstatus": 1}, order_by="invoice_date")        
	
	# +++++++++++++++++++++ Ver 2.0 ENDS +++++++++++++++++++++
			
	def get_tasks(self):
		return frappe.get_all("Task", "*", {"project": self.name}, order_by="exp_start_date asc")

	def check_timesheet_status(self):
		if self.status == 'Completed':
			if frappe.db.exists({
				'doctype': 'Timesheet',
				'docstatus': 0,
				'project':self.name
			}):
				frappe.throw('Submit all <b>Timesheet</b> related to this project to close the project')

	def validate_branch_change(self):
		if self.flags.dont_sync_tasks: return
		
		if self.branch != self.get_db_value("branch"):
			for doctype in ["Project Advance", "Project Invoice"]:
				for t in frappe.get_all(doctype, ["name"], {"project": self.name, "docstatus":("<",2)}):
					msg = '<b>Reference# <a href="#Form/{0}/{1}">{0}: {1}</a></b>'.format(doctype, t.name)
					frappe.throw(_("Change of branch not permitted.<br>{0}").format(msg),title="Dependencies found")

	def sync_additional_tasks(self):
		"""sync tasks and remove table"""
		if self.flags.dont_sync_tasks: return
		
		task_names = []
		task_idx = 0
		for t in self.additional_tasks:
			task_idx += 1

			if not t.target_uom:
				t.target_uom = 'Percent'
				if not t.target_quantity:
					t.target_quantity = 100
                        
			if t.task_id:
				task = frappe.get_doc("Task", t.task_id)
			else:
				task = frappe.new_doc("Task")
				task.project = self.name

			task.update({
				"activity": t.activity,
				"subject": t.task,
				"is_group": t.is_group,
				"work_quantity": t.work_quantity,
				"work_quantity_complete": t.work_quantity_complete,
				"target_uom": t.target_uom,
				"target_quantity": t.target_quantity,
				"status": t.status,
				"exp_start_date": t.start_date,
				"exp_end_date": t.end_date,
				"description": t.description,
				"target_quantity_complete": t.target_quantity_complete,
				"task_idx": task_idx,
				"grp_exp_start_date": t.grp_exp_start_date,
				"grp_exp_end_date": t.grp_exp_end_date,
				"grp_work_quantity": t.grp_work_quantity,
				"grp_work_quantity_complete": t.grp_work_quantity_complete,
				"additional_task": 1
			})

			task.flags.ignore_links = True
			task.flags.from_project = True
			task.flags.ignore_feed = True
			task.save(ignore_permissions = True)
			task_names.append(task.name)

		# delete
		for t in frappe.get_all("Task", ["name"], {"project": self.name, "name": ("not in", task_names), "additional_task": 1}):
			frappe.delete_doc("Task", t.name)

		# self.update_percent_complete()
		self.update_costing()

	def sync_activity_tasks(self):
		"""sync tasks and remove table"""
		if self.flags.dont_sync_tasks: return

		task_names = []
		task_idx = 0
		for t in self.activity_tasks:
			task_idx += 1

			if not t.target_uom:
				t.target_uom = 'Percent'
				if not t.target_quantity:
					t.target_quantity = 100
			
			if t.task_id:
				task = frappe.get_doc("Task", t.task_id)
			else:
				task = frappe.new_doc("Task")
				task.project = self.name

			task.update({
				"activity": t.activity,
				"subject": t.task,
				"is_group": t.is_group,
				"work_quantity": t.work_quantity,
				"work_quantity_complete": t.work_quantity_complete,
				"target_uom": t.target_uom,
				"target_quantity": t.target_quantity,
				"status": t.status,
				"exp_start_date": t.start_date,
				"exp_end_date": t.end_date,
				"description": t.description,
				"target_quantity_complete": t.target_quantity_complete,
				"task_idx": task_idx,
				"grp_exp_start_date": t.grp_exp_start_date,
				"grp_exp_end_date": t.grp_exp_end_date,
				"grp_work_quantity": t.grp_work_quantity,
				"grp_work_quantity_complete": t.grp_work_quantity_complete,
				"additional_task": 0
			})

			task.flags.ignore_links = True
			task.flags.from_project = True
			task.flags.ignore_feed = True
			task.save(ignore_permissions = True)
			task_names.append(task.name)

		# delete
		for t in frappe.get_all("Task", ["name"], {"project": self.name, "name": ("not in", task_names), "additional_task": 0}):
			frappe.delete_doc("Task", t.name)

		# self.update_percent_complete()
		self.update_costing()

	def validate_work_quantity(self):
		if self.flags.dont_sync_tasks: return
		
		for task in self.activity_tasks:
			prev_value = frappe.db.get_value("Task", task.task_id, "work_quantity")
			
			if flt(task.work_quantity) < flt(task.work_quantity_complete):
				frappe.throw(_("<b>WORK PLAN</b><br/> Row# {0} : `Target Work Quantity` cannot be less than `Already Achieved Wrok Quantity`.").format(task.idx))

			if flt(task.work_quantity) != flt(prev_value) and flt(prev_value) > 0:
				msg = ""
				ts_list = frappe.db.sql("""
							select name
							from `tabTimesheet`
							where parent_project = "{0}"
							and task = '{1}'
							and docstatus < 2
					""".format(self.name, task.task_id), as_dict=1)

				if len(ts_list):
					for item in ts_list:
						msg += 'Reference: <a href="#Form/Timesheet/{0}">{0}</a><br/>'.format(item.name,item.name)
					
					frappe.throw("Row# {0} : Cannot change `Target Work Quantity` for Tasks already having active Timesheets. <br/>{1}".format(task.idx, msg))

		for task in self.additional_tasks:
			prev_value = frappe.db.get_value("Task", task.task_id, "work_quantity")
			
			if flt(task.work_quantity) < flt(task.work_quantity_complete):
				frappe.throw(_("<b>WORK PLAN</b><br/> Row# {0} : `Target Work Quantity` cannot be less than `Already Achieved Wrok Quantity`.").format(task.idx))

			if flt(task.work_quantity) != flt(prev_value) and flt(prev_value) > 0:
				msg = ""
				ts_list = frappe.db.sql("""
							select name
							from `tabTimesheet`
							where project = "{0}"
							and task = '{1}'
							and docstatus < 2
					""".format(self.name, task.task_id), as_dict=1)

				if len(ts_list):
					for item in ts_list:
						msg += 'Reference: <a href="#Form/Timesheet/{0}">{0}</a><br/>'.format(item.name,item.name)
					
					frappe.throw("Row# {0} : Cannot change `Target Work Quantity` for Tasks already having active Timesheets. <br/>{1}".format(task.idx, msg))
                                        
	def validate_target_quantity(self):
		if self.flags.dont_sync_tasks: return
		
		for task in self.activity_tasks:
			prev_value = frappe.db.get_value("Task", task.task_id, "target_quantity")
			
			if flt(task.target_quantity) < flt(task.target_quantity_complete):
				frappe.throw(_("<b>WORK PLAN</b><br/> Row# {0} : `Target Value` cannot be less than `Achieved Value`.").format(task.idx))

			if flt(task.target_quantity) != flt(prev_value) and flt(prev_value) > 0:
				msg = ""
				ts_list = frappe.db.sql("""
							select name
							from `tabTimesheet`
							where project = "{0}"
							and task = '{1}'
							and docstatus < 2
					""".format(self.name, task.task_id), as_dict=1)

				if len(ts_list):
					for item in ts_list:
						msg += 'Reference: <a href="#Form/Timesheet/{0}">{0}</a><br/>'.format(item.name,item.name)
					
					frappe.throw("Row# {0} : Cannot change `Target Quantity/Value` for Tasks already having active Timesheets. <br/>{1}".format(task.idx, msg))
								
		for task in self.additional_tasks:
			prev_value = frappe.db.get_value("Task", task.task_id, "target_quantity")
			
			if flt(task.target_quantity) < flt(task.target_quantity_complete):
				frappe.throw(_("<b>WORK PLAN</b><br/> Row# {0} : `Target Value` cannot be less than `Achieved Value`.").format(task.idx))

			if flt(task.target_quantity) != flt(prev_value) and flt(prev_value) > 0:
				msg = ""
				ts_list = frappe.db.sql("""
							select name
							from `tabTimesheet`
							where project = "{0}"
							and task = '{1}'
							and docstatus < 2
					""".format(self.name, task.task_id), as_dict=1)

				if len(ts_list):
					for item in ts_list:
						msg += 'Reference: <a href="#Form/Timesheet/{0}">{0}</a><br/>'.format(item.name,item.name)
					
					frappe.throw("Row# {0} : Cannot change `Target Quantity/Value` for Tasks already having active Timesheets. <br/>{1}".format(task.idx, msg))
								
	def set_status(self):
		self.docstatus = {
			"Planning": 0,
			"Ongoing": 0,
			"Completed": 1,
			"Cancelled": 2
		}[str(self.status) or "Planning"]

	def validate_project_type_and_party(self):
		""" Restrict user from changing party if there are advance/invoice transactions """

		if not self.project_type:
			frappe.throw(_("Project type cannot be empty"), title="Data Missing")
		elif self.party_type and not self.party:
			frappe.throw(_("Party cannot be empty"),title="Data Missing")
		elif not self.party_type and self.party:
			frappe.throw(_("Party Type cannot be empty"),title="Data Missing")
		else:
			#project_type = {"Internal": ["Employee","None"], "External": ["Supplier","Customer"]}
			project_type = {"Internal": ["Customer"], "External": ["Supplier"]}
			for key,value in project_type.items():
				if self.project_type == key and (self.party_type or "None") not in value:
					frappe.throw(_("Party type should be {0} for {1} projects").format("/".join(value),key), title="Invalid Data")

			prev_project_type = self.get_db_value("project_type") 
			prev_party        = self.get_db_value("party")

			fields = []
			if prev_project_type and prev_project_type != self.project_type:
				fields.append("Project Type")
			elif prev_party and prev_party != self.party:
				fields.append("Party")
			
			if fields:
				self.check_dependencies(fields[0])

	def check_dependencies(self, field):
		for dt in ["Project Advance", "Project Invoice"]:
			for t in frappe.get_all(dt, ["name"], {"project": self.name,"docstatus":("<",2)}):
				msg = '<b>Reference# : <a href="#Form/{1}/{0}">{0}</a></b>'.format(t.name,dt)
				frappe.throw(_("{2} cannot be changed for projects already having {1}<br>{0}").format(msg,dt,field), title="Invalid Operation")
                                 

	def validate_branch_cc(self):
		if self.flags.dont_sync_tasks: return

		if self.cost_center != frappe.db.get_value("Branch", self.branch, "cost_center"):
			frappe.throw("Project\'s branch and cost center doesn't belong to each other")

	def validate_dates(self):
		if self.flags.dont_sync_tasks: return
				
		if self.expected_start_date and self.expected_end_date:
			if getdate(self.expected_end_date) < getdate(self.expected_start_date):
				frappe.throw(_("Expected End Date can not be less than Expected Start Date"))
		
		if self.dlp_start_date and self.dlp_end_date:
			if getdate(self.dlp_end_date) < getdate(self.dlp_start_date):
				frappe.throw(_("DLP End Date can not be less than DLP Start Date"))
			self.total_no_days = date_diff(self.dlp_end_date, self.dlp_start_date)
				
		# ++++++++++++++++++++ Ver 2.0 BEGINS ++++++++++++++++++++
		# Following code added by SHIV on 20/09/2017
		for task in self.activity_tasks:
			if not self.revised_completion_date:
				prev_start_date = getdate(frappe.db.get_value("Task", task.task_id, "exp_start_date"))
				prev_end_date = getdate(frappe.db.get_value("Task", task.task_id, "exp_end_date"))

				if (prev_start_date and getdate(task.start_date)) and (getdate(task.start_date) != prev_start_date):
					msg = ""
					ts_list = frappe.db.sql("""
								select name
								from `tabTimesheet`
								where parent_project = "{0}"
								and task = '{1}'
								and docstatus < 2
						""".format(self.name, task.task_id), as_dict=1)

					if len(ts_list):
						for item in ts_list:
							msg += 'Reference: <a href="#Form/Timesheet/{0}">{0}</a><br/>'.format(item.name,item.name)
						
						frappe.throw("Row# {0} : Cannot change `Start Date` for Tasks already having active Timesheets. <br/>{1}".format(task.idx, msg))

				if (prev_end_date and getdate(task.end_date)) and (getdate(task.end_date) != prev_end_date):
					msg = ""
					ts_list = frappe.db.sql("""
								select name
								from `tabTimesheet`
								where parent_project = "{0}"
								and task = '{1}'
								and docstatus < 2
						""".format(self.name, task.task_id), as_dict=1)

					if len(ts_list):
						for item in ts_list:
							msg += 'Reference: <a href="#Form/Timesheet/{0}">{0}</a><br/>'.format(item.name,item.name)
						
						frappe.throw("Row# {0} : Cannot change `End Date` for Tasks already having active Timesheets. <br/>{1}".format(task.idx, msg))

		for task in self.additional_tasks:
			if not self.revised_completion_date:
				prev_start_date = getdate(frappe.db.get_value("Task", task.task_id, "exp_start_date"))
				prev_end_date = getdate(frappe.db.get_value("Task", task.task_id, "exp_end_date"))

				if (prev_start_date and getdate(task.start_date)) and (getdate(task.start_date) != prev_start_date):
					msg = ""
					ts_list = frappe.db.sql("""
								select name
								from `tabTimesheet`
								where parent_project = "{0}"
								and task = '{1}'
								and docstatus < 2
						""".format(self.name, task.task_id), as_dict=1)

					if len(ts_list):
						for item in ts_list:
							msg += 'Reference: <a href="#Form/Timesheet/{0}">{0}</a><br/>'.format(item.name,item.name)
						
						frappe.throw("Row# {0} : Cannot change `Start Date` for Tasks already having active Timesheets. <br/>{1}".format(task.idx, msg))

				if (prev_end_date and getdate(task.end_date)) and (getdate(task.end_date) != prev_end_date):
					msg = ""
					ts_list = frappe.db.sql("""
								select name
								from `tabTimesheet`
								where parent_project = "{0}"
								and task = '{1}'
								and docstatus < 2
						""".format(self.name, task.task_id), as_dict=1)

					if len(ts_list):
						for item in ts_list:
							msg += 'Reference: <a href="#Form/Timesheet/{0}">{0}</a><br/>'.format(item.name,item.name)
						
						frappe.throw("Row# {0} : Cannot change `End Date` for Tasks already having active Timesheets. <br/>{1}".format(task.idx, msg))                                        
									
		# +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++
	def update_project(self):
		#self.update_percent_complete()
		self.update_project_progress()
		self.update_costing()
		self.flags.dont_sync_tasks = True
		self.save(ignore_permissions = True)

	""" Default Project Codes begins here of ERPNext Jai"""
	def copy_from_template(self):
		"""
		Copy tasks from template
		"""
		if self.project_template and not frappe.db.get_all("Task", dict(project=self.name), limit=1):
			# has a template, and no loaded tasks, so lets create
			if not self.expected_start_date:
				# project starts today
				self.expected_start_date = today()

			template = frappe.get_doc("Project Template", self.project_template)

			if not self.project_type:
				self.project_type = template.project_type

			# create tasks from template
			project_tasks = []
			tmp_task_details = []
			for task in template.tasks:
				template_task_details = frappe.get_doc("Task", task.task)
				tmp_task_details.append(template_task_details)
				task = self.create_task_from_template(template_task_details)
				project_tasks.append(task)

			self.dependency_mapping(tmp_task_details, project_tasks)

	def create_task_from_template(self, task_details):
		return frappe.get_doc(
			dict(
				doctype="Task",
				subject=task_details.subject,
				project=self.name,
				status="Open",
				exp_start_date=self.calculate_start_date(task_details),
				exp_end_date=self.calculate_end_date(task_details),
				description=task_details.description,
				task_weight=task_details.task_weight,
				type=task_details.type,
				issue=task_details.issue,
				is_group=task_details.is_group,
				color=task_details.color,
				template_task=task_details.name,
				priority=task_details.priority,
			)
		).insert()

	def calculate_start_date(self, task_details):
		self.start_date = add_days(self.expected_start_date, task_details.start)
		self.start_date = self.update_if_holiday(self.start_date)
		return self.start_date

	def calculate_end_date(self, task_details):
		self.end_date = add_days(self.start_date, task_details.duration)
		return self.update_if_holiday(self.end_date)

	def update_if_holiday(self, date):
		holiday_list = self.holiday_list or get_holiday_list(self.company)
		while is_holiday(holiday_list, date):
			date = add_days(date, 1)
		return date

	def dependency_mapping(self, template_tasks, project_tasks):
		for project_task in project_tasks:
			template_task = frappe.get_doc("Task", project_task.template_task)

			self.check_depends_on_value(template_task, project_task, project_tasks)
			self.check_for_parent_tasks(template_task, project_task, project_tasks)

	def check_depends_on_value(self, template_task, project_task, project_tasks):
		if template_task.get("depends_on") and not project_task.get("depends_on"):
			project_template_map = {pt.template_task: pt for pt in project_tasks}

			for child_task in template_task.get("depends_on"):
				if project_template_map and project_template_map.get(child_task.task):
					project_task.reload()  # reload, as it might have been updated in the previous iteration
					project_task.append(
						"depends_on", {"task": project_template_map.get(child_task.task).name}
					)
					project_task.save()

	def check_for_parent_tasks(self, template_task, project_task, project_tasks):
		if template_task.get("parent_task") and not project_task.get("parent_task"):
			for pt in project_tasks:
				if pt.template_task == template_task.parent_task:
					project_task.parent_task = pt.name
					project_task.save()
					break

	def is_row_updated(self, row, existing_task_data, fields):
		if self.get("__islocal") or not existing_task_data:
			return True

		d = existing_task_data.get(row.task_id, {})

		for field in fields:
			if row.get(field) != d.get(field):
				return True

	def update_project(self):
		"""Called externally by Task"""
		self.update_percent_complete()
		self.update_costing()
		self.db_update()

	def after_insert(self):
		self.copy_from_template()
		if self.sales_order:
			frappe.db.set_value("Sales Order", self.sales_order, "project", self.name)

	def on_trash(self):
		frappe.db.set_value("Sales Order", {"project": self.name}, "project", "")

	def update_percent_complete(self):
		if self.percent_complete_method == "Manual":
			if self.status == "Completed":
				self.percent_complete = 100
			return

		total = frappe.db.count("Task", dict(project=self.name))

		if not total:
			self.percent_complete = 0
		else:
			if (self.percent_complete_method == "Task Completion" and total > 0) or (
				not self.percent_complete_method and total > 0
			):
				completed = frappe.db.sql(
					"""select count(name) from tabTask where
					project=%s and status in ('Cancelled', 'Completed')""",
					self.name,
				)[0][0]
				self.percent_complete = flt(flt(completed) / total * 100, 2)

			if self.percent_complete_method == "Task Progress" and total > 0:
				progress = frappe.db.sql(
					"""select sum(progress) from tabTask where
					project=%s""",
					self.name,
				)[0][0]
				self.percent_complete = flt(flt(progress) / total, 2)

			if self.percent_complete_method == "Task Weight" and total > 0:
				weight_sum = frappe.db.sql(
					"""select sum(task_weight) from tabTask where
					project=%s""",
					self.name,
				)[0][0]
				weighted_progress = frappe.db.sql(
					"""select progress, task_weight from tabTask where
					project=%s""",
					self.name,
					as_dict=1,
				)
				pct_complete = 0
				for row in weighted_progress:
					pct_complete += row["progress"] * frappe.utils.safe_div(row["task_weight"], weight_sum)
				self.percent_complete = flt(flt(pct_complete), 2)

		# don't update status if it is cancelled
		if self.status == "Cancelled":
			return

		if self.percent_complete == 100:
			self.status = "Completed"

	def update_costing(self):
		from_time_sheet = frappe.db.sql("""select
			sum(costing_amount) as costing_amount,
			sum(billing_amount) as billing_amount,
			min(from_time) as start_date,
			max(to_time) as end_date,
			sum(hours) as time
			from `tabTimesheet Detail` where project = %s and docstatus = 1""", self.name, as_dict=1)[0]

		from_expense_claim = frappe.db.sql("""select
			sum(total_sanctioned_amount) as total_sanctioned_amount
			from `tabExpense Claim` where project = %s and approval_status='Approved'
			and docstatus = 1""",
			self.name, as_dict=1)[0]

		self.actual_start_date = from_time_sheet.start_date
		self.actual_end_date = from_time_sheet.end_date

		self.total_costing_amount = flt(from_time_sheet.costing_amount)
		self.total_billing_amount = flt(from_time_sheet.billing_amount)
		self.actual_time = flt(from_time_sheet.time)

		self.total_expense_claim = flt(from_expense_claim.total_sanctioned_amount)

		self.gross_margin = flt(self.total_billing_amount) - flt(self.total_costing_amount)

		if self.total_billing_amount:
			self.per_gross_margin = (self.gross_margin / flt(self.total_billing_amount)) *100

		# from frappe.query_builder.functions import Max, Min, Sum

		# TimesheetDetail = frappe.qb.DocType("Timesheet Detail")
		# from_time_sheet = (
		# 	frappe.qb.from_(TimesheetDetail)
		# 	.select(
		# 		Sum(TimesheetDetail.costing_amount).as_("costing_amount"),
		# 		Sum(TimesheetDetail.billing_amount).as_("billing_amount"),
		# 		Min(TimesheetDetail.from_time).as_("start_date"),
		# 		Max(TimesheetDetail.to_time).as_("end_date"),
		# 		Sum(TimesheetDetail.hours).as_("time"),
		# 	)
		# 	.where((TimesheetDetail.project == self.name) & (TimesheetDetail.docstatus == 1))
		# ).run(as_dict=True)[0]

		# self.actual_start_date = from_time_sheet.start_date
		# self.actual_end_date = from_time_sheet.end_date

		# self.total_costing_amount = from_time_sheet.costing_amount
		# self.total_billable_amount = from_time_sheet.billing_amount
		# self.actual_time = from_time_sheet.time

		# self.update_purchase_costing()
		# self.update_sales_amount()
		# self.update_billed_amount()
		# self.calculate_gross_margin()

	def calculate_gross_margin(self):
		expense_amount = (
			flt(self.total_costing_amount)
			+ flt(self.total_purchase_cost)
			+ flt(self.get("total_consumed_material_cost", 0))
		)

		self.gross_margin = flt(self.total_billed_amount) - expense_amount
		if self.total_billed_amount:
			self.per_gross_margin = (self.gross_margin / flt(self.total_billed_amount)) * 100

	def update_purchase_costing(self):
		total_purchase_cost = calculate_total_purchase_cost(self.name)
		##frappe.throw(str( total_purchase_cost[0][0]))
		self.total_purchase_cost = total_purchase_cost and total_purchase_cost[0][0] or 0

	def update_sales_amount(self):
		total_sales_amount = frappe.db.sql(
			"""select sum(base_net_total)
			from `tabSales Order` where project = %s and docstatus=1""",
			self.name,
		)
		#frappe.throw(str(total_sales_amount))

		self.total_sales_amount = total_sales_amount and total_sales_amount[0][0] or 0

	def update_billed_amount(self):
		total_billed_amount = frappe.db.sql(
			"""select sum(base_net_total)
			from `tabSales Invoice` where project = %s and docstatus=1""",
			self.name,
		)

		self.total_billed_amount = total_billed_amount and total_billed_amount[0][0] or 0

	def after_rename(self, old_name, new_name, merge=False):
		if old_name == self.copied_from:
			frappe.db.set_value("Project", new_name, "copied_from", new_name)

	def send_welcome_email(self):
		url = get_url(f"/project/?name={self.name}")
		messages = (
			_("You have been invited to collaborate on the project: {0}").format(self.name),
			url,
			_("Join"),
		)

		content = """
		<p>{0}.</p>
		<p><a href="{1}">{2}</a></p>
		"""

		for user in self.users:
			if user.welcome_email_sent == 0:
				frappe.sendmail(
					user.user,
					subject=_("Project Collaboration Invitation"),
					content=content.format(*messages),
				)
				user.welcome_email_sent = 1
	
	@frappe.whitelist()
	def update_party_info(self):
		if self.project_type:
			if self.party_type and self.party:
				doc = frappe.get_doc(self.party_type, self.party)
				self.party_address = doc.get("customer_details") if self.party_type == "Customer" else doc.get("supplier_details") if self.party_type == "Supplier" else doc.get("employee_name")
				self.party_image = doc.image
			else:
				self.party_address = None
				self.party_image = None

def get_timeline_data(doctype: str, name: str) -> dict[int, int]:
	"""Return timeline for attendance"""

	timesheet_detail = frappe.qb.DocType("Timesheet Detail")

	return dict(
		frappe.qb.from_(timesheet_detail)
		.select(UnixTimestamp(timesheet_detail.from_time), Count("*"))
		.where(timesheet_detail.project == name)
		.where(timesheet_detail.from_time > CurDate() - Interval(years=1))
		.where(timesheet_detail.docstatus < 2)
		.groupby(Date(timesheet_detail.from_time))
		.run()
	)


def get_project_list(doctype, txt, filters, limit_start, limit_page_length=20, order_by="modified"):
	customers, suppliers = get_customers_suppliers("Project", frappe.session.user)

	ignore_permissions = False
	if is_website_user() and frappe.session.user != "Guest":
		if not filters:
			filters = []

		if customers:
			filters.append([doctype, "customer", "in", customers])
			ignore_permissions = True

	meta = frappe.get_meta(doctype)

	fields = "distinct *"

	or_filters = []

	if txt:
		if meta.search_fields:
			for f in meta.get_search_fields():
				if f == "name" or meta.get_field(f).fieldtype in (
					"Data",
					"Text",
					"Small Text",
					"Text Editor",
					"select",
				):
					or_filters.append([doctype, f, "like", "%" + txt + "%"])
		else:
			if isinstance(filters, dict):
				filters["name"] = ("like", "%" + txt + "%")
			else:
				filters.append([doctype, "name", "like", "%" + txt + "%"])

	return frappe.get_list(
		doctype,
		fields=fields,
		filters=filters,
		or_filters=or_filters,
		limit_start=limit_start,
		limit_page_length=limit_page_length,
		order_by=order_by,
		ignore_permissions=ignore_permissions,
	)


def get_list_context(context=None):
	from erpnext.controllers.website_list_for_contact import get_list_context

	list_context = get_list_context(context)
	list_context.update(
		{
			"show_sidebar": True,
			"show_search": True,
			"no_breadcrumbs": True,
			"title": _("Projects"),
			"get_list": get_project_list,
			"row_template": "templates/includes/projects/project_row.html",
		}
	)

	return list_context


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_users_for_project(doctype, txt, searchfield, start, page_len, filters):
	conditions = []
	return frappe.db.sql(
		"""select name, concat_ws(' ', first_name, middle_name, last_name)
		from `tabUser`
		where enabled=1
			and name not in ("Guest", "Administrator")
			and ({key} like %(txt)s
				or full_name like %(txt)s)
			{fcond} {mcond}
		order by
			(case when locate(%(_txt)s, name) > 0 then locate(%(_txt)s, name) else 99999 end),
			(case when locate(%(_txt)s, full_name) > 0 then locate(%(_txt)s, full_name) else 99999 end),
			idx desc,
			name, full_name
		limit %(page_len)s offset %(start)s""".format(
			**{
				"key": searchfield,
				"fcond": get_filters_cond(doctype, filters, conditions),
				"mcond": get_match_cond(doctype),
			}
		),
		{"txt": "%%%s%%" % txt, "_txt": txt.replace("%", ""), "start": start, "page_len": page_len},
	)


@frappe.whitelist()
def get_cost_center_name(project):
	return frappe.db.get_value("Project", project, "cost_center")


def hourly_reminder():
	fields = ["from_time", "to_time"]
	projects = get_projects_for_collect_progress("Hourly", fields)

	for project in projects:
		if get_time(nowtime()) >= get_time(project.from_time) or get_time(nowtime()) <= get_time(
			project.to_time
		):
			send_project_update_email_to_users(project.name)


def project_status_update_reminder():
	daily_reminder()
	twice_daily_reminder()
	weekly_reminder()


def daily_reminder():
	fields = ["daily_time_to_send"]
	projects = get_projects_for_collect_progress("Daily", fields)

	for project in projects:
		if allow_to_make_project_update(project.name, project.get("daily_time_to_send"), "Daily"):
			send_project_update_email_to_users(project.name)


def twice_daily_reminder():
	fields = ["first_email", "second_email"]
	projects = get_projects_for_collect_progress("Twice Daily", fields)
	fields.remove("name")

	for project in projects:
		for d in fields:
			if allow_to_make_project_update(project.name, project.get(d), "Twicely"):
				send_project_update_email_to_users(project.name)


def weekly_reminder():
	fields = ["day_to_send", "weekly_time_to_send"]
	projects = get_projects_for_collect_progress("Weekly", fields)

	current_day = get_datetime().strftime("%A")
	for project in projects:
		if current_day != project.day_to_send:
			continue

		if allow_to_make_project_update(project.name, project.get("weekly_time_to_send"), "Weekly"):
			send_project_update_email_to_users(project.name)


def allow_to_make_project_update(project, time, frequency):
	data = frappe.db.sql(
		""" SELECT name from `tabProject Update`
		WHERE project = %s and date = %s """,
		(project, today()),
	)

	# len(data) > 1 condition is checked for twicely frequency
	if data and (frequency in ["Daily", "Weekly"] or len(data) > 1):
		return False

	if get_time(nowtime()) >= get_time(time):
		return True


@frappe.whitelist()
def create_duplicate_project(prev_doc, project_name):
	"""Create duplicate project based on the old project"""
	import json

	prev_doc = json.loads(prev_doc)

	if project_name == prev_doc.get("name"):
		frappe.throw(_("Use a name that is different from previous project name"))

	# change the copied doc name to new project name
	project = frappe.copy_doc(prev_doc)
	project.name = project_name
	project.project_template = ""
	project.project_name = project_name
	project.insert()

	# fetch all the task linked with the old project
	task_list = frappe.get_all("Task", filters={"project": prev_doc.get("name")}, fields=["name"])

	# Create duplicate task for all the task
	for task in task_list:
		task = frappe.get_doc("Task", task)
		new_task = frappe.copy_doc(task)
		new_task.project = project.name
		new_task.insert()

	project.db_set("project_template", prev_doc.get("project_template"))


def get_projects_for_collect_progress(frequency, fields):
	fields.extend(["name"])

	return frappe.get_all(
		"Project",
		fields=fields,
		filters={"collect_progress": 1, "frequency": frequency, "status": "Open"},
	)


def send_project_update_email_to_users(project):
	doc = frappe.get_doc("Project", project)

	if is_holiday(doc.holiday_list) or not doc.users:
		return

	project_update = frappe.get_doc(
		{
			"doctype": "Project Update",
			"project": project,
			"sent": 0,
			"date": today(),
			"time": nowtime(),
			"naming_series": "UPDATE-.project.-.YY.MM.DD.-",
		}
	).insert()

	subject = "For project %s, update your status" % (project)

	incoming_email_account = frappe.db.get_value(
		"Email Account", dict(enable_incoming=1, default_incoming=1), "email_id"
	)

	frappe.sendmail(
		recipients=get_users_email(doc),
		message=doc.message,
		subject=_(subject),
		reference_doctype=project_update.doctype,
		reference_name=project_update.name,
		reply_to=incoming_email_account,
	)


def collect_project_status():
	for data in frappe.get_all("Project Update", {"date": today(), "sent": 0}):
		replies = frappe.get_all(
			"Communication",
			fields=["content", "text_content", "sender"],
			filters=dict(
				reference_doctype="Project Update",
				reference_name=data.name,
				communication_type="Communication",
				sent_or_received="Received",
			),
			order_by="creation asc",
		)

		for d in replies:
			doc = frappe.get_doc("Project Update", data.name)
			user_data = frappe.db.get_values(
				"User", {"email": d.sender}, ["full_name", "user_image", "name"], as_dict=True
			)[0]

			doc.append(
				"users",
				{
					"user": user_data.name,
					"full_name": user_data.full_name,
					"image": user_data.user_image,
					"project_status": frappe.utils.md_to_html(
						EmailReplyParser.parse_reply(d.text_content) or d.content
					),
				},
			)

			doc.save(ignore_permissions=True)


def send_project_status_email_to_users():
	yesterday = add_days(today(), -1)

	for d in frappe.get_all("Project Update", {"date": yesterday, "sent": 0}):
		doc = frappe.get_doc("Project Update", d.name)

		project_doc = frappe.get_doc("Project", doc.project)

		args = {"users": doc.users, "title": _("Project Summary for {0}").format(yesterday)}

		frappe.sendmail(
			recipients=get_users_email(project_doc),
			template="daily_project_summary",
			args=args,
			subject=_("Daily Project Summary for {0}").format(d.name),
			reference_doctype="Project Update",
			reference_name=d.name,
		)

		doc.db_set("sent", 1)


def update_project_sales_billing():
	sales_update_frequency = frappe.db.get_single_value("Selling Settings", "sales_update_frequency")
	if sales_update_frequency == "Each Transaction":
		return
	elif sales_update_frequency == "Monthly" and frappe.utils.now_datetime().day != 1:
		return

	# Else simply fallback to Daily
	exists_query = "(SELECT 1 from `tab{doctype}` where docstatus = 1 and project = `tabProject`.name)"
	project_map = {}
	for project_details in frappe.db.sql(
		"""
			SELECT name, 1 as order_exists, null as invoice_exists from `tabProject` where
			exists {order_exists}
			union
			SELECT name, null as order_exists, 1 as invoice_exists from `tabProject` where
			exists {invoice_exists}
		""".format(
			order_exists=exists_query.format(doctype="Sales Order"),
			invoice_exists=exists_query.format(doctype="Sales Invoice"),
		),
		as_dict=True,
	):
		project = project_map.setdefault(
			project_details.name, frappe.get_doc("Project", project_details.name)
		)
		if project_details.order_exists:
			project.update_sales_amount()
		if project_details.invoice_exists:
			project.update_billed_amount()

	for project in project_map.values():
		project.save()


@frappe.whitelist()
def create_kanban_board_if_not_exists(project):
	from frappe.desk.doctype.kanban_board.kanban_board import quick_kanban_board

	project = frappe.get_doc("Project", project)
	if not frappe.db.exists("Kanban Board", project.project_name):
		quick_kanban_board("Task", project.project_name, "status", project.name)

	return True


@frappe.whitelist()
def set_project_status(project, status):
	"""
	set status for project and all related tasks
	"""
	if status not in ("Completed", "Cancelled"):
		frappe.throw(_("Status must be Cancelled or Completed"))

	project = frappe.get_doc("Project", project)
	frappe.has_permission(doc=project, throw=True)

	for task in frappe.get_all("Task", dict(project=project.name)):
		frappe.db.set_value("Task", task.name, "status", status)

	project.status = status
	project.save()


def get_holiday_list(company=None):
	if not company:
		company = get_default_company() or frappe.get_all("Company")[0].name

	holiday_list = frappe.get_cached_value("Company", company, "default_holiday_list")
	if not holiday_list:
		frappe.throw(
			_("Please set a default Holiday List for Company {0}").format(frappe.bold(get_default_company()))
		)
	return holiday_list


def get_users_email(doc):
	return [d.email for d in doc.users if frappe.db.get_value("User", d.user, "enabled")]


def calculate_total_purchase_cost(project: str | None = None):
	
	if project:
		pitem = qb.DocType("Purchase Invoice Item")
		frappe.qb.DocType("Purchase Invoice Item")
		total_purchase_cost = (
			qb.from_(pitem)
			.select(Sum(pitem.base_net_amount))
			.where((pitem.project == project) & (pitem.docstatus == 1))
			.run(as_list=True)
		)
		#total_purchase_cost="1000000"
		##frappe.throw(str(total_purchase_cost))
		return total_purchase_cost
	return None


@frappe.whitelist()
def recalculate_project_total_purchase_cost(project: str | None = None):
	if project:
		total_purchase_cost = calculate_total_purchase_cost(project)
		frappe.db.set_value(
			"Project",
			project,
			"total_purchase_cost",
			(total_purchase_cost and total_purchase_cost[0][0] or 0),
		)

""" ************************************************************************* """
""" custom function starts from here,  codes from old cdcl erp"""
@frappe.whitelist()
def change_status_ongoing(project_id):
	frappe.db.sql("Update `tabProject` set status = 'Ongoing', docstatus = 0 where name = '{}'".format(project_id))
	return 1

# ++++++++++++++++++++ Ver 2.0 BEGINS ++++++++++++++++++++
# Following method is created by SHIV on 02/09/2017
@frappe.whitelist()
def make_project_advance(source_name, target_doc=None):
	def update_master(source_doc, target_doc, source_partent):
		#target_doc.customer = source_doc.customer
		pass
	
	doclist = get_mapped_doc("Project", source_name, {
		"Project": {
				"doctype": "Project Advance",
				"field_map":{
					"name": "project",
					"party_type": "party_type",
					"party": "party",
					"party_address": "party_address"
				},
				"postprocess": update_master
		}
	}, target_doc)
	return doclist


@frappe.whitelist()
def make_boq(source_name, target_doc=None):
	def update_master(source_doc, target_doc, source_partent):
		pass
	
	doclist = get_mapped_doc("Project", source_name, {
		"Project": {
				"doctype": "BOQ",
				"field_map":{
						"name": "project",
				},
				"postprocess": update_master
			}
	}, target_doc)
	return doclist

@frappe.whitelist()
def extension_of_time(source_name, target_doc=None):
	def update_master(source_doc, target_doc, source_partent):
		pass
	
	doclist = get_mapped_doc("Project", source_name, {
		"Project": {
				"doctype": "Extension of Time",
				"field_map":{
						"name": "project",
				},
				"postprocess": update_master
			}
	}, target_doc)
	return doclist

@frappe.whitelist()
def sent_dlp_mail(project):
	dlp_email_list = frappe.db.sql("select e.user_id from tabProject p, `tabDLP Email List` e \
				where e.parent=p.name and p.name='{0}'".format(project), as_dict=1)
	if dlp_email_list:
		recipients = [a['user_id'] for a in dlp_email_list if frappe.db.get_value("User", a['user_id'], "enabled") == 1]
		
		if not recipients:
			recipients = get_users_with_role("Project Manager")
		
		subject = _("Defect Liability Period Notification")
		message = (
			_("Dear Sir/Madam,")
			+ "<br><br>"
			+ _("The Project: {0} is left with 6 days of defect liability expiry date").format(
				doc.name
			)
		)
		frappe.sendmail(recipients=recipients, subject=subject, message=message)

@frappe.whitelist()
def update_project_dlp_date():
	for doc in frappe.db.get_all("Project", {"docstatus": ("!=", 1)}):
		self = frappe.get_doc("Project", doc.name)
		if self.dlp_start_date and self.dlp_end_date:
			if getdate(today()) > getdate(self.dlp_end_date):
				return
			remaining_days = date_diff(self.dlp_end_date, today())
			# frappe.throw(f'here {remaining_days}')
			self.db_set('remaining_days', remaining_days, update_modified=False)
			if remaining_days == 6 and self.sent_email_notification:
				sent_dlp_mail(self.name)


def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user
	user_roles = frappe.get_roles(user)
	if "Administrator" in user_roles or "HR Manager" or  "Auditor" in user_roles:
		return

	if "HR User" in user_roles or "Employee" in user_roles or "Projects User" in user_roles:

		assign_branch_name = frappe.db.get_value(
			"Assign Branch",
			{"user": user},
			"name"
		)

		if assign_branch_name:
			# Get branches from child table
			branches = frappe.get_all(
				"Branch Item",
				filters={"parent": assign_branch_name},
				pluck="branch"
			)

			if branches:
				branches = "', '".join(branches)
				return f"`tabProject`.`branch` IN ('{branches}')"
		return "1=0"
