import frappe
import electronic_tender.controllers.tender as tender_controller

def collect_tenders():
    tenders = frappe.db.sql(
        """
        SELECT name FROM `tabTender`
        """,
    )
    for tender in tenders:
        tender_controller.tender_summary(tender)