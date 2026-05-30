"""eBay authentication — Trading API user token management."""
from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()


class EbayCredentials:
    """Holds Trading API credentials loaded from env or explicit kwargs."""

    SANDBOX_ENDPOINT = "https://api.sandbox.ebay.com/ws/api.dll"
    PROD_ENDPOINT = "https://api.ebay.com/ws/api.dll"

    def __init__(
        self,
        app_id: str | None = None,
        dev_id: str | None = None,
        cert_id: str | None = None,
        user_token: str | None = None,
        environment: str | None = None,
    ):
        self.app_id = app_id or os.environ["EBAY_APP_ID"]
        self.dev_id = dev_id or os.environ["EBAY_DEV_ID"]
        self.cert_id = cert_id or os.environ["EBAY_CERT_ID"]
        self.user_token = user_token or os.environ["EBAY_USER_TOKEN"]
        env = environment or os.getenv("EBAY_ENVIRONMENT", "sandbox")
        self.sandbox = env.lower() == "sandbox"

    @property
    def endpoint(self) -> str:
        return self.SANDBOX_ENDPOINT if self.sandbox else self.PROD_ENDPOINT

    def trading_headers(self, call_name: str, site_id: int = 0) -> dict:
        return {
            "X-EBAY-API-CALL-NAME": call_name,
            "X-EBAY-API-APP-NAME": self.app_id,
            "X-EBAY-API-DEV-NAME": self.dev_id,
            "X-EBAY-API-CERT-NAME": self.cert_id,
            "X-EBAY-API-SITEID": str(site_id),
            "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
            "Content-Type": "text/xml; charset=utf-8",
        }
