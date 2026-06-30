import frappe
import json
from frappe import _

def create_justdial_lead_source():
    if not frappe.db.exists("Lead Source","Justdial"):
        doc = frappe.get_doc({
            "doctype": "Lead Source",
            "source_name": "Justdial"
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print("Lead Source Added For Justdial")
    else:
        print("Justdial Lead Source Already Available")

@frappe.whitelist()
def capture_lead(**kwargs):
    """
    API endpoint to capture lead data from external source.
    Handles both regular form data and JSON payloads.
    If phone exists, updates the lead, otherwise creates a new one.
    """
    try:
        if frappe.request and frappe.request.data:
            try:
                data = json.loads(frappe.request.data)
            except Exception:
                data = frappe.form_dict
        else:
            data = frappe.form_dict
 
        mobile = data.get("mobile", "")
        phone = data.get("phone", "")
 
        existing_lead = None
 
        if mobile:
            existing_lead = frappe.db.get_value("Lead", {"mobile_no": mobile}, "name")
 
        if not existing_lead and phone:
            existing_lead = frappe.db.get_value("Lead", {"phone": phone}, "name")
 
        if existing_lead:
            lead = frappe.get_doc("Lead", existing_lead)
        else:
            lead = frappe.new_doc("Lead")
 
        lead.lead_name = data.get("name", "")
        lead.company_name = data.get("company", "")
        lead.mobile_no = mobile
        lead.phone = phone
        lead.email_id = data.get("email", "")
        lead.source = "Justdial"
        lead.type_of_lead = data.get("leadtype", "")
        lead.category = data.get("category", "")
        lead.date = data.get("date", "")
        lead.time = data.get("time", "")
        lead.leadid = data.get("leadid", "")
        lead.parentid = data.get("parentid", "")
 
        city_name = data.get("city", "")
 
        if city_name:
            lead.city = city_name
            city_doc = frappe.db.get_value("City", {"title": city_name}, "state")
            if city_doc:
                lead.state = city_doc
 
        if lead.source == "Justdial":
            lead_meta = frappe.get_meta("Lead")
            has_custom_lead_type = lead_meta.has_field("custom_justdial_lead_type")
 
            if has_custom_lead_type:
                if lead.category and "services" in lead.category.lower():
                    lead.custom_justdial_lead_type = "Prototype"
                else:
                    lead.custom_justdial_lead_type = "Sales"
 
        if existing_lead:
            lead.save(ignore_permissions=True)
        else:
            lead.insert(ignore_permissions=True)
 
        frappe.db.commit()

        address_data = {
            "city": data.get("city", ""),
            "area": data.get("area", ""),
            "branch_area": data.get("brancharea", ""),
            "pincode": data.get("branchpin", ""),
        }
 
        if any(address_data.values()):
            try:
                create_or_update_address(lead.name, address_data, lead.lead_name)
                frappe.db.commit()
            except Exception:
                frappe.log_error(
                    title="Justdial Address Save Error",
                    message=frappe.get_traceback(),
                )
 
        return "RECEIVED"
 
    except Exception:
        frappe.log_error(title="Justdial Lead Capture Error", message=frappe.get_traceback())
        return "ERROR"
 
 
def create_or_update_address(lead_name, address_data, lead_title):
    existing_address = frappe.db.sql(
        """SELECT parent FROM `tabDynamic Link`
           WHERE link_doctype = 'Lead' AND link_name = %s AND parenttype = 'Address'""",
        lead_name,
    )

    if existing_address:
        address = frappe.get_doc("Address", existing_address[0][0])
    else:
        address = frappe.new_doc("Address")

    address.address_title = f"{lead_title}" if lead_title else f"Lead {lead_name}"
    address.city = address_data.get("city", "")
    address.pincode = address_data.get("pincode", "")
    address.address_line1 = address_data.get("area", "")
    address.address_line2 = address_data.get("branch_area", "")
    address.address_type = "Other"

    # Populate state to satisfy sites where it's mandatory on Address
    if address.city:
        state = frappe.db.get_value("City", {"title": address.city}, "state")
        if state:
            address.state = state

    if not existing_address:
        address.append("links", {
            "link_doctype": "Lead",
            "link_name": lead_name,
            "link_title": lead_title,
        })

    if existing_address:
        address.save(ignore_permissions=True)
    else:
        address.insert(ignore_permissions=True)