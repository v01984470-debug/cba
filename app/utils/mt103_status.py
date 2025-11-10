from typing import Dict

# Placeholder. In real integration, query SWIFT or internal datastore.


def get_mt103_status(uetr: str) -> Dict:
    # Simulate: if uetr endswith certain char, mark as sent
    if not uetr:
        return {"available": False}
    status = "SENT" if uetr[-1] in "02468" else "NULL_AND_VOID"
    return {"available": True, "status": status}
