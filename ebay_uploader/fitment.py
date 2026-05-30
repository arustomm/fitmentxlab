"""Fitment / vehicle compatibility parsing and formatting."""
from __future__ import annotations
import re
from .models import FitmentEntry


# Matches things like "2019-2023 Ford F-150 XLT"
_RANGE_PATTERN = re.compile(
    r"(\d{4})\s*[-–]\s*(\d{4})\s+([A-Za-z]+)\s+(.+?)(?:\s+(.+))?$"
)
# Matches "2020 Ford F-150" or "2020 Ford F-150 XLT"
_SINGLE_PATTERN = re.compile(
    r"(\d{4})\s+([A-Za-z]+)\s+(.+?)(?:\s+(.+))?$"
)


def parse_fitment_text(text: str) -> list[FitmentEntry]:
    """
    Parse a free-text fitment string into FitmentEntry objects.

    Supports:
        "2019-2023 Ford F-150"
        "2020 Ford F-150 XLT"
        "2018-2022 RAM 1500; 2019-2023 Chevy Silverado 1500"
    """
    entries: list[FitmentEntry] = []
    # Split on semicolons or newlines for multiple vehicles
    segments = re.split(r"[;\n]+", text)
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue

        m = _RANGE_PATTERN.match(seg)
        if m:
            start_year = int(m.group(1))
            end_year = int(m.group(2))
            make = m.group(3)
            model = m.group(4).strip()
            trim = m.group(5)
            for year in range(start_year, end_year + 1):
                entries.append(FitmentEntry(
                    year=str(year),
                    make=make,
                    model=model,
                    trim=trim,
                ))
            continue

        m = _SINGLE_PATTERN.match(seg)
        if m:
            entries.append(FitmentEntry(
                year=m.group(1),
                make=m.group(2),
                model=m.group(3).strip(),
                trim=m.group(4),
            ))

    return entries


def fitment_to_xml(entries: list[FitmentEntry]) -> str:
    """Render a list of FitmentEntry objects into eBay ItemCompatibilityList XML."""
    if not entries:
        return ""

    # eBay caps compatibility list at 3000 entries
    entries = entries[:3000]

    lines = ["<ItemCompatibilityList>"]
    for entry in entries:
        lines.append("  <Compatibility>")
        lines.append(f"    <CompatibilityNotes>{_esc(entry.notes)}</CompatibilityNotes>")
        lines.append(f"    <NameValueList><Name>Year</Name><Value>{_esc(entry.year)}</Value></NameValueList>")
        lines.append(f"    <NameValueList><Name>Make</Name><Value>{_esc(entry.make)}</Value></NameValueList>")
        lines.append(f"    <NameValueList><Name>Model</Name><Value>{_esc(entry.model)}</Value></NameValueList>")
        if entry.trim:
            lines.append(f"    <NameValueList><Name>Trim</Name><Value>{_esc(entry.trim)}</Value></NameValueList>")
        if entry.engine:
            lines.append(f"    <NameValueList><Name>Engine</Name><Value>{_esc(entry.engine)}</Value></NameValueList>")
        lines.append("  </Compatibility>")
    lines.append("</ItemCompatibilityList>")
    return "\n".join(lines)


def _esc(s: str | None) -> str:
    if not s:
        return ""
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))
