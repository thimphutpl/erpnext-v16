// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// Hide all default Frappe chart containers via CSS
(function() {
	const style = document.createElement('style');
	style.innerHTML = `
	  .chart-wrapper, .frappe-chart, .report-chart, .chart-container, .chart-container svg {
		display: none !important;
		height: 0 !important;
		min-height: 0 !important;
		max-height: 0 !important;
		padding: 0 !important;
		margin: 0 !important;
	  }
	`;
	document.head.appendChild(style);
})();

// Utility function to load external scripts like Chart.js and plugins
function load_script(src) {
	return new Promise((resolve, reject) => {
		const script = document.createElement("script");
		script.src = src;
		script.onload = resolve;
		script.onerror = reject;
		document.head.appendChild(script);
	});
}

frappe.query_reports["Project Progress Graphs"] = {
	filters: [
		{
			fieldname: "project_defination",
			label: "Project Definition",
			fieldtype: "Link",
			options: "Project Definition",
		},
		{
			fieldname: "project",
			label: "Project",
			fieldtype: "Link",
			options: "Project",
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 1
		},
		{
			fieldname: "range",
			label: __("Range"),
			fieldtype: "Select",
			options: [{ value: "Monthly", label: __("Monthly") }],
			default: "Monthly",
			reqd: 0
		}
	],

	onload: async function(report) {		
		await load_script("https://cdn.jsdelivr.net/npm/chart.js");
		await load_script("https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom");
		if (window.Chart && window.Chart.register && window.ChartZoom) {
			window.Chart.register(window.ChartZoom);
		}
		report.chart = null;		
	},

	after_datatable_render: function(report) {
		frappe.call({
			method: "erpnext.projects.report.project_progress_graphs.project_progress_graphs.execute",
			args: {
				report_name: "Project Progress Graphs",
				filters: frappe.query_report.get_filter_values()
			},
			callback: function(r) {
				let chart_data = null;
				if (r && r.message && r.message[3]) {
					chart_data = r.message[3];
				}
				console.log("Fetched chart data:", chart_data);
				if (!window.Chart || !chart_data || !chart_data.data) {
					console.warn("Chart.js or chart data missing!");
					return;
				}

				let wrapper = document.body;
				if (
					frappe.query_report.page &&
					frappe.query_report.page.wrapper &&
					typeof frappe.query_report.page.wrapper.querySelector === 'function'
				) {
					wrapper = frappe.query_report.page.wrapper;
				}

				let datatable = wrapper.querySelector('.dt-scrollable');
				let chart_div = wrapper.querySelector("#chartjs-canvas");
				let scroll_wrapper;

				if (!chart_div) {
					const msg_div = document.createElement("div");
					msg_div.textContent = "Progress Graph! If the achievement bar is above the target bar, we are ahead of the schedule";
					msg_div.style.fontWeight = 'medium';
					msg_div.style.fontSize = '0.8rem';
					msg_div.style.marginBottom = '0.5rem';
					msg_div.style.color = '#333';
					msg_div.style.marginLeft = '25px';

					chart_div = document.createElement("canvas");
					chart_div.id = "chartjs-canvas";
					chart_div.height = 300;
					chart_div.style.maxHeight = '300px';
					chart_div.style.height = '300px';
					chart_div.style.maxWidth = '100%';
					chart_div.style.display = 'block';

					scroll_wrapper = document.createElement("div");
					scroll_wrapper.classList.add("custom-chart-wrapper");
					scroll_wrapper.style.overflowX = "auto";
					scroll_wrapper.style.padding = "0.5rem 0";
					scroll_wrapper.style.background = "#fff";
					
					scroll_wrapper.appendChild(msg_div);
					scroll_wrapper.appendChild(chart_div);

					if (datatable && datatable.parentNode) {
						datatable.parentNode.insertBefore(scroll_wrapper, datatable.parentNode.firstChild);
					} else {
						wrapper.prepend(scroll_wrapper);
					}
				} else {
					scroll_wrapper = chart_div.parentElement;
					chart_div.height = 300;
					chart_div.style.maxHeight = '300px';
					chart_div.style.height = '300px';
					const ctx = chart_div.getContext("2d");
					ctx && ctx.clearRect(0, 0, chart_div.width, chart_div.height);
				}

				if (window.chartjs_instance) {
					window.chartjs_instance.destroy();
				}

				// Get the content/container width dynamically
				const parentWidth = (wrapper && wrapper.offsetWidth) ? wrapper.offsetWidth : 1000;
				const perLabelWidth = 80;
				const labels = chart_data.data.labels;
				const chartWidth = Math.max(labels.length * perLabelWidth, parentWidth);

				chart_div.width = chartWidth;
				chart_div.style.width = chartWidth + "px";
				chart_div.style.minWidth = chartWidth + "px";

				// Center if not scrolling
				if (chartWidth === parentWidth) {
					scroll_wrapper.style.justifyContent = "center";
					scroll_wrapper.style.display = "flex";
				} else {
					scroll_wrapper.style.justifyContent = "flex-start";
					scroll_wrapper.style.display = "block";
				}

				const datasets = chart_data.data.datasets.map(ds => ({
					label: ds.name,
					data: ds.values,
					fill: false,
					borderColor: ds.name === "Target" ? "#5e64ff" : "#63d0ff",
					backgroundColor: ds.name === "Target" ? "#5e64ff" : "#63d0ff",
					tension: 0.3,
					pointRadius: 3
				}));

				const ctx = chart_div.getContext("2d");
				window.chartjs_instance = new Chart(ctx, {
					type: 'line',
					data: {
						labels: labels,
						datasets: datasets
					},
					options: {
						responsive: false,
						maintainAspectRatio: false,
						plugins: {
							legend: {
								labels: {
									font: { size: 13 }
								}
							},
							tooltip: {
								mode: 'index',
								intersect: false,
								titleFont: { size: 13 },
								bodyFont: { size: 12 }
							},
							zoom: {
								zoom: {
									wheel: { enabled: true, speed: 0.002 },
									pinch: { enabled: true, speed: 0.002},
									mode: 'x'
								},
								pan: {
									enabled: true,
									mode: 'x'
								}
							}
						},
						interaction: {
							mode: 'nearest',
							axis: 'x',
							intersect: false
						},
						scales: {
							x: {
								title: {
									display: true,
									text: 'Period',
									font: { size: 13 }
								},
								ticks: { font: { size: 12 } }
							},
							y: {
								title: {
									display: true,
									text: 'Progress (%)',
									font: { size: 13 }
								},
								ticks: { font: { size: 12 } },
								beginAtZero: true,
							}
						}
					}
				});
			}
		});
	},
};
