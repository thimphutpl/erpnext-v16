from frappe import _


def get_data():
	return {
		"heatmap": True,
		"heatmap_message": _("This is based on the Time Sheets created against this project"),
		"fieldname": "project",
		"transactions": [
			{
				"label": _("Project"),
				"items": ["Task", "Timesheet", "Issue", "Project Update"],
			},
			{"label": _("Material"), "items": ["BOM", "Material Request", "Stock Entry", "BOQ", "BOQ Adjustment"]},
			# {"label": _("Sales"), "items": ["Sales Order", "Delivery Note", "Sales Invoice"]},
			{"label": _("Purchase"), "items": ["Purchase Order", "Purchase Receipt", "Purchase Invoice"]},
			{"label": _("Transactions"), "items": ["Project Advance", "Project Invoice", "Project Payment", "MB Entry"]},
		],
	}
