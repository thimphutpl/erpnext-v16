# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from frappe.model.document import Document


class Branch(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		branch: DF.Data
		company: DF.Link
		cost_center: DF.Link
		disabled: DF.Check
		expense_bank_account: DF.Link | None
<<<<<<< HEAD
=======
		holiday_list: DF.Link | None
>>>>>>> 7502b1f16ba846639bbfb0f8f917d068bc1f0324
		revenue_bank_account: DF.Link | None
	# end: auto-generated types

	pass
