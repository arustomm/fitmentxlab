"""Vendor CSV parser — maps arbitrary vendor columns to normalized Product objects."""
from __future__ import annotations
import re
from pathlib import Path
from typing import Iterator
import pandas as pd
import yaml

from .models import (
    Product, ProductType, TireSpecs, WheelSpecs, SuspensionSpecs, FitmentEntry
)
from .fitment import parse_fitment_text

# Tire size patterns
_TIRE_METRIC = re.compile(
    r"^(?:LT|P|ST|C)?(\d{2,3})/(\d{2,3})([RBD])(\d{1,2}(?:\.\d)?)$",
    re.IGNORECASE,
)
_TIRE_FLOTATION = re.compile(
    r"^(\d{2}(?:\.\d)?)x(\d{2}(?:\.\d)?)([RBD])(\d{1,2}(?:\.\d)?)$",
    re.IGNORECASE,
)


def _load_mapping(mapping_path: str | Path) -> dict:
    with open(mapping_path, "r") as f:
        return yaml.safe_load(f)


def _col(row: pd.Series, mapping: dict, key: str, default=None):
    """Safely fetch a value from a CSV row using the mapping config."""
    col_name = mapping.get("columns", {}).get(key, "")
    if not col_name:
        return default
    col_name_lower = col_name.strip().lower()
    # Case-insensitive column lookup
    for c in row.index:
        if c.strip().lower() == col_name_lower:
            val = row[c]
            if pd.isna(val):
                return default
            return str(val).strip() if isinstance(val, str) else val
    return default


def _parse_tire_size(size_str: str) -> TireSpecs | None:
    s = size_str.strip().upper().replace(" ", "")
    m = _TIRE_METRIC.match(s)
    if m:
        return TireSpecs(
            width=m.group(1),
            aspect_ratio=m.group(2),
            construction=m.group(3).upper(),
            rim_diameter=m.group(4),
        )
    m = _TIRE_FLOTATION.match(s)
    if m:
        return TireSpecs(
            width=m.group(2),
            aspect_ratio="",
            construction=m.group(3).upper(),
            rim_diameter=m.group(4),
        )
    return None


def _parse_float(val) -> float | None:
    if val is None:
        return None
    try:
        return float(str(val).replace("$", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def _parse_images(val: str | None) -> list[str]:
    if not val:
        return []
    return [u.strip() for u in val.split(",") if u.strip()]


class CSVParser:
    def __init__(self, mapping_path: str | Path):
        self.mapping = _load_mapping(mapping_path)
        self.product_type = ProductType(self.mapping.get("product_type", "tire"))
        self.overrides = self.mapping.get("overrides", {})
        self.vendor_name = self.mapping.get("vendor_name", "Unknown Vendor")

    def parse_file(self, csv_path: str | Path) -> Iterator[Product]:
        df = pd.read_csv(csv_path, dtype=str, keep_default_na=True)
        # Normalize column names: strip whitespace
        df.columns = [c.strip() for c in df.columns]

        for _, row in df.iterrows():
            product = self._parse_row(row)
            if product is not None:
                yield product

    def _parse_row(self, row: pd.Series) -> Product | None:
        m = self.mapping
        c = lambda key, default=None: _col(row, m, key, default)

        sku = c("sku")
        if not sku:
            return None

        title = c("title") or ""
        brand = c("brand") or ""
        cost_raw = _parse_float(c("cost"))
        if cost_raw is None:
            return None  # skip rows without a cost

        qty_raw = c("quantity", "1")
        try:
            quantity = int(float(str(qty_raw)))
        except (ValueError, TypeError):
            quantity = 1

        product = Product(
            sku=sku,
            title=title[:80],  # eBay title limit
            brand=brand,
            product_type=self.product_type,
            cost=cost_raw,
            quantity=quantity,
            msrp=_parse_float(c("msrp")),
            map_price=_parse_float(c("map_price")),
            description=c("description"),
            image_urls=_parse_images(c("images")),
            upc=c("upc"),
            mpn=c("mpn"),
            country_of_manufacture=self.overrides.get("country_of_manufacture"),
            warranty=self.overrides.get("warranty"),
        )

        # Type-specific specs
        if self.product_type == ProductType.TIRE:
            product.tire_specs = self._parse_tire_specs(row)
        elif self.product_type == ProductType.WHEEL:
            product.wheel_specs = self._parse_wheel_specs(row)
        elif self.product_type == ProductType.SUSPENSION:
            product.suspension_specs = SuspensionSpecs(
                part_type=c("part_type"),
                lift_height=c("lift_height"),
            )

        # Fitment
        product.fitment = self._parse_fitment(row)

        return product

    def _parse_tire_specs(self, row: pd.Series) -> TireSpecs | None:
        m = self.mapping
        c = lambda key, default=None: _col(row, m, key, default)

        size_combined = c("size_combined")
        if size_combined:
            specs = _parse_tire_size(size_combined)
        else:
            width = c("tire_width")
            aspect = c("tire_aspect")
            diam = c("tire_diameter")
            if not (width and aspect and diam):
                return None
            specs = TireSpecs(
                width=width,
                aspect_ratio=aspect,
                rim_diameter=diam,
            )

        if specs:
            specs.load_index = c("load_index")
            specs.speed_rating = c("speed_rating")
            specs.load_range = c("load_range")
            specs.utqg = c("utqg")
            specs.sidewall = c("sidewall")

        return specs

    def _parse_wheel_specs(self, row: pd.Series) -> WheelSpecs | None:
        m = self.mapping
        c = lambda key, default=None: _col(row, m, key, default)

        diameter = c("diameter")
        width = c("width")
        bolt_pattern = c("bolt_pattern")
        if not (diameter and width and bolt_pattern):
            return None

        # Normalize bolt pattern: "5-114.3" → "5x114.3"
        bolt_pattern = bolt_pattern.replace("-", "x", 1) if "-" in bolt_pattern else bolt_pattern

        return WheelSpecs(
            diameter=diameter,
            width=width,
            bolt_pattern=bolt_pattern,
            offset=c("offset"),
            backspacing=c("backspacing"),
            hub_bore=c("hub_bore"),
            finish=c("finish"),
            material=self.overrides.get("material", "Aluminum Alloy"),
        )

    def _parse_fitment(self, row: pd.Series) -> list[FitmentEntry]:
        m = self.mapping
        c = lambda key, default=None: _col(row, m, key, default)

        fitment_text = c("fitment_text")
        if fitment_text:
            return parse_fitment_text(fitment_text)

        year = c("fitment_year")
        make = c("fitment_make")
        model = c("fitment_model")
        if year and make and model:
            return [FitmentEntry(
                year=year,
                make=make,
                model=model,
                trim=c("fitment_trim"),
                engine=c("fitment_engine"),
            )]

        return []
