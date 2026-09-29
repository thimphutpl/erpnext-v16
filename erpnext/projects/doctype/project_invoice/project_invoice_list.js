frappe.listview_settings['Project Invoice']={
	add_fields: ["status","docstatus","total_balance_amount","total_received_amount","total_paid_amount","net_invoice_amount","party_type","party"],
	filters: [["status", "=", "Unpaid"]],
	get_indicator: function(doc){
		var colors = {
			"Draft": "red",
			"Unpaid": "orange",
			"Paid": "green",
			"Cancelled": "darkgrey"
		};		

		//console.log(cur_list);
		//return [__(doc.status), colors[doc.status], "status,=," + doc.status];

		var balance = 0.0;
		
		if(parseFloat(doc.total_received_amount || 0.0) > 0.0 || parseFloat(doc.total_paid_amount || 0.0) > 0.0){
			balance = 100-Math.round((parseFloat(doc.total_received_amount || 0.0)+parseFloat(doc.total_paid_amount || 0.0))/parseFloat(doc.net_invoice_amount || 1)*100);
		}
		else{
			balance = 100;
		}
		
		
		if(doc.status == "Draft"){
			return [__("Draft"), "orange", "status,=," + doc.status];
		}
		else if(parseFloat(doc.total_balance_amount) > 0.0 || doc.status == "Unpaid"){
			return [__("{0}% {1}", [balance, ((doc.party_type==="Supplier")? "Payable" : "Receivable")]), "red", "status,=," + doc.status];
		}
		else if(parseFloat(doc.total_balance_amount) == 0.0 || doc.status == "Paid"){
			return [__("{0}", [((doc.party_type==="Supplier")? "Paid" : "Received")]), "green", "status,=," + doc.status];
		}
		else if(doc.docstatus==2 || doc.status == "Cancelled"){
			return [__("Cancelled"), "darkgrey", "status,=," + doc.status];
		}
	}
};