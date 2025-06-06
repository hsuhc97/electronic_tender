import frappe
import os
import json
import traceback
import requests
import pandas as pd
from typing import List, Dict

@frappe.whitelist()
def enqueue_tender_lot_import(tender_package, restart = False):
    tender_package = frappe.get_doc("Tender Package", tender_package)
    if (tender_package.status != "Draft"):
        frappe.throw(
            "{0} is in {1} status, only Draft status is allowed".format(
                tender_package.name, tender_package.status
            )
        )
    if (tender_package.import_file == None):
        frappe.throw(
            "{0} has no import file".format(
                tender_package.name
            )
        )
    if (tender_package.tender_lot_import_template == None):
        frappe.throw(
            "{0} has no tender lot import template".format(
                tender_package.name
            )
        )
    if (tender_package.number_of_total_rows == 0 or restart):
        frappe.enqueue(
            "electronic_tender.controllers.tender_package.tender_lot_import_prepare",
            enqueue_after_commit=True,
            tender_package=tender_package.name,
        )
    else:
        frappe.enqueue(
            "electronic_tender.controllers.tender_package.tender_lot_import_process",
            enqueue_after_commit=True,
            tender_package=tender_package.name,
            row_number=tender_package.number_of_processed_rows
        )
    return "queued"


def tender_lot_import_prepare(tender_package):
    try:
        tender_package = frappe.get_doc("Tender Package", tender_package)
        # 删除原来的tender_lot
        frappe.db.delete("Tender Lot", {"tender_package": tender_package.name})
        
        folder_name = "/tmp/tender_package_import"
        os.makedirs(folder_name, exist_ok=True)
        file_name = os.path.join(folder_name, tender_package.name)
        if os.path.exists(file_name):
            os.remove(file_name)

        file_url = tender_package.import_file
        try:
            response = requests.get(file_url, stream=True)
            response.raise_for_status()
            with open(file_name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        except Exception as ie:
            raise RuntimeError(f"File download failed: {ie}")

        df = pd.read_excel(file_name, header=None)
        total_rows = len(df)
        tender_package.import_status = "Processing"
        tender_package.why_failed = ""
        tender_package.number_of_lots = 0
        tender_package.quantity = 0
        tender_package.filter = json.dumps({})
        tender_package.number_of_total_rows = total_rows
        tender_package.number_of_processed_rows = 0
        tender_package.save()
        frappe.enqueue(
            "electronic_tender.controllers.tender_package.tender_lot_import_process",
            enqueue_after_commit=True,
            tender_package=tender_package.name,
            row_number=0
        )
    except Exception as e:
        frappe.db.rollback()
        detailed_error = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        frappe.db.set_value("Tender Package", tender_package, {
            "import_status": "Failed",
            "why_failed": detailed_error
        })


def tender_lot_import_process(tender_package, row_number=0):
    try:
        tender_package = frappe.get_doc("Tender Package", tender_package)
        start_row_number = row_number
        template = frappe.get_doc("Tender Lot Import Template", tender_package.tender_lot_import_template)
        file_name = os.path.join("/tmp/tender_package_import", tender_package.name)
        df = pd.read_excel(file_name, header=None)
        for _ in range(template.number_of_lots_per_time):
            rows = tender_lot_import_assemble_rows(df, template, row_number)
            if not rows:
                break
            import_tender_lot(tender_package, rows, template)
            row_number = rows[-1].Index + 1

        if (start_row_number == row_number):
            frappe.enqueue(
                "electronic_tender.controllers.tender_package.tender_lot_import_complete",
                enqueue_after_commit=True,
                tender_package=tender_package.name,
            )
        else:
            tender_package.number_of_processed_rows = row_number
            tender_package.save()
            frappe.enqueue(
                "electronic_tender.controllers.tender_package.tender_lot_import_process",
                enqueue_after_commit=True,
                tender_package=tender_package.name,
                row_number=row_number
            )
    except Exception as e:
        frappe.db.rollback()
        detailed_error = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        frappe.db.set_value("Tender Package", tender_package, {
            "import_status": "Failed",
            "why_failed": detailed_error
        })


def tender_lot_import_complete(tender_package):
    try:
        folder_name = "/tmp/tender_package_import"
        file_name = os.path.join(folder_name, tender_package)
        if os.path.exists(file_name):
            os.remove(file_name)
        tender_package_publish(tender_package)
        tender_package = frappe.get_doc("Tender Package", tender_package)
        tender_package.import_status = "Completed"
        tender_package.save()

        tender = frappe.get_doc("Tender", tender_package.tender)

        message_content = frappe.new_doc("Message Content")
        message_content.title = "投标消息"
        message_content.content = "[{0}]新增[{1}]个投标单".format(tender.tender_name, tender_package.number_of_lots)
        message_content.type = "Tender"
        message_content.save()

        frappe.enqueue(
            "electronic_erp.controllers.mobile_push_notification.send_mobile_push_notification",
            enqueue_after_commit=True,
            message_content=message_content.name
        )
    except Exception as e:
        frappe.db.rollback()
        detailed_error = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        frappe.db.set_value("Tender Package", tender_package, {
            "import_status": "Failed",
            "why_failed": detailed_error
        })

@frappe.whitelist()
def tender_package_summary(tender_package):
    tender_package = frappe.get_doc("Tender Package", tender_package)
    summary = frappe.db.sql(
        """
        SELECT
            COUNT(1) AS total_lots,
            SUM(quantity) AS total_quantity,
            GROUP_CONCAT(DISTINCT item) AS items,
            GROUP_CONCAT(DISTINCT grade) AS grades,
            GROUP_CONCAT(DISTINCT lock_condition) AS lock_conditions
        FROM `tabTender Lot`
        WHERE tender_package = %s
        """,
        (tender_package.name)
    )
    filter = {
        "items": summary[0][2],
        "grades": summary[0][3],
        "lock_conditions": summary[0][4],
    }
    tender_package.number_of_lots = summary[0][0]
    tender_package.quantity = summary[0][1]
    tender_package.filter = json.dumps(filter)
    tender_package.save()

@frappe.whitelist()
def tender_package_publish(tender_package):
    tender_package_summary(tender_package)
    tender_package = frappe.get_doc("Tender Package", tender_package)
    frappe.db.sql(
        """
        UPDATE `tabTender Lot`
        SET status = "Processing"
        WHERE tender_package = %s
        """,
        (tender_package.name)
    )
    tender_package.status = "Processing"
    tender_package.save()

def import_tender_lot(tender_package, rows, template):
    if (skip_tender_lot(rows, template)):
        return

    tender_lot = frappe.new_doc("Tender Lot")
    tender_lot.tender_package = tender_package.name
    tender_lot.index = get_tender_lot_index(rows, template)
    for row in rows:
        lot_item = get_tender_lot_item(row, template)
        tender_lot.append("lot_items", lot_item)
    tender_lot.save()

def skip_tender_lot(rows, template):
    if (template.skip_script is None):
        return False
    local_vars = {
        "rows": rows,
    }
    exec(template.skip_script, globals(), local_vars)
    return local_vars["skip"]

def get_tender_lot_index(rows, template):
    local_vars = {
        "rows": rows,
    }
    exec(template.index_script, globals(), local_vars)
    return local_vars["index"]
    

def get_tender_lot_item(row, template):
    local_vars = {
        "row": row,
        "template": template,
    }
    exec(template.item_script, globals(), local_vars)
    item_name = local_vars["item_name"]
    quantity = local_vars["quantity"]
    grade = local_vars["grade"]
    lock_condition = local_vars["lock_condition"]
    # 把item_name做分词，拿到标准的item_code
    tokenizerResult = tokenizer(item_name.split(" "))
    item_code = tokenizerResult.get("Item Code")
    if (item_code is None):
        # 如果拿不到标准的item_code，则创建一个新的非标item
        try:
            item = frappe.get_doc("Item", item_name)
        except frappe.DoesNotExistError:
            item = frappe.new_doc("Item")
            item.item_code = item_name
            item.item_group = "Non-standard"
            item.stock_uom = "Nos"
            item.has_variants = 1
            item.append("attributes", {
                "attribute": "Capacity"
            })
            item.save()
    elif (len(item_code) > 1):
        raise RuntimeError(f"get ambiguous item code[{item_code}] from: {item_name}")
    else:
        item = frappe.get_doc("Item", item_code[0].replacement)
    # 除了标准的item_code外，还有可能通过分词拿到属性值
    attributes = {}
    item_attributes = tokenizerResult.get("Item Attribute")
    if (item_attributes is not None):
        for item_attribute in item_attributes:
            attribute_name = item_attribute.item_attribute
            attributes[attribute_name] = item_attribute.replacement

    return {
        "item": item.item_code,
        "quantity": quantity,
        "grade": grade,
        "lock_condition": lock_condition,
        "attributes": json.dumps(attributes),
    }
    
    
def tender_lot_import_assemble_rows(df, template, row_number=0):
    assemble_type = template.assemble_type
    if (assemble_type == "One Lot Per Row"):
        return one_lot_per_row(df, row_number, template.header_row_mark)
    elif (assemble_type == "Split by Header Row"):
        return split_by_header_row(df, row_number, template.header_row_mark)
    elif (assemble_type == "Split by Specified Cell"):
        return group_by_cell(df, row_number, template.header_row_mark, template.index_of_group_cell)


def one_lot_per_row(df, start_row, header_row_mark):
    rows = []
    if start_row > len(df):
        return rows
    for row in df.itertuples(index=True):
        current_row = row.Index
        if current_row < start_row:
            continue
            
        first_value = row[1]
        
        if not first_value:
            break
            
        if first_value == header_row_mark:
            continue
            
        return [row]
    
    return rows


def split_by_header_row(df, start_row, header_row_mark ):
    rows = []
    for row in df.itertuples(index=True):
        current_row = row.Index
        if current_row < start_row:
            continue
            
        first_value = row[1]
        
        if not first_value:
            break
            
        if first_value == header_row_mark:
            break    
            
        rows.append(row)
    
    return rows


def group_by_cell(df, start_row, header_row_mark, cell_index):
    if cell_index >= len(df.columns):
        raise IndexError(f"Cell index [{cell_index}] out of range (max {len(df.columns)-1})")
    rows = []
    
    column_name = df.columns[cell_index]
    group_value = None
    
    for row in df.itertuples(index=True):
        current_row = row.Index
        if current_row < start_row:
            continue
            
        first_value = row[1]
        
        if not first_value:
            break
            
        if first_value == header_row_mark:
            continue
            
        cell_value = row[cell_index + 1].strip()
        
        if not cell_value:
            break
            
        if group_value is None:
            group_value = cell_value
        elif cell_value != group_value:
            break
        
        rows.append(row)
    
    return rows


def tokenizer(tokens):
    result = {}
    index = 0
    while index < len(tokens):
        current_token = tokens[index]
        # 查找以当前 token 为 firstToken 的所有 TokenGroup
        token_group_list = frappe.db.get_list("Token Group",
            filters={
                "first_token": current_token,
            },
            fields=["token_number", "original_value", "replacement", "item_attribute", "type"],
            order_by="token_number desc",
        )
        matched = False
        for token_group in token_group_list:
            token_number = token_group.token_number
            # 检查剩余tokens是否足够
            if index + token_number > len(tokens):
                continue
            
            sub_tokens = tokens[index : index + token_number]
            concatenated_tokens = ' '.join(sub_tokens)
            if concatenated_tokens.lower() == token_group.original_value.lower():
                if token_group.type not in result:
                    result[token_group.type] = []
                result[token_group.type].append(token_group)
                index += token_number
                matched = True
                break
        
        if not matched:
            index += 1
    
    return result  
