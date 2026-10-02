frappe.listview_settings['Project Payment']={
	add_fields: ["project", "status", "posting_date", "total_amount"],
	filters: [["status", "=", "Draft"]],
	get_indicator: function(doc){
		var colors = {
			"Open": "orange",
			"Overdue": "red",
			"Pending Review": "orange",
			"Working": "orange",
			"Closed": "green",
			"Cancelled": "dark grey",
			"Draft": "red",
			"Submitted": "green",
			"Cancelled": "dark grey",
			"Payment Received": "green"
		}		
		
		if(doc.docstatus==0 || doc.status == "Draft"){
			//return [__(doc.status), colors[doc.status], "status,=," + doc.status];
			return [__(doc.status), "red", "status,=," + doc.status];
		}
		else if(doc.docstatus==1 || doc.status == "Received" || doc.status == "Paid"){
			return [__(doc.status), "green", "status,=," + doc.status];
		}
		else if(doc.docstatus==2 || doc.status == "Cancelled"){
			return [__("Cancelled"), "dark grey", "status,=," + doc.status];
		}
	}
};