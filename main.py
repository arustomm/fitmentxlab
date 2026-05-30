#!/usr/bin/env python3
"""
eBay Bulk Uploader CLI
Usage:
    python main.py upload --csv inventory.csv --mapping config/vendors/my_vendor.yaml
    python main.py upload --csv tires.csv --mapping config/vendors/tires.yaml --dry-run
    python main.py status
    python main.py retry-failed --mapping config/vendors/my_vendor.yaml
"""
from __future__ import annotations
import sys
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.table import Table

from ebay_uploader.auth import EbayCredentials
from ebay_uploader.csv_parser import CSVParser
from ebay_uploader.uploader import BulkUploader
from ebay_uploader import tracker as db

console = Console()


def _load_settings(settings_path: str) -> dict:
    p = Path(settings_path)
    if not p.exists():
        console.print(f"[red]Settings file not found: {settings_path}[/red]")
        console.print("Copy config/settings.yaml.example to config/settings.yaml and fill it in.")
        sys.exit(1)
    with open(p) as f:
        return yaml.safe_load(f)


@click.group()
def cli():
    """eBay Bulk Upload Automation — Tires, Wheels & Suspension."""


@cli.command()
@click.option("--csv", "csv_path", required=True, type=click.Path(exists=True),
              help="Path to vendor CSV file.")
@click.option("--mapping", required=True, type=click.Path(exists=True),
              help="Vendor column-mapping YAML (see config/vendors/).")
@click.option("--settings", default="config/settings.yaml",
              help="Main settings YAML [default: config/settings.yaml].")
@click.option("--dry-run", is_flag=True, default=False,
              help="Validate via eBay VerifyAddItem but don't actually list.")
@click.option("--limit", default=0, type=int,
              help="Only process first N rows (0 = all).")
def upload(csv_path: str, mapping: str, settings: str, dry_run: bool, limit: int):
    """Parse a vendor CSV and bulk-upload listings to eBay."""
    cfg = _load_settings(settings)
    if dry_run:
        cfg.setdefault("upload", {})["dry_run"] = True

    console.print(f"[bold cyan]Parsing CSV:[/bold cyan] {csv_path}")
    parser = CSVParser(mapping)
    products = list(parser.parse_file(csv_path))

    if limit:
        products = products[:limit]

    console.print(f"  Vendor: {parser.vendor_name}")
    console.print(f"  Parsed: {len(products)} products")

    if not products:
        console.print("[yellow]No valid products found in CSV.[/yellow]")
        return

    creds = EbayCredentials()
    uploader = BulkUploader(cfg, creds)
    results = uploader.upload_products(products)

    # Print summary table
    success = [r for r in results if r.status == "success"]
    failed = [r for r in results if r.status == "failed"]
    skipped = [r for r in results if r.status == "skipped"]
    dry = [r for r in results if r.status == "dry_run"]

    console.print()
    console.print("[bold]Upload Summary[/bold]")
    console.print(f"  [green]Success:[/green]  {len(success)}")
    console.print(f"  [yellow]Skipped:[/yellow]  {len(skipped)}")
    console.print(f"  [red]Failed:[/red]   {len(failed)}")
    if dry:
        console.print(f"  [cyan]Dry run:[/cyan]  {len(dry)}")

    if failed:
        console.print()
        table = Table(title="Failed Uploads", show_lines=True)
        table.add_column("SKU", style="red")
        table.add_column("Title")
        table.add_column("Error")
        for r in failed:
            table.add_row(r.sku, r.title[:50], (r.error or "")[:80])
        console.print(table)

    if success:
        console.print()
        table = Table(title="Successfully Listed", show_lines=True)
        table.add_column("SKU")
        table.add_column("Title")
        table.add_column("Price", justify="right")
        table.add_column("Item ID")
        for r in success:
            price = f"${r.sale_price:.2f}" if r.sale_price else "-"
            table.add_row(r.sku, r.title[:45], price, r.ebay_item_id or "-")
        console.print(table)


@cli.command()
@click.option("--settings", default="config/settings.yaml")
def status(settings: str):
    """Show upload history summary from the tracking database."""
    db.init_db()
    summary = db.summary()
    if not summary:
        console.print("No uploads tracked yet.")
        return

    table = Table(title="Upload Tracker Summary")
    table.add_column("Status")
    table.add_column("Count", justify="right")
    for status_label, count in sorted(summary.items()):
        color = {"success": "green", "failed": "red", "skipped": "yellow"}.get(status_label, "white")
        table.add_row(f"[{color}]{status_label}[/{color}]", str(count))
    console.print(table)


@cli.command("retry-failed")
@click.option("--csv", "csv_path", required=True, type=click.Path(exists=True),
              help="Same vendor CSV used in the original upload.")
@click.option("--mapping", required=True, type=click.Path(exists=True))
@click.option("--settings", default="config/settings.yaml")
def retry_failed(csv_path: str, mapping: str, settings: str):
    """Re-upload only the SKUs that previously failed."""
    db.init_db()
    failed_skus = set(db.get_failed_skus())
    if not failed_skus:
        console.print("[green]No failed uploads to retry.[/green]")
        return

    console.print(f"Retrying {len(failed_skus)} failed SKUs...")
    cfg = _load_settings(settings)

    parser = CSVParser(mapping)
    products = [p for p in parser.parse_file(csv_path) if p.sku in failed_skus]

    creds = EbayCredentials()
    cfg.setdefault("upload", {})["skip_existing"] = False  # force retry
    uploader = BulkUploader(cfg, creds)
    uploader.upload_products(products)


@cli.command("get-policies")
@click.option("--settings", default="config/settings.yaml")
def get_policies(settings: str):
    """List your eBay account's business policies (fulfillment/payment/return IDs)."""
    console.print("[yellow]Note:[/yellow] Policy IDs must be retrieved from your eBay seller account.")
    console.print("Go to: My eBay → Account → Business Policies")
    console.print("Or visit: https://www.bizpolicy.ebay.com/businesspolicy/manage")
    console.print()
    console.print("Once you have the IDs, add them to config/settings.yaml:")
    console.print("  ebay:")
    console.print("    fulfillment_policy_id: 1234567890")
    console.print("    payment_policy_id: 1234567890")
    console.print("    return_policy_id: 1234567890")


if __name__ == "__main__":
    cli()
