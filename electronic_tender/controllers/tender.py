import frappe

@frappe.whitelist()
def tender_summary(tender):
    tender = frappe.get_doc("Tender", tender)
    summary = frappe.db.sql(
        """
        SELECT
            COUNT(1) AS processing_tender_lots
        FROM `tabTender Lot`
        WHERE tender = %s AND status = "Processing"
        """,
        (tender.name)
    )
    tender.number_of_processing_lots = summary[0][0]
    tender.save()