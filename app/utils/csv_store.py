import csv
import re
from typing import Dict, Optional, List


def iban_valid(iban: str) -> bool:
    s = re.sub(r"\s+", "", iban or "").upper()
    if not (15 <= len(s) <= 34):
        return False
    rearr = s[4:] + s[:4]
    digits = "".join(str(int(ch, 36)) for ch in rearr)
    try:
        return int(digits) % 97 == 1
    except Exception:
        return False


def load_accounts_csv(csv_path: str) -> Dict[str, Dict[str, str]]:
    by_iban: Dict[str, Dict[str, str]] = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            iban = (row.get("iban") or "").strip()
            if not iban:
                continue
            by_iban[iban.upper()] = {k: (v.strip() if isinstance(
                v, str) else v) for k, v in row.items()}
    return by_iban


def validate_against_csv(accounts_by_iban: Dict[str, Dict[str, str]], *, iban: str,
                         holder_name: Optional[str] = None, swift: Optional[str] = None, ccy: Optional[str] = None) -> Dict:
    errors = []
    if not iban or not iban_valid(iban):
        errors.append("Invalid or missing IBAN checksum")
    record = accounts_by_iban.get((iban or "").strip().upper())
    if not record:
        return {"ok": False, "errors": ["IBAN not found in CSV"] + errors, "record": None}
    if holder_name and (record.get("account_holder_name", "").upper() != holder_name.strip().upper()):
        errors.append("Account holder name mismatch")
    if swift and record.get("swift_bic") and record["swift_bic"].upper() != swift.strip().upper():
        errors.append("SWIFT/BIC mismatch")
    if ccy and record.get("account_currency") and record["account_currency"].upper() != ccy.strip().upper():
        errors.append("Currency mismatch")
    return {"ok": len(errors) == 0, "errors": errors, "record": record}


def suggest_alternate_active(by_iban: Dict[str, Dict[str, str]], holder_name: str, *, exclude_iban: Optional[str] = None) -> Optional[str]:
    if not holder_name:
        return None
    name_u = holder_name.strip().upper()
    exclude_u = (exclude_iban or "").strip().upper()
    candidates: List[str] = []
    for rec in by_iban.values():
        if rec.get("account_holder_name", "").upper() != name_u:
            continue
        if rec.get("account_status") != "ACTIVE":
            continue
        iban = (rec.get("iban") or "").strip().upper()
        if not iban or iban == exclude_u:
            continue
        candidates.append(iban)
    return candidates[0] if candidates else None
