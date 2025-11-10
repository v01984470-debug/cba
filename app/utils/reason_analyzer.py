from typing import Dict

REASON_MAP = {
    "AC04": {"label": "Account Closed", "next": "alternate_account", "auto_refund": True},
    "AC01": {"label": "Incorrect Account Number", "next": "alternate_account", "auto_refund": True},
    "MS03": {"label": "Reason Not Specified", "next": "manual_review", "auto_refund": False},
    # Extended mappings to align with formal flow categories
    "FCA": {"label": "CBA FCA Account", "next": "cba_fca_account", "auto_refund": True},
    "CHRG": {"label": "Charges Applied - No Return", "next": "charges_no_return", "auto_refund": False},
    "VALU": {"label": "Value Date Issue", "next": "value_date_issue", "auto_refund": True},
    "POLY": {"label": "Internal Policy", "next": "internal_policy", "auto_refund": False},
    "CORR": {"label": "Correspondent Issue", "next": "correspondent_issue", "auto_refund": True},
    "CURR": {"label": "Wrong Currency", "next": "manual_review", "auto_refund": False},
}


def analyze_return_reason(code: str, addtl: str | None = None) -> Dict:
    info = REASON_MAP.get(
        code or "", {"label": "Unknown", "next": "manual_review", "auto_refund": False})
    return {
        "code": code,
        "label": info["label"],
        "action": info["next"],
        "auto_refund_eligible": info.get("auto_refund", False),
        "details": addtl
    }
