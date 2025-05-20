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

def collect_tender_packages():
    frappe.db.sql(
        """
        UPDATE `tabTender Package`
        SET status = "Closed"
        WHERE close_time_ts < UNIX_TIMESTAMP() - 120
        """
    )
    

def collect_tender_lots():
    frappe.db.sql(
        """
        UPDATE `tabTender Lot`
        SET status = "Closed"
        WHERE close_time_ts < UNIX_TIMESTAMP() - 60
        """
    )