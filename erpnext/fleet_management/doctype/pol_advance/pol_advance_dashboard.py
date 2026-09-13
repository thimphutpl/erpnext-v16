from frappe import _

def get_data():
	return {
		"fieldname": "name",  # assuming Journal Entry stores POL Advance's name in its reference_name
		"non_standard_fieldnames": {
			"Journal Entry": "reference_name",
		},
		"transactions": [
			{
				"label": _("Accounting"),
				"items": ["Journal Entry"]
			}
		]
	}
