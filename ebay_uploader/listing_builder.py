"""Builds eBay Trading API XML <Item> blocks from Product objects."""
from __future__ import annotations
from .models import Product, ProductType, TireSpecs, WheelSpecs
from .fitment import fitment_to_xml, _esc

# eBay US category IDs
CATEGORY_MAP = {
    ProductType.TIRE: {
        "default": "66471",          # Passenger Car Tires
        "lt": "66472",               # Light Truck & SUV Tires
    },
    ProductType.WHEEL: "28713",      # Car & Truck Wheels
    ProductType.SUSPENSION: "33742", # Suspension Parts
    ProductType.PACKAGE: "66472",    # Grouped under tires for packages
}


def _pick_tire_category(specs: TireSpecs | None) -> str:
    if specs and specs.load_range:
        # LT tires typically have a load range (C/D/E)
        return "66472"
    return "66471"


def _item_specific(name: str, value: str) -> str:
    if not value:
        return ""
    return f"""<NameValueList><Name>{_esc(name)}</Name><Value>{_esc(str(value))}</Value></NameValueList>"""


def _tire_specifics(p: Product) -> str:
    s = p.tire_specs
    specs_xml = ""
    specs_xml += _item_specific("Brand", p.brand)
    if s:
        specs_xml += _item_specific("Tire Width", s.width)
        specs_xml += _item_specific("Aspect Ratio", s.aspect_ratio)
        specs_xml += _item_specific("Rim Diameter", s.rim_diameter)
        specs_xml += _item_specific("Tire Diameter", s.rim_diameter)
        if s.load_index:
            specs_xml += _item_specific("Load Index Rating", s.load_index)
        if s.speed_rating:
            specs_xml += _item_specific("Speed Rating", s.speed_rating)
        if s.load_range:
            specs_xml += _item_specific("Load Range", s.load_range)
        if s.utqg:
            specs_xml += _item_specific("UTQG", s.utqg)
        if s.sidewall:
            specs_xml += _item_specific("Sidewall Style", s.sidewall)
        specs_xml += _item_specific("Construction", "Radial" if s.construction == "R" else s.construction)
    if p.mpn:
        specs_xml += _item_specific("Manufacturer Part Number", p.mpn)
    if p.upc:
        specs_xml += _item_specific("UPC", p.upc)
    if p.country_of_manufacture:
        specs_xml += _item_specific("Country/Region of Manufacture", p.country_of_manufacture)
    if p.warranty:
        specs_xml += _item_specific("Warranty", p.warranty)
    return specs_xml


def _wheel_specifics(p: Product) -> str:
    s = p.wheel_specs
    specs_xml = ""
    specs_xml += _item_specific("Brand", p.brand)
    if s:
        specs_xml += _item_specific("Rim Diameter", s.diameter)
        specs_xml += _item_specific("Rim Width", s.width)
        specs_xml += _item_specific("Bolt Pattern", s.bolt_pattern)
        if s.offset:
            specs_xml += _item_specific("Offset", s.offset)
        if s.backspacing:
            specs_xml += _item_specific("Backspacing", s.backspacing)
        if s.hub_bore:
            specs_xml += _item_specific("Hub Bore Diameter", s.hub_bore)
        if s.finish:
            specs_xml += _item_specific("Finish", s.finish)
        specs_xml += _item_specific("Wheel Material", s.material)
        specs_xml += _item_specific("Wheel Construction", "Cast Aluminum")
    if p.mpn:
        specs_xml += _item_specific("Manufacturer Part Number", p.mpn)
    if p.upc:
        specs_xml += _item_specific("UPC", p.upc)
    if p.country_of_manufacture:
        specs_xml += _item_specific("Country/Region of Manufacture", p.country_of_manufacture)
    if p.warranty:
        specs_xml += _item_specific("Warranty", p.warranty)
    return specs_xml


def _suspension_specifics(p: Product) -> str:
    s = p.suspension_specs
    specs_xml = ""
    specs_xml += _item_specific("Brand", p.brand)
    if s:
        if s.part_type:
            specs_xml += _item_specific("Part Type", s.part_type)
        if s.lift_height:
            specs_xml += _item_specific("Lift Height", s.lift_height)
    if p.mpn:
        specs_xml += _item_specific("Manufacturer Part Number", p.mpn)
    if p.upc:
        specs_xml += _item_specific("UPC", p.upc)
    if p.warranty:
        specs_xml += _item_specific("Warranty", p.warranty)
    return specs_xml


def _item_specifics_xml(p: Product) -> str:
    if p.product_type == ProductType.TIRE:
        inner = _tire_specifics(p)
    elif p.product_type == ProductType.WHEEL:
        inner = _wheel_specifics(p)
    else:
        inner = _suspension_specifics(p)
    if not inner:
        return ""
    return f"<ItemSpecifics>{inner}</ItemSpecifics>"


def _picture_details(urls: list[str], max_images: int = 12) -> str:
    if not urls:
        return ""
    lines = ["<PictureDetails>"]
    for url in urls[:max_images]:
        lines.append(f"  <PictureURL>{_esc(url)}</PictureURL>")
    lines.append("</PictureDetails>")
    return "\n".join(lines)


def _description_html(p: Product) -> str:
    if p.description:
        return p.description

    # Auto-generate a basic description
    lines = [f"<h2>{_esc(p.title)}</h2>"]
    if p.product_type == ProductType.TIRE and p.tire_specs:
        s = p.tire_specs
        lines.append(f"<p><strong>Size:</strong> {_esc(s.full_size_string)}</p>")
    elif p.product_type == ProductType.WHEEL and p.wheel_specs:
        s = p.wheel_specs
        lines.append(f"<p><strong>Size:</strong> {_esc(s.size_string)} | "
                     f"<strong>Bolt Pattern:</strong> {_esc(s.bolt_pattern)}</p>")
        if s.offset:
            lines.append(f"<p><strong>Offset:</strong> {_esc(s.offset)}</p>")
        if s.finish:
            lines.append(f"<p><strong>Finish:</strong> {_esc(s.finish)}</p>")
    elif p.product_type == ProductType.SUSPENSION and p.suspension_specs:
        s = p.suspension_specs
        if s.lift_height:
            lines.append(f"<p><strong>Lift Height:</strong> {_esc(s.lift_height)}</p>")
    lines.append("<p>Brand new in original manufacturer packaging.</p>")
    if p.warranty:
        lines.append(f"<p><strong>Warranty:</strong> {_esc(p.warranty)}</p>")
    return "".join(lines)


def build_item_xml(p: Product, settings: dict) -> str:
    """Return a Trading API <Item>…</Item> XML block for a single Product."""
    ebay_cfg = settings.get("ebay", {})
    defaults = settings.get("defaults", {})
    shipping_cfg = ebay_cfg.get("shipping", {})
    return_cfg = ebay_cfg.get("return_policy", {})

    price = p.sale_price
    if price is None:
        raise ValueError(f"SKU {p.sku} has no sale_price — run pricing engine first")

    # Category
    if p.product_type == ProductType.TIRE:
        category_id = _pick_tire_category(p.tire_specs)
    elif p.product_type == ProductType.WHEEL:
        category_id = CATEGORY_MAP[ProductType.WHEEL]
    elif p.product_type == ProductType.SUSPENSION:
        category_id = CATEGORY_MAP[ProductType.SUSPENSION]
    else:
        category_id = CATEGORY_MAP[ProductType.PACKAGE]

    condition_id = defaults.get("condition_id", 1000)
    listing_type = defaults.get("listing_type", "FixedPriceItem")
    dispatch_days = ebay_cfg.get("dispatch_days", 3)
    currency = ebay_cfg.get("currency", "USD")
    country = ebay_cfg.get("country", "US")
    paypal_email = ebay_cfg.get("paypal_email", "")

    returns_accepted = "ReturnsAccepted" if return_cfg.get("returns_accepted", True) else "ReturnsNotAccepted"
    refund = return_cfg.get("refund", "MoneyBack")
    returns_within = return_cfg.get("returns_within", "Days_30")
    shipping_paid_by = return_cfg.get("shipping_paid_by", "Buyer")

    shipping_type = shipping_cfg.get("type", "Flat")
    shipping_service = shipping_cfg.get("service", "UPSGround")
    shipping_cost = shipping_cfg.get("cost", 0.00)
    shipping_additional = shipping_cfg.get("additional_cost", 0.00)

    max_images = settings.get("upload", {}).get("max_images", 12)

    description_cdata = f"<![CDATA[{_description_html(p)}]]>"
    fitment_xml = fitment_to_xml(p.fitment)

    paypal_block = ""
    if paypal_email:
        paypal_block = f"""
  <PaymentMethods>PayPal</PaymentMethods>
  <PayPalEmailAddress>{_esc(paypal_email)}</PayPalEmailAddress>"""

    return f"""<Item>
  <Title>{_esc(p.title[:80])}</Title>
  <Description>{description_cdata}</Description>
  <PrimaryCategory>
    <CategoryID>{category_id}</CategoryID>
  </PrimaryCategory>
  <StartPrice>{price:.2f}</StartPrice>
  <ConditionID>{condition_id}</ConditionID>
  <Country>{country}</Country>
  <Currency>{currency}</Currency>
  <DispatchTimeMax>{dispatch_days}</DispatchTimeMax>
  <ListingDuration>GTC</ListingDuration>
  <ListingType>{listing_type}</ListingType>
  <Quantity>{p.quantity}</Quantity>
  <SKU>{_esc(p.sku)}</SKU>
  {_picture_details(p.image_urls, max_images)}
  {_item_specifics_xml(p)}
  {fitment_xml}
  {paypal_block}
  <ReturnPolicy>
    <ReturnsAcceptedOption>{returns_accepted}</ReturnsAcceptedOption>
    <RefundOption>{refund}</RefundOption>
    <ReturnsWithinOption>{returns_within}</ReturnsWithinOption>
    <ShippingCostPaidByOption>{shipping_paid_by}</ShippingCostPaidByOption>
  </ReturnPolicy>
  <ShippingDetails>
    <ShippingType>{shipping_type}</ShippingType>
    <ShippingServiceOptions>
      <ShippingServicePriority>1</ShippingServicePriority>
      <ShippingService>{shipping_service}</ShippingService>
      <ShippingServiceCost>{shipping_cost:.2f}</ShippingServiceCost>
      <ShippingServiceAdditionalCost>{shipping_additional:.2f}</ShippingServiceAdditionalCost>
    </ShippingServiceOptions>
  </ShippingDetails>
  <Site>US</Site>
</Item>"""
