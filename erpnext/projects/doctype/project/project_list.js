frappe.listview_settings["Project"] = {
	add_fields: ["status", "priority", "is_active", "percent_complete", "tot_wq_percent_complete", "tot_wq_percent", "expected_end_date", "project_name"],
	filters: [["status", "=", "Open"]],
	get_indicator: function (doc) {
		// if (doc.status == "Open" && doc.percent_complete) {
		// 	return [__("{0}%", [cint(doc.percent_complete)]), "orange", "percent_complete,>,0|status,=,Open"];
		// } else {
		if(parseFloat(doc.tot_wq_percent_complete) < parseFloat(doc.tot_wq_percent)){
			return [__("{0}%", [Math.round(doc.tot_wq_percent_complete)]), "orange", "tot_wq_percent_complete,>=,0|status,=,Ongoing"];
		} else if(parseFloat(doc.tot_wq_percent_complete) >= parseFloat(doc.tot_wq_percent)){
			return [__("{0}%", [Math.round(doc.tot_wq_percent_complete)]), "green", "tot_wq_percent_complete,>=,"+doc.tot_wq_percent+"|status,=,"+doc.status];
		} else {
			return [__(doc.status), frappe.utils.guess_colour(doc.status), "status,=," + doc.status];
		}
	},
};
