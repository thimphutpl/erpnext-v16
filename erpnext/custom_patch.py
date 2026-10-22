import frappe

def update_salary():
	sal=frappe.db.sql(""" select name from `tabSalary Structure`""",as_dict=1)
	for s in sal:
		doc=frappe.get_doc("Salary Structure",s.name)
		doc.save()
		frappe.db.commit()
