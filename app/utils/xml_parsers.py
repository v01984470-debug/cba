from typing import Dict, Optional
from lxml import etree

# Support multiple namespace versions
NS_004_VERSIONS = [
    "urn:iso:std:iso:20022:tech:xsd:pacs.004.001.12",
    "urn:iso:std:iso:20022:tech:xsd:pacs.004.001.09",
    "urn:iso:std:iso:20022:tech:xsd:pacs.004.001.08"
]

NS_008_VERSIONS = [
    "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.12",
    "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08",
    "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.09"
]


def _gettext(node: Optional[etree._Element], xpath: str, ns: Dict[str, str]) -> Optional[str]:
    if node is None:
        return None
    found = node.xpath(xpath, namespaces=ns)
    if not found:
        return None
    text = found[0].text if isinstance(
        found[0], etree._Element) else str(found[0])
    return text.strip() if text else None


def _find_working_namespace(root: etree._Element, xpath: str, namespace_versions: list) -> Optional[Dict[str, str]]:
    """Find the first working namespace version for the given xpath."""
    for ns_version in namespace_versions:
        ns = {"ns": ns_version}
        if root.xpath(xpath, namespaces=ns):
            return ns
    return None


def parse_pacs008(xml_text: str) -> Dict[str, Optional[str]]:
    root = etree.fromstring(xml_text.encode("utf-8"))

    # Find working namespace
    working_ns = _find_working_namespace(
        root, './/ns:CdtTrfTxInf', NS_008_VERSIONS)
    if not working_ns:
        return {"e2e": None, "uetr": None, "dbtr_name": None, "dbtr_iban": None, "ccy": None, "amount": None}

    tx = root.xpath('.//ns:CdtTrfTxInf', namespaces=working_ns)[0]

    ccy_el = tx.xpath('.//ns:IntrBkSttlmAmt', namespaces=working_ns)
    ccy_el = ccy_el[0] if ccy_el else None
    amt_text = ccy_el.text if ccy_el is not None else None
    amount_value = float(amt_text) if amt_text else None

    # Try UETR first, then fall back to TxId
    uetr = _gettext(tx, './/ns:PmtId/ns:UETR', working_ns)
    if not uetr:
        uetr = _gettext(tx, './/ns:PmtId/ns:TxId', working_ns)

    # Try to get IBAN from multiple possible locations
    dbtr_iban = _gettext(tx, './/ns:DbtrAcct/ns:Id/ns:IBAN', working_ns)
    if not dbtr_iban:
        dbtr_iban = _gettext(
            tx, './/ns:Dbtr/ns:Id/ns:OrgId/ns:Othr/ns:Id', working_ns)
    if not dbtr_iban:
        dbtr_iban = _gettext(tx, './/ns:Dbtr/ns:Id/ns:Othr/ns:Id', working_ns)

    return {
        "e2e": _gettext(tx, './/ns:PmtId/ns:EndToEndId', working_ns),
        "uetr": uetr,
        "dbtr_name": _gettext(tx, './/ns:Dbtr/ns:Nm', working_ns),
        "dbtr_iban": dbtr_iban,
        "ccy": ccy_el.get('Ccy') if ccy_el is not None else None,
        "amount": amount_value,
    }


def parse_pacs004(xml_text: str) -> Dict[str, Optional[str]]:
    root = etree.fromstring(xml_text.encode("utf-8"))

    # Find working namespace
    working_ns = _find_working_namespace(root, './/ns:TxInf', NS_004_VERSIONS)
    if not working_ns:
        return {
            "e2e": None, "uetr": None, "cdtr_name": None, "cdtr_iban": None,
            "rtr_ccy": None, "rtr_amount": None, "rsn": None, "rsn_info": None
        }

    tx = root.xpath('.//ns:TxInf', namespaces=working_ns)[0]

    rtr_list = tx.xpath('.//ns:RtrdIntrBkSttlmAmt', namespaces=working_ns)
    rtr_el = rtr_list[0] if rtr_list else None
    rtr_text = rtr_el.text if rtr_el is not None else None
    rtr_amount_value = float(rtr_text) if rtr_text else None

    # Try OrgnlUETR first, then fall back to OrgnlTxId
    uetr = _gettext(tx, './ns:OrgnlUETR', working_ns)
    if not uetr:
        uetr = _gettext(tx, './ns:OrgnlTxId', working_ns)

    # Try to get IBAN from multiple possible locations
    cdtr_iban = _gettext(tx, './/ns:CdtrAcct/ns:Id/ns:IBAN', working_ns)
    if not cdtr_iban:
        cdtr_iban = _gettext(
            tx, './/ns:Cdtr/ns:Id/ns:OrgId/ns:Othr/ns:Id', working_ns)
    if not cdtr_iban:
        cdtr_iban = _gettext(tx, './/ns:Cdtr/ns:Id/ns:Othr/ns:Id', working_ns)

    # Also extract debtor (customer) IBAN for cross-message validation
    dbtr_iban = _gettext(tx, './/ns:DbtrAcct/ns:Id/ns:IBAN', working_ns)
    if not dbtr_iban:
        dbtr_iban = _gettext(
            tx, './/ns:Dbtr/ns:Id/ns:OrgId/ns:Othr/ns:Id', working_ns)
    if not dbtr_iban:
        dbtr_iban = _gettext(tx, './/ns:Dbtr/ns:Id/ns:Othr/ns:Id', working_ns)

    return {
        "e2e": _gettext(tx, './ns:OrgnlEndToEndId', working_ns),
        "uetr": uetr,
        "cdtr_name": _gettext(tx, './/ns:Cdtr//ns:Nm', working_ns),
        "cdtr_iban": cdtr_iban,
        "dbtr_iban": dbtr_iban,
        "rtr_ccy": rtr_el.get('Ccy') if rtr_el is not None else None,
        "rtr_amount": rtr_amount_value,
        "rsn": _gettext(tx, './/ns:RtrRsnInf/ns:Rsn/ns:Cd', working_ns),
        "rsn_info": _gettext(tx, './/ns:RtrRsnInf/ns:AddtlInf', working_ns),
    }
