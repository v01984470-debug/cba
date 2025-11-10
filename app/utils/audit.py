from typing import Dict, Any, List
from datetime import datetime


def append_audit(state: Dict[str, Any], actor: str, action: str, details: Dict[str, Any]) -> Dict[str, Any]:
    events: List[Dict[str, Any]] = list(state.get("audit_events", []))
    events.append({
        "ts": datetime.utcnow().isoformat() + "Z",
        "actor": actor,
        "action": action,
        "details": details,
    })
    state["audit_events"] = events
    return state
