from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class ProductType(str, Enum):
    TIRE = "tire"
    WHEEL = "wheel"
    SUSPENSION = "suspension"
    PACKAGE = "package"


@dataclass
class TireSpecs:
    width: str
    aspect_ratio: str
    rim_diameter: str
    construction: str = "R"
    load_index: Optional[str] = None
    speed_rating: Optional[str] = None
    load_range: Optional[str] = None
    utqg: Optional[str] = None
    sidewall: Optional[str] = None

    @property
    def size_string(self) -> str:
        return f"{self.width}/{self.aspect_ratio}{self.construction}{self.rim_diameter}"

    @property
    def full_size_string(self) -> str:
        s = self.size_string
        if self.load_index and self.speed_rating:
            s += f" {self.load_index}{self.speed_rating}"
        if self.load_range:
            s += f" {self.load_range}"
        return s


@dataclass
class WheelSpecs:
    diameter: str
    width: str
    bolt_pattern: str
    offset: Optional[str] = None
    backspacing: Optional[str] = None
    hub_bore: Optional[str] = None
    finish: Optional[str] = None
    material: str = "Aluminum Alloy"

    @property
    def size_string(self) -> str:
        return f"{self.diameter}x{self.width}"


@dataclass
class SuspensionSpecs:
    part_type: Optional[str] = None
    lift_height: Optional[str] = None


@dataclass
class FitmentEntry:
    year: str
    make: str
    model: str
    trim: Optional[str] = None
    engine: Optional[str] = None

    @property
    def notes(self) -> str:
        parts = [self.year, self.make, self.model]
        if self.trim:
            parts.append(self.trim)
        return " ".join(parts)


@dataclass
class Product:
    sku: str
    title: str
    brand: str
    product_type: ProductType
    cost: float
    quantity: int = 0
    msrp: Optional[float] = None
    map_price: Optional[float] = None
    description: Optional[str] = None
    image_urls: List[str] = field(default_factory=list)
    upc: Optional[str] = None
    mpn: Optional[str] = None
    country_of_manufacture: Optional[str] = None
    warranty: Optional[str] = None

    tire_specs: Optional[TireSpecs] = None
    wheel_specs: Optional[WheelSpecs] = None
    suspension_specs: Optional[SuspensionSpecs] = None

    fitment: List[FitmentEntry] = field(default_factory=list)

    # Set by the pricing engine before upload
    sale_price: Optional[float] = None

    # Raw passthrough from vendor CSV for custom fields
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UploadResult:
    sku: str
    title: str
    status: str               # "success" | "failed" | "skipped" | "dry_run"
    ebay_item_id: Optional[str] = None
    ebay_url: Optional[str] = None
    sale_price: Optional[float] = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
