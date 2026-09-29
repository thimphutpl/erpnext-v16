frappe.listview_settings['MB Entry']={
	add_fields: ["name", "status", "entry_date", "total_balance_amount"],
	filters: [["status", "=", "Uninvoiced"]],
	get_indicator: function(doc){
		var colors = {
			"Draft": "orange",
			"Uninvoiced": "red",
			"Invoiced": "green",
			"Cancelled": "dark grey"
		}		

		return [__(doc.status), colors[doc.status], "status,=," + doc.status];
		/*
		if(doc.status == "Draft"){
			return [__("Draft"), "orance", "status,=," + doc.status];
		}
		else if(parseFloat(doc.total_balance_amount) > 0.0 || doc.status == "Unpaid"){
			//return [__(doc.status), colors[doc.status], "status,=," + doc.status];
			return [__("Unpaid"), "red", "status,=," + doc.status];
		}
		else if(parseFloat(doc.total_balance_amount) == 0.0 || doc.status == "Paid"){
			return [__("Paid"), "green", "status,=," + doc.status];
		}
		else if(doc.docstatus==2 || doc.status == "Cancelled"){
			return [__("Cancelled"), "dark grey", "status,=," + doc.status];
		}
		*/
	}
};