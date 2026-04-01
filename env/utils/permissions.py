ROLE_PERMISSIONS = {
    "admin": {
        "pages": {
            "dashboard",
            "properties",
            "units",
            "tenants",
            "payments",
            "reports",
            "profile",
        },
        "edit_properties": True,
        "edit_units": True,
        "edit_tenants": True,
        "edit_payments": True,
        "export_reports": True,
        "manage_profiles": True,
    },
    "manager": {
        "pages": {
            "dashboard",
            "properties",
            "units",
            "tenants",
            "payments",
            "reports",
            "profile",
        },
        "edit_properties": True,
        "edit_units": True,
        "edit_tenants": True,
        "edit_payments": True,
        "export_reports": True,
        "manage_profiles": False,
    },
    "viewer": {
        "pages": {
            "dashboard",
            "properties",
            "units",
            "tenants",
            "reports",
            "profile",
        },
        "edit_properties": False,
        "edit_units": False,
        "edit_tenants": False,
        "edit_payments": False,
        "export_reports": False,
        "manage_profiles": False,
    },
}


def normalize_role(role):
    role_name = (role or "viewer").strip().lower()
    if role_name not in ROLE_PERMISSIONS:
        return "viewer"
    return role_name


def get_permissions_for_role(role):
    return ROLE_PERMISSIONS[normalize_role(role)]


def can_access_page(role, page_key):
    permissions = get_permissions_for_role(role)
    return page_key in permissions["pages"]
