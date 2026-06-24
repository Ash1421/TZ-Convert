"""
converter.py — DST-aware time conversion using Python's built-in zoneinfo.

On Windows, zoneinfo needs the tzdata package (pip install tzdata).
This module checks for that on import and raises a clear error if missing.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# ---------------------------------------------------------------------------
# Windows tzdata guard — raises early with a helpful message
# ---------------------------------------------------------------------------
try:
    ZoneInfo("America/Denver")
except ZoneInfoNotFoundError:
    raise ImportError(
        "\n\nNo timezone database found.\n"
        "Run:  pip install tzdata\n"
        "Then restart the application.\n"
    ) from None


# ---------------------------------------------------------------------------
# Core conversion
# ---------------------------------------------------------------------------

def convert_time(dt: datetime, from_tz: str, to_tz: str) -> datetime:
    """
    Convert *dt* from *from_tz* to *to_tz* (both IANA strings).

    Naive datetimes are treated as belonging to *from_tz*.
    DST is handled automatically via zoneinfo.
    """
    try:
        src_zone = ZoneInfo(from_tz)
        dst_zone = ZoneInfo(to_tz)
    except (ZoneInfoNotFoundError, KeyError) as exc:
        raise ValueError(f"Unknown IANA timezone: {exc}") from exc

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=src_zone)
    else:
        dt = dt.astimezone(src_zone)

    return dt.astimezone(dst_zone)


def get_current_time(tz: str = "UTC") -> datetime:
    """Return the current time in *tz*."""
    try:
        return datetime.now(ZoneInfo(tz))
    except (ZoneInfoNotFoundError, KeyError) as exc:
        raise ValueError(f"Unknown IANA timezone: {exc}") from exc


def get_utc_offset_str(tz: str) -> str:
    """Return a human-readable UTC offset string, e.g. 'UTC+13:00'."""
    now = get_current_time(tz)
    offset = now.utcoffset()
    if offset is None:
        return "UTC+0:00"
    total = int(offset.total_seconds())
    sign = "+" if total >= 0 else "-"
    total = abs(total)
    h, rem = divmod(total, 3600)
    m = rem // 60
    return f"UTC{sign}{h}:{m:02d}"


def format_time(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S %Z") -> str:
    return dt.strftime(fmt)


def parse_datetime(text: str, fmt: str = "%Y-%m-%d %H:%M") -> datetime:
    """Parse *text* into a naive datetime using *fmt*."""
    return datetime.strptime(text, fmt)


# ---------------------------------------------------------------------------
# Batch / multi-zone conversion
# ---------------------------------------------------------------------------

def convert_to_many(dt: datetime, from_tz: str, to_tzs: list[str]) -> dict[str, datetime]:
    """Convert *dt* from *from_tz* to each timezone in *to_tzs*."""
    return {tz: convert_time(dt, from_tz, tz) for tz in to_tzs}


# ---------------------------------------------------------------------------
# World clock snapshot
# ---------------------------------------------------------------------------

WORLD_CLOCKS: list[dict[str, str]] = [
    {"label": "UTC",          "tz": "UTC"},
    {"label": "London",       "tz": "Europe/London"},
    {"label": "Paris",        "tz": "Europe/Paris"},
    {"label": "Moscow",       "tz": "Europe/Moscow"},
    {"label": "Dubai",        "tz": "Asia/Dubai"},
    {"label": "Karachi",      "tz": "Asia/Karachi"},
    {"label": "India",        "tz": "Asia/Kolkata"},
    {"label": "Bangkok",      "tz": "Asia/Bangkok"},
    {"label": "Singapore",    "tz": "Asia/Singapore"},
    {"label": "Tokyo",        "tz": "Asia/Tokyo"},
    {"label": "Sydney",       "tz": "Australia/Sydney"},
    {"label": "Melbourne",    "tz": "Australia/Melbourne"},
    {"label": "Auckland",     "tz": "Pacific/Auckland"},
    {"label": "Honolulu",     "tz": "Pacific/Honolulu"},
    {"label": "Los Angeles",  "tz": "America/Los_Angeles"},
    {"label": "Denver",       "tz": "America/Denver"},
    {"label": "Chicago",      "tz": "America/Chicago"},
    {"label": "New York",     "tz": "America/New_York"},
    {"label": "São Paulo",    "tz": "America/Sao_Paulo"},
    {"label": "Johannesburg", "tz": "Africa/Johannesburg"},
]


def get_world_clocks() -> list[dict[str, str]]:
    """Return current time for each city in WORLD_CLOCKS."""
    result = []
    for entry in WORLD_CLOCKS:
        try:
            now = get_current_time(entry["tz"])
            result.append({
                "label":  entry["label"],
                "tz":     entry["tz"],
                "time":   format_time(now, "%H:%M:%S"),
                "date":   format_time(now, "%a, %d %b %Y"),
                "offset": get_utc_offset_str(entry["tz"]),
            })
        except ValueError:
            pass
    return result
