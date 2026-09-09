from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'project_definition',
		'non_standard_fieldnames': {
			'Material Request': 'reference_name',
		},
		'transactions': [
			{
				'label': _('Projects'),
				'items': ['Project']
			},
			{
				'label': _('SETTLEMENT'),
				'items': ['Monthly Project Settlement']
			},
			{
				'label': _('Material'),
				'items': ['Material Request']
			},
		]
	}