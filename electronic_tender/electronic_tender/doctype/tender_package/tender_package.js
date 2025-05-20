// Copyright (c) 2025, Orient AI and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tender Package", {
	refresh(frm) {
		frm.add_custom_button("Summary", () => tenderPackageSummary(frm), "Actions");
		if (frm.doc.status == "Draft") {
			frm.add_custom_button("Publish", () => tenderPackagePublish(frm), "Actions");
		}
		if (
			frm.doc.status == "Draft" &&
			frm.doc.is_bridged == 0 &&
			frm.doc.is_imported == 1
		) {
			if (frm.doc.import_status == "Idle") {
				frm.add_custom_button("Process", () => enqueueTenderLotImport(frm), "Import");
			} else if (frm.doc.import_status == "Processing") {
				// frm.add_custom_button("Cancel", () => cancelTenderLotImport(frm), "Cancel");
			} else if (frm.doc.import_status == "Failed") {
				frm.add_custom_button("Retry", () => enqueueTenderLotImport(frm), "Import");
			} else if (frm.doc.import_status == "Completed") {
				frm.add_custom_button(
					"Re-import",
					() => {
                        enqueueTenderLotImport(frm, true);
					},
					"Import"
				);
			}
		}

		if (frm.doc.filter) {
			frm.set_value("filter", JSON.stringify(JSON.parse(frm.doc.filter), null, 4));
		}
	},
});

function tenderPackageSummary(frm) {
	frappe.call({
		method: "electronic_tender.controllers.tender_package.tender_package_summary",
		args: { tender_package: frm.doc.name },
	});
}

function enqueueTenderLotImport(frm, restart = false) {
	frappe.call({
		method: "electronic_tender.controllers.tender_package.enqueue_tender_lot_import",
		args: {
			tender_package: frm.doc.name,
			restart: restart,
		},
		callback: function (r) {
			if (r.message === "queued") {
				frappe.show_alert({
					message: __("Tender Lot Import has been queued."),
					indicator: "green",
				});
			}
		},
	});
}
