"""eBay Trading API XML client with retry logic."""
from __future__ import annotations
import xml.etree.ElementTree as ET
from typing import Any
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .auth import EbayCredentials

NS = "urn:ebay:apis:eBLBaseComponents"


class EbayAPIError(Exception):
    def __init__(self, message: str, errors: list[dict] | None = None):
        super().__init__(message)
        self.errors = errors or []


class TradingClient:
    def __init__(self, creds: EbayCredentials, site_id: int = 0):
        self.creds = creds
        self.site_id = site_id
        self.session = requests.Session()

    @retry(
        retry=retry_if_exception_type(requests.RequestException),
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=2, min=2, max=16),
        reraise=True,
    )
    def _call(self, call_name: str, body_xml: str) -> ET.Element:
        payload = f"""<?xml version="1.0" encoding="utf-8"?>
<{call_name}Request xmlns="{NS}">
  <RequesterCredentials>
    <eBayAuthToken>{self.creds.user_token}</eBayAuthToken>
  </RequesterCredentials>
  {body_xml}
</{call_name}Request>"""

        resp = self.session.post(
            self.creds.endpoint,
            data=payload.encode("utf-8"),
            headers=self.creds.trading_headers(call_name, self.site_id),
            timeout=60,
        )
        resp.raise_for_status()

        root = ET.fromstring(resp.content)
        self._check_ack(root, call_name)
        return root

    def _check_ack(self, root: ET.Element, call_name: str) -> None:
        ack_el = root.find(f"{{{NS}}}Ack")
        ack = ack_el.text if ack_el is not None else "Unknown"
        if ack in ("Failure", "PartialFailure"):
            errors = []
            for err in root.findall(f".//{{{NS}}}Errors"):
                code_el = err.find(f"{{{NS}}}ErrorCode")
                msg_el = err.find(f"{{{NS}}}LongMessage")
                sev_el = err.find(f"{{{NS}}}SeverityCode")
                errors.append({
                    "code": code_el.text if code_el is not None else "",
                    "message": msg_el.text if msg_el is not None else "",
                    "severity": sev_el.text if sev_el is not None else "",
                })
            raise EbayAPIError(f"{call_name} returned {ack}", errors)

    # ------------------------------------------------------------------
    # High-level helpers
    # ------------------------------------------------------------------

    def add_items(self, item_xmls: list[str]) -> list[dict[str, Any]]:
        """Submit up to 10 items in one AddItems call. Returns list of results."""
        containers = ""
        for idx, item_xml in enumerate(item_xmls, start=1):
            containers += f"""
  <AddItemRequestContainer>
    <MessageID>{idx}</MessageID>
    {item_xml}
  </AddItemRequestContainer>"""

        root = self._call("AddItems", containers)
        results: list[dict[str, Any]] = []
        for container in root.findall(f"{{{NS}}}AddItemResponseContainer"):
            msg_id_el = container.find(f"{{{NS}}}MessageID")
            item_id_el = container.find(f"{{{NS}}}ItemID")
            ack_el = container.find(f"{{{NS}}}Ack")
            errors = []
            for err in container.findall(f".//{{{NS}}}Errors"):
                code_el = err.find(f"{{{NS}}}ErrorCode")
                msg_el = err.find(f"{{{NS}}}LongMessage")
                sev_el = err.find(f"{{{NS}}}SeverityCode")
                errors.append({
                    "code": code_el.text if code_el is not None else "",
                    "message": msg_el.text if msg_el is not None else "",
                    "severity": sev_el.text if sev_el is not None else "",
                })
            results.append({
                "message_id": int(msg_id_el.text) if msg_id_el is not None else idx,
                "item_id": item_id_el.text if item_id_el is not None else None,
                "ack": ack_el.text if ack_el is not None else "Unknown",
                "errors": errors,
            })
        return results

    def get_account_policies(self) -> dict[str, list[dict]]:
        """Fetch fulfillment, payment, and return policies from seller account."""
        results: dict[str, list[dict]] = {
            "fulfillment": [],
            "payment": [],
            "return": [],
        }

        root = self._call(
            "GetBillingAgreementAttributes",
            "<CategoryID>0</CategoryID>",  # placeholder — not actually used
        )
        # Real policy fetch via GetSellerProfiles or AccountAPI is preferred;
        # this is a stub that reminds caller to fill in policy IDs in settings.yaml
        return results

    def verify_add_item(self, item_xml: str) -> list[dict]:
        """Dry-run a single item through VerifyAddItem — no listing created."""
        root = self._call("VerifyAddItem", item_xml)
        errors = []
        for err in root.findall(f".//{{{NS}}}Errors"):
            code_el = err.find(f"{{{NS}}}ErrorCode")
            msg_el = err.find(f"{{{NS}}}LongMessage")
            sev_el = err.find(f"{{{NS}}}SeverityCode")
            errors.append({
                "code": code_el.text if code_el is not None else "",
                "message": msg_el.text if msg_el is not None else "",
                "severity": sev_el.text if sev_el is not None else "",
            })
        return errors
