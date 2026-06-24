"""
resolver.py — IANA timezone resolution engine.

Resolution priority:
  1. Timezone alias/abbreviation  (PST → America/Los_Angeles)
  2. Direct IANA string           (America/Denver)
  3. City-based lookup            (Denver → America/Denver)
  4. City, State/Country pattern  (Goodland, KS → America/Denver)
  5. US state lookup              (Kansas → America/Chicago)
  6. Country lookup               (Australia → Australia/Sydney)
  7. Fuzzy city match             (Syney → Australia/Sydney)
  8. Fuzzy state match
  9. Fuzzy country match
 10. System timezone fallback
"""

from __future__ import annotations

import difflib
import logging
import re
from functools import lru_cache
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from location_data import (
    CITY_TIMEZONES,
    COUNTRY_TIMEZONES,
    FLORIDA_PANHANDLE_CITIES,
    TZ_ALIASES,
    US_STATE_TIMEZONES,
    WEST_TEXAS_CITIES,
    WESTERN_KANSAS_CITIES,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Valid IANA timezone set
# ---------------------------------------------------------------------------

def _build_tz_set() -> frozenset[str]:
    """
    Build the set of valid IANA timezone strings.

    Falls back to a curated list if available_timezones() returns empty
    (can happen on Windows before tzdata is installed, though requirements.txt
    should prevent that).
    """
    try:
        from zoneinfo import available_timezones
        tzs = available_timezones()
        if tzs:
            return frozenset(tzs)
    except Exception:
        pass

    # Minimal fallback — tzdata should always be installed per requirements.txt
    return frozenset([
        "UTC", "Etc/GMT",
        "America/New_York", "America/Chicago", "America/Denver",
        "America/Los_Angeles", "America/Phoenix", "America/Anchorage",
        "America/Honolulu", "Pacific/Honolulu",
        "America/Indiana/Indianapolis", "America/Kentucky/Louisville",
        "America/Detroit", "America/Winnipeg", "America/Edmonton",
        "America/Vancouver", "America/Toronto", "America/Halifax",
        "America/St_Johns", "America/Sao_Paulo", "America/Argentina/Buenos_Aires",
        "America/Santiago", "America/Bogota", "America/Lima", "America/Caracas",
        "America/Guayaquil", "America/La_Paz", "America/Mexico_City",
        "America/Asuncion", "America/Montevideo", "America/Havana",
        "America/Costa_Rica", "America/Guatemala", "America/Panama",
        "Europe/London", "Europe/Dublin", "Europe/Lisbon", "Europe/Paris",
        "Europe/Berlin", "Europe/Madrid", "Europe/Rome", "Europe/Amsterdam",
        "Europe/Brussels", "Europe/Zurich", "Europe/Vienna", "Europe/Warsaw",
        "Europe/Prague", "Europe/Budapest", "Europe/Bucharest", "Europe/Athens",
        "Europe/Istanbul", "Europe/Moscow", "Europe/Kiev", "Europe/Stockholm",
        "Europe/Oslo", "Europe/Copenhagen", "Europe/Helsinki", "Europe/Riga",
        "Europe/Tallinn", "Europe/Vilnius", "Europe/Belgrade", "Europe/Zagreb",
        "Europe/Sofia", "Europe/Bratislava", "Europe/Ljubljana",
        "Atlantic/Reykjavik",
        "Asia/Tokyo", "Asia/Seoul", "Asia/Shanghai", "Asia/Hong_Kong",
        "Asia/Singapore", "Asia/Taipei", "Asia/Bangkok", "Asia/Jakarta",
        "Asia/Kuala_Lumpur", "Asia/Manila", "Asia/Kolkata", "Asia/Dhaka",
        "Asia/Karachi", "Asia/Colombo", "Asia/Kathmandu", "Asia/Kabul",
        "Asia/Dubai", "Asia/Riyadh", "Asia/Baghdad", "Asia/Tehran",
        "Asia/Jerusalem", "Asia/Amman", "Asia/Beirut", "Asia/Damascus",
        "Asia/Tashkent", "Asia/Almaty", "Asia/Baku", "Asia/Tbilisi",
        "Asia/Yerevan", "Asia/Rangoon", "Asia/Phnom_Penh", "Asia/Vientiane",
        "Asia/Ho_Chi_Minh", "Asia/Ulaanbaatar", "Asia/Jayapura",
        "Asia/Makassar",
        "Australia/Sydney", "Australia/Melbourne", "Australia/Brisbane",
        "Australia/Perth", "Australia/Adelaide", "Australia/Darwin",
        "Pacific/Auckland", "Pacific/Fiji", "Pacific/Honolulu",
        "Pacific/Port_Moresby", "Pacific/Guam",
        "Africa/Cairo", "Africa/Johannesburg", "Africa/Nairobi",
        "Africa/Lagos", "Africa/Accra", "Africa/Addis_Ababa",
        "Africa/Casablanca", "Africa/Tunis", "Africa/Algiers",
        "Africa/Khartoum", "Africa/Dar_es_Salaam", "Africa/Kampala",
        "Africa/Harare", "Africa/Douala", "Africa/Abidjan", "Africa/Dakar",
    ])


_VALID_TIMEZONES: frozenset[str] = _build_tz_set()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _validate(tz: str) -> str | None:
    """Return *tz* if it is a valid IANA timezone, else None."""
    try:
        ZoneInfo(tz)
        return tz
    except (ZoneInfoNotFoundError, KeyError):
        return None


# ---------------------------------------------------------------------------
# Fuzzy matchers (LRU-cached for repeated lookups)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=512)
def _fuzzy_city(q: str) -> str | None:
    m = difflib.get_close_matches(q, CITY_TIMEZONES.keys(), n=1, cutoff=0.70)
    return m[0] if m else None


@lru_cache(maxsize=256)
def _fuzzy_state(q: str) -> str | None:
    m = difflib.get_close_matches(q, US_STATE_TIMEZONES.keys(), n=1, cutoff=0.75)
    return m[0] if m else None


@lru_cache(maxsize=256)
def _fuzzy_country(q: str) -> str | None:
    m = difflib.get_close_matches(q, COUNTRY_TIMEZONES.keys(), n=1, cutoff=0.75)
    return m[0] if m else None


# ---------------------------------------------------------------------------
# Regional edge-case handlers
# ---------------------------------------------------------------------------

def _resolve_kansas(city: str) -> str:
    return "America/Denver" if city in WESTERN_KANSAS_CITIES else "America/Chicago"


def _resolve_florida(city: str) -> str:
    return "America/Chicago" if city in FLORIDA_PANHANDLE_CITIES else "America/New_York"


def _resolve_texas(city: str) -> str:
    return "America/Denver" if city in WEST_TEXAS_CITIES else "America/Chicago"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1024)
def resolve_location(location: str) -> tuple[str, str]:
    """
    Resolve a freeform location string to an IANA timezone.

    Returns (iana_timezone, method) where *method* describes how the result
    was obtained.

    Examples
    --------
    >>> resolve_location("Denver")
    ('America/Denver', 'city')
    >>> resolve_location("Goodland, KS")
    ('America/Denver', 'city-regional')
    >>> resolve_location("Australia")
    ('Australia/Sydney', 'country')
    >>> resolve_location("PST")
    ('America/Los_Angeles', 'alias')
    """
    if not location or not location.strip():
        return get_system_timezone(), "system"

    q = _norm(location)

    # 1. Timezone alias
    if q.upper() in TZ_ALIASES:
        return TZ_ALIASES[q.upper()], "alias"

    # 2. Direct IANA string
    if "/" in q or q == "utc":
        candidate = location.strip()
        if _validate(candidate):
            return candidate, "iana"
        titled = "/".join(p.title() for p in candidate.split("/"))
        if _validate(titled):
            return titled, "iana"

    # 3. City direct lookup
    if q in CITY_TIMEZONES:
        tz = CITY_TIMEZONES[q]
        if q in WESTERN_KANSAS_CITIES:
            tz = _resolve_kansas(q)
        if q in FLORIDA_PANHANDLE_CITIES:
            tz = _resolve_florida(q)
        if q in WEST_TEXAS_CITIES:
            tz = _resolve_texas(q)
        return tz, "city"

    # 4. "City, Region" pattern
    if "," in q:
        city_part, region_part = [p.strip() for p in q.split(",", 1)]
        if city_part in CITY_TIMEZONES:
            if region_part in ("kansas", "ks"):
                return _resolve_kansas(city_part), "city-regional"
            if region_part in ("florida", "fl"):
                return _resolve_florida(city_part), "city-regional"
            if region_part in ("texas", "tx"):
                return _resolve_texas(city_part), "city-regional"
            return CITY_TIMEZONES[city_part], "city"
        if region_part in US_STATE_TIMEZONES:
            return US_STATE_TIMEZONES[region_part], "state"
        if region_part in COUNTRY_TIMEZONES:
            return COUNTRY_TIMEZONES[region_part], "country"

    # 5. US state
    if q in US_STATE_TIMEZONES:
        return US_STATE_TIMEZONES[q], "state"

    # 6. Country
    if q in COUNTRY_TIMEZONES:
        return COUNTRY_TIMEZONES[q], "country"

    # 7–9. Fuzzy matches
    fc = _fuzzy_city(q)
    if fc:
        return CITY_TIMEZONES[fc], f"city~{fc}"

    fs = _fuzzy_state(q)
    if fs:
        return US_STATE_TIMEZONES[fs], f"state~{fs}"

    fco = _fuzzy_country(q)
    if fco:
        return COUNTRY_TIMEZONES[fco], f"country~{fco}"

    # 10. Fallback
    logger.warning("Could not resolve %r; falling back to system timezone.", location)
    return get_system_timezone(), "system-fallback"


def get_system_timezone() -> str:
    """Return the local system IANA timezone string."""
    import datetime as _dt
    name = str(_dt.datetime.now(_dt.timezone.utc).astimezone().tzinfo)
    return name if _validate(name) else "UTC"


def search_timezones(query: str, limit: int = 20) -> list[str]:
    """Substring + fuzzy search across all known IANA timezone strings."""
    q = query.strip().lower()
    all_tzs = sorted(_VALID_TIMEZONES)
    exact = [tz for tz in all_tzs if q in tz.lower()]
    if len(exact) >= limit:
        return exact[:limit]
    fuzzy = difflib.get_close_matches(query, all_tzs, n=limit, cutoff=0.4)
    return list(dict.fromkeys(exact + fuzzy))[:limit]


def list_timezones(prefix: str = "") -> list[str]:
    """Return sorted IANA timezone strings, optionally filtered by prefix."""
    tzs = sorted(_VALID_TIMEZONES)
    return [tz for tz in tzs if tz.startswith(prefix)] if prefix else tzs
