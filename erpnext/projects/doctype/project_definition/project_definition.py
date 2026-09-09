# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals
import frappe
from frappe.utils import flt, getdate, get_url, today
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
import datetime
# from erpnext.custom_utils import get_branch_cc
from frappe.model.naming import make_autoname
from datetime import date

class ProjectDefinition(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.projects.doctype.ongoing_project_item.ongoing_project_item import OngoingProjectItem
		from frappe.types import DF

		a_expenses: DF.Data | None
		budget_profile: DF.Literal["", "Annually", "Overall"]
		company: DF.Link | None
		cost_center: DF.Link | None
		cost_center_mandays: DF.Data | None
		end_date: DF.Date
		f_progress: DF.Data | None
		fiscal_year: DF.Link | None
		freeze_project: DF.Check
		overall_mandays: DF.Data | None
		percent_completed: DF.Percent
		physical_progress: DF.Percent
		physical_progress_weightage: DF.Percent
		project_category: DF.Literal["", "GI Project", "DFG Project", "Other Project"]
		project_code: DF.Data | None
		project_code_prefix: DF.Literal["", "GI-J", "GI-K", "GI-T", "GI-P", "GI-G", "GI"]
		project_man_days: DF.Data | None
		project_manager: DF.Link | None
		project_manager_designation: DF.Link | None
		project_manager_name: DF.Data | None
		project_name: DF.Data
		project_profile: DF.Literal["", "Internal", "External"]
		project_sites: DF.Table[OngoingProjectItem]
		provisional_estimated_budget: DF.Data | None
		start_date: DF.Date
		status: DF.Literal["Created", "Ongoing", "Completed"]
		total_overall_project_cost: DF.Currency
	# end: auto-generated types
	def autoname(self):
		self.name = "GI-"+self.project_code+" - GYALSUNG"

	def validate(self):
		self.validate_project_profile()
		self.update_same_cost_center_mandays()
	
	def before_cancel(self):
		project_list = frappe.db.get_list("Project",filters={"project_definition":self.name,"docstatus":["!=",2]})
		if len(project_list)>0:
			frappe.throw("Project Definition {} is linked with Projects {}".format(self.name,project_list))

	def validate_project_profile(self):
		if self.project_profile == "External" and "Accounts Manager" not in frappe.get_roles(frappe.session.user):
			frappe.throw("Please select project profile as Internal.", title = "Invalid Selection")
	def update_same_cost_center_mandays(self):
		mandays = frappe.db.sql("""select sum(project_man_days) from `tabProject Definition` where cost_center = '{}' and docstatus = 1""".format(self.cost_center), as_dict=1)[0]['sum(project_man_days)']
		if not mandays:
			mandays=1
		frappe.db.sql("""update `tabProject Definition` set cost_center_mandays = {} where name = '{}'""".format(mandays, self.name))
		# self.cost_center_mandays = mandays
	#added by Kinley 16/01/2025
	@frappe.whitelist()
	def update_project_progress(self):
		self.update_same_cost_center_mandays()
		if not self.project_category:
			frappe.throw("Please project categoy")
		if self.docstatus == 1:
			for pc in frappe.db.get_all("Project Definition", {"project_category": self.project_category, "docstatus":1}, ["name"]):
				project_man_days = overall_mandays = physical_progress_weightage = physical_progress = no_of_projects = no_of_project_definitions = 0
				contribution_per_prj = frappe.db.sql("""
									select sum(ifnull(percent_completed, 0)) as wqc from `tabProject` where project_definition = '{}'
									""".format(pc.name), as_dict=1)[0].wqc

				for prj in frappe.db.get_all("Project", {"project_definition": pc.name}, ["mandays", "physical_progress"]):
					if not prj.mandays:
						prj.mandays = 0
					project_man_days += flt(prj.mandays,2)
					if not prj.physical_progress:
						prj.physical_progress = 0
					physical_progress += flt(prj.physical_progress,4)
					no_of_projects += 1
				frappe.db.sql("""
						update `tabProject Definition` set project_man_days = {} where name = '{}'
						""".format(project_man_days, pc.name))

				for pd in frappe.db.get_all("Project Definition", {"docstatus": 1, "project_category": self.project_category}, ["project_man_days"]):
					if not pd.project_man_days:
						pd.project_man_days = 0
					overall_mandays += flt(pd.project_man_days,2)
					no_of_project_definitions += 1
				physical_progress_weightage = flt(flt(project_man_days) / flt(overall_mandays)*100,3)
				if no_of_projects > 0:
					contribution_per_prj = flt(physical_progress_weightage*(flt(physical_progress)*0.01),4)
				# physical_progress = flt(flt(physical_progress_weightage) * (contribution_per_prj * 0.01),4)


				frappe.db.sql("""
						update `tabProject Definition` set overall_mandays = {}, physical_progress_weightage = {}, physical_progress = {}, percent_completed = {} where name = '{}'
						""".format(overall_mandays, physical_progress_weightage, contribution_per_prj, physical_progress, pc.name))
				# frappe.db.commit()	
	@frappe.whitelist()
	def check_logged_in_user_role(self):
		#return values initialization-----------------
		freeze_project = 1
		#----------------------------Supervisor------------------------------------------------------------------------------------------------------------------------------------------------------------|
		user = frappe.session.user
		user_roles = frappe.get_roles(user)

		if user == "Administrator":
			freeze_project = 0
		if "Freeze Project" in user_roles:
			freeze_project = 0
		
		return freeze_project 
# ADDED BY Kinley ON 04-06-2024
@frappe.whitelist()
def make_purchase_requisition(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.material_request_type = "Purchase"
		target.reference_type = "Project Definition"
		target.reference_name = source.name
		target.creation_date = date.today()
		target.for_project = 1
		target.branch = frappe.db.get_value("Branch", {"cost_center":source.cost_center}, "name")
		# target.site = frappe.db.get_value("Project", source.project, "site")

	doc = get_mapped_doc("Project Definition", source_name,	{
		"Project Definition": {
			"doctype": "Material Request",
			"field_map": {
				"name" : "reference_name",
			},
		},
	}, target_doc, set_missing_values)

	return doc

@frappe.whitelist()
def make_material_issue_request(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.material_request_type  = "Material Issue"
		target.reference_type = "Project Definition"
		target.reference_name = source.name
		target.creation_date = date.today()
		target.for_project = 1
		target.branch = frappe.db.get_value("Branch", {"cost_center":source.cost_center}, "name")
		# target.site = frappe.db.get_value("Project", source.project, "site")

	doc = get_mapped_doc("Project Definition", source_name,	{
		"Project Definition": {
			"doctype": "Material Request",
			"field_map": {
				"name" : "reference_name",
			},
		},
	}, target_doc, set_missing_values)

	return doc

@frappe.whitelist()
def make_stock_issue_entry(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.stock_entry_type  = "Material Issue"
		target.reference_type = "Project Definition"
		target.reference_name = source.name
		target.creation_date = date.today()
		target.for_project = 1
		target.branch = frappe.db.get_value("Branch", {"cost_center":source.cost_center}, "name")
		# target.site = frappe.db.get_value("Project", source.project, "site")

	doc = get_mapped_doc("Project Definition", source_name,	{
		"Project Definition": {
			"doctype": "Stock Entry",
			"field_map": {
				"name" : "reference_name",
			},
		},
	}, target_doc, set_missing_values)

	return doc

@frappe.whitelist()
def make_stock_return_entry(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.stock_entry_type  = "Material Return"
		target.reference_type = "Project Definition"
		target.reference_name = source.name
		target.creation_date = date.today()
		target.for_project = 1
		target.branch = frappe.db.get_value("Branch", {"cost_center":source.cost_center}, "name")
		# target.site = frappe.db.get_value("Project", source.project, "site")

	doc = get_mapped_doc("Project Definition", source_name,	{
		"Project Definition": {
			"doctype": "Stock Entry",
			"field_map": {
				"name" : "reference_name",
			},
		},
	}, target_doc, set_missing_values)

	return doc

@frappe.whitelist()
def make_project(source_name, target_doc=None):
	def update_date(obj, target, source_parent):
		target.supervisor = None
	def set_missing_values(source, target):
		target.project_name = None
		target.branch = frappe.db.get_value("Branch", {"cost_center": source.cost_center})
	doc = get_mapped_doc("Project Definition", source_name, {
			"Project Definition": {
				"doctype": "Project",
				"field_map": {
					"name": "project_definition",
					"project_profile": "project_type"
				},
				"postprocess": update_date,
				"validation": {"docstatus": ["=", 1]}
			},
		}, target_doc, set_missing_values)
	# project_region = frappe.db.sql("select region from `tabRegion Item` where parent='{}'".format(source_name),as_dict=True)
	# data = get_mapped_doc("Project Definiftion", source_name, {
	# 	"Project Definition":{
	# 		"doctype": "Project",
	# 		"field_map": {
	# 			project_region[0][1]: "region"
	# 		},
	# 		"postprocess": update_date,
	# 		"validation": {"docstatus": ["=", 1]}
	# 	},
	# }, target_doc)
	#frappe.throw("project:{}".format(project_region))
	
	return doc


@frappe.whitelist()
def monthly_settlement(source_name, target_doc=None):
	def update_date(obj, target, source_parent):
		target.supervisor = None
		target.purpose = "Settlement"
	doc = get_mapped_doc("Project Definition", source_name, {
			"Project Definition": {
				"doctype": "Monthly Project Settlement",
				"field_map": {"project_profile": "project_type"},
				"postprocess": update_date,
				"validation": {"docstatus": ["!=", 1]}
			},
		}, target_doc)

	return doc

@frappe.whitelist()
def get_project_cost(project_definition):
	project_names = frappe.db.sql("select site_name as name from `tabOngoing Project Item` where parent='{}'".format(project_definition),as_dict=1)
	for item in project_names:
		total_cost = frappe.db.sql("select total_cost from `tabProject` where name='{}'".format(item.name),as_dict=1)
		if total_cost:
			frappe.db.sql("update `tabOngoing Project Item` set total_cost={} where parent='{}' and site_name='{}'".format(total_cost[0].total_cost, project_definition, item.name))

# Following code added by SHIV on 2021/05/13
def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles or "Projects GM" in user_roles:
		return

	return """(
		exists(select 1
			from `tabEmployee` as e
			where e.branch = `tabProject`.branch
			and e.user_id = '{user}')
		or
		exists(select 1
			from `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
			where e.user_id = '{user}'
			and ab.employee = e.name
			and bi.parent = ab.name
			and bi.branch = `tabProject`.branch)
	)""".format(user=user)

