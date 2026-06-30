import frappe


CUSTOM_FIELDS = [
    {
        "dt": "Lead",
        "fieldname": "justdial_section",
        "fieldtype": "Section Break",
        "insert_after": "company_name",
        "label": "Justdial Lead Details",
        "name": "Lead-justdial_section",
        "collapsible": 1,
    },
    {
        "dt": "Lead",
        "fieldname": "leadid",
        "fieldtype": "Data",
        "insert_after": "justdial_section",
        "label": "Justdial Lead ID",
        "name": "Lead-leadid",
        "unique": 1,
        "read_only": 1,
        "no_copy": 1,
    },
    {
        "dt": "Lead",
        "fieldname": "type_of_lead",
        "fieldtype": "Data",
        "insert_after": "leadid",
        "label": "Lead Type",
        "name": "Lead-type_of_lead",
        "read_only": 1,
    },
    {
        "dt": "Lead",
        "fieldname": "category",
        "fieldtype": "Data",
        "insert_after": "type_of_lead",
        "label": "Justdial Category",
        "name": "Lead-category",
        "read_only": 1,
    },
    {
        "dt": "Lead",
        "fieldname": "justdial_column_break",
        "fieldtype": "Column Break",
        "insert_after": "category",
        "name": "Lead-justdial_column_break",
    },
    {
        "dt": "Lead",
        "fieldname": "date",
        "fieldtype": "Date",
        "insert_after": "justdial_column_break",
        "label": "Lead Date",
        "name": "Lead-date",
        "also_satisfied_by": ["custom_date"],
        "read_only": 1,
    },
    {
        "dt": "Lead",
        "fieldname": "time",
        "fieldtype": "Time",
        "insert_after": "date",
        "label": "Lead Time",
        "name": "Lead-time",
        "also_satisfied_by": ["custom_time"],
        "read_only": 1,
    },
    {
        "dt": "Lead",
        "fieldname": "parentid",
        "fieldtype": "Data",
        "insert_after": "time",
        "label": "Parent/Contract ID",
        "name": "Lead-parentid",
        "no_copy": 1,
        "read_only": 1,
    },
    {
        "dt": "Lead",
        "fieldname": "dncmobile",
        "fieldtype": "Check",
        "insert_after": "parentid",
        "label": "Mobile in DND",
        "name": "Lead-dncmobile",
        "read_only": 1,
    },
    {
        "dt": "Lead",
        "fieldname": "dncphone",
        "fieldtype": "Check",
        "insert_after": "dncmobile",
        "label": "Phone in DND",
        "name": "Lead-dncphone",
        "read_only": 1,
    },
    {
        "dt": "Lead",
        "fieldname": "justdial_section_end",
        "fieldtype": "Section Break",
        "insert_after": "dncphone",
        "name": "Lead-justdial_section_end",
    },
]


def after_install():
    add_custom_fields_to_lead()


def before_uninstall():
    remove_custom_fields_from_lead()


def add_custom_fields_to_lead():
    meta = frappe.get_meta("Lead")

    for field in CUSTOM_FIELDS:
        field = dict(field)
        alternate_names = field.pop("also_satisfied_by", [])

        if meta.has_field(field["fieldname"]):
            continue

        if any(meta.has_field(alt) for alt in alternate_names):
            continue

        frappe.get_doc({"doctype": "Custom Field", **field}).insert()

    frappe.db.commit()


def remove_custom_fields_from_lead():
    for field in CUSTOM_FIELDS:
        if frappe.db.exists("Custom Field", field["name"]):
            frappe.delete_doc("Custom Field", field["name"], ignore_permissions=True)

    frappe.db.commit()