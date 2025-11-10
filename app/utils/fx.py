import json
import urllib.request
from typing import Optional

FRANKFURTER_URL = "https://api.frankfurter.app/latest?from={base}&to=AUD"

# Offline fallback rates to keep UI functional if live FX API is unavailable
# These are indicative rates for demo/testing and should not be used in production
STATIC_AUD_RATES = {
    "EUR": 1.7786,
    "USD": 1.5132,
    "GBP": 1.9500,
    "JPY": 0.0101,
    "CHF": 1.7000,
}


def get_aud_rate(base_ccy: str) -> Optional[float]:
    if not base_ccy:
        return None
    if base_ccy.upper() == "AUD":
        return 1.0
    url = FRANKFURTER_URL.format(base=base_ccy.upper())
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            rates = data.get("rates", {})
            rate = rates.get("AUD")
            if isinstance(rate, (int, float)):
                return float(rate)
    except Exception:
        # Network error or API not reachable: fall back to static rates
        pass
    # Fallback to static rates (demo/testing)
    return STATIC_AUD_RATES.get(base_ccy.upper())


def convert_to_aud(amount: float, base_ccy: str) -> Optional[float]:
    if amount is None:
        return None
    rate = get_aud_rate(base_ccy)
    if rate is None:
        return None
    return float(amount) * float(rate)
