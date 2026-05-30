"""Main upload orchestration pipeline."""
from __future__ import annotations
from pathlib import Path
from typing import Iterator
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn

from .models import Product, UploadResult
from .auth import EbayCredentials
from .trading_client import TradingClient, EbayAPIError
from .pricing import PricingEngine
from .listing_builder import build_item_xml
from . import tracker as db

console = Console()

_EBAY_ITEM_URL = "https://www.ebay.com/itm/{}"
_EBAY_SANDBOX_URL = "https://sandbox.ebay.com/itm/{}"


def _chunk(lst: list, size: int) -> Iterator[list]:
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


class BulkUploader:
    def __init__(self, settings: dict, creds: EbayCredentials | None = None):
        self.settings = settings
        self.creds = creds or EbayCredentials()
        self.client = TradingClient(
            self.creds,
            site_id=settings.get("ebay", {}).get("site_id", 0),
        )
        self.pricing = PricingEngine(settings.get("pricing", {}))
        self.upload_cfg = settings.get("upload", {})
        self.dry_run: bool = self.upload_cfg.get("dry_run", False)
        self.skip_existing: bool = self.upload_cfg.get("skip_existing", True)
        self.batch_size: int = min(self.upload_cfg.get("batch_size", 10), 10)
        db.init_db()

    def upload_products(self, products: list[Product]) -> list[UploadResult]:
        # Price everything first
        self.pricing.price_all(products)

        # Filter already-live SKUs if skip_existing
        to_upload = []
        skipped = []
        for p in products:
            if self.skip_existing and db.is_already_live(p.sku):
                skipped.append(UploadResult(
                    sku=p.sku, title=p.title, status="skipped",
                    sale_price=p.sale_price,
                ))
            else:
                to_upload.append(p)

        results: list[UploadResult] = list(skipped)

        if not to_upload:
            console.print("[yellow]All products already live — nothing to upload.[/yellow]")
            return results

        console.print(
            f"[bold]Uploading {len(to_upload)} products[/bold] "
            f"({'dry run' if self.dry_run else 'LIVE'}) | "
            f"{len(skipped)} skipped (already live)"
        )

        batches = list(_chunk(to_upload, self.batch_size))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Uploading...", total=len(to_upload))

            for batch in batches:
                batch_results = self._upload_batch(batch)
                results.extend(batch_results)
                for r in batch_results:
                    db.save_result(r)
                progress.advance(task, len(batch))

        return results

    def _upload_batch(self, batch: list[Product]) -> list[UploadResult]:
        item_xmls: list[str] = []
        failed_results: list[UploadResult] = []

        for p in batch:
            try:
                xml = build_item_xml(p, self.settings)
                item_xmls.append(xml)
            except Exception as exc:
                failed_results.append(UploadResult(
                    sku=p.sku, title=p.title, status="failed",
                    error=str(exc), sale_price=p.sale_price,
                ))
                item_xmls.append("")  # placeholder to keep indices aligned

        if self.dry_run:
            return self._dry_run_batch(batch, item_xmls) + failed_results

        valid_indices = [i for i, x in enumerate(item_xmls) if x]
        valid_items = [batch[i] for i in valid_indices]
        valid_xmls = [item_xmls[i] for i in valid_indices]

        if not valid_xmls:
            return failed_results

        try:
            api_results = self.client.add_items(valid_xmls)
        except EbayAPIError as exc:
            # Whole batch failed
            return [
                UploadResult(
                    sku=p.sku, title=p.title, status="failed",
                    error=str(exc), sale_price=p.sale_price,
                )
                for p in valid_items
            ] + failed_results
        except Exception as exc:
            return [
                UploadResult(
                    sku=p.sku, title=p.title, status="failed",
                    error=f"Unexpected error: {exc}", sale_price=p.sale_price,
                )
                for p in valid_items
            ] + failed_results

        results: list[UploadResult] = []
        for api_res, product in zip(api_results, valid_items):
            item_id = api_res.get("item_id")
            ack = api_res.get("ack", "Failure")
            errors = api_res.get("errors", [])
            warnings = [e["message"] for e in errors if e.get("severity") == "Warning"]
            hard_errors = [e["message"] for e in errors if e.get("severity") != "Warning"]

            if ack in ("Success", "Warning") and item_id:
                url_tmpl = _EBAY_SANDBOX_URL if self.creds.sandbox else _EBAY_ITEM_URL
                results.append(UploadResult(
                    sku=product.sku,
                    title=product.title,
                    status="success",
                    ebay_item_id=item_id,
                    ebay_url=url_tmpl.format(item_id),
                    sale_price=product.sale_price,
                    warnings=warnings,
                ))
            else:
                results.append(UploadResult(
                    sku=product.sku,
                    title=product.title,
                    status="failed",
                    error="; ".join(hard_errors) or "Unknown eBay error",
                    sale_price=product.sale_price,
                    warnings=warnings,
                ))

        return results + failed_results

    def _dry_run_batch(
        self, batch: list[Product], item_xmls: list[str]
    ) -> list[UploadResult]:
        results: list[UploadResult] = []
        for p, xml in zip(batch, item_xmls):
            if not xml:
                continue
            try:
                errors = self.client.verify_add_item(xml)
                hard = [e["message"] for e in errors if e.get("severity") != "Warning"]
                warnings = [e["message"] for e in errors if e.get("severity") == "Warning"]
                results.append(UploadResult(
                    sku=p.sku, title=p.title,
                    status="dry_run",
                    sale_price=p.sale_price,
                    error="; ".join(hard) if hard else None,
                    warnings=warnings,
                ))
            except Exception as exc:
                results.append(UploadResult(
                    sku=p.sku, title=p.title, status="failed",
                    error=str(exc), sale_price=p.sale_price,
                ))
        return results
