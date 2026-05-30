"""Pricing engine — applies tiered markup, MAP enforcement, and rounding."""
from __future__ import annotations
import math
from .models import Product


def _apply_rounding(price: float, mode: str) -> float:
    if mode == "x.99":
        return math.floor(price) + 0.99 if price % 1 != 0.99 else price
    if mode == "x.95":
        return math.floor(price) + 0.95 if price % 1 != 0.95 else price
    return round(price, 2)


class PricingEngine:
    def __init__(self, pricing_config: dict):
        self.tiers = pricing_config.get("tiers", [{"markup_pct": 0.35}])
        self.rounding = pricing_config.get("rounding", "x.99")
        self.enforce_map = pricing_config.get("enforce_map", True)
        self.min_margin = pricing_config.get("min_margin_dollars", 5.0)

    def _markup_for_cost(self, cost: float) -> float:
        for tier in self.tiers:
            max_cost = tier.get("max_cost")
            if max_cost is None or cost <= max_cost:
                return float(tier["markup_pct"])
        # Fallback — last tier's markup
        return float(self.tiers[-1]["markup_pct"])

    def price(self, product: Product) -> float:
        """Calculate and set sale_price on the product. Returns the price."""
        cost = product.cost
        markup = self._markup_for_cost(cost)

        # margin-on-cost formula: price = cost / (1 - markup)
        # This gives markup as % of selling price, not cost
        raw_price = cost / (1.0 - markup)

        # Ensure minimum dollar margin
        if raw_price - cost < self.min_margin:
            raw_price = cost + self.min_margin

        # Apply rounding
        sale_price = _apply_rounding(raw_price, self.rounding)

        # MAP enforcement — never go below vendor MAP
        if self.enforce_map and product.map_price:
            sale_price = max(sale_price, product.map_price)

        product.sale_price = sale_price
        return sale_price

    def price_all(self, products: list[Product]) -> None:
        for p in products:
            self.price(p)
