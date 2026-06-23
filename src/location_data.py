"""
location_data.py — IANA timezone mapping tables.

US multi-timezone states, regional edge cases, city lookups, country defaults,
and common abbreviation aliases.
"""

# ---------------------------------------------------------------------------
# US State → Primary IANA timezone
# Multi-timezone states default to the most-populated region.
# ---------------------------------------------------------------------------
US_STATE_TIMEZONES: dict[str, str] = {
    "alabama": "America/Chicago",
    "alaska": "America/Anchorage",
    "arizona": "America/Phoenix",
    "arkansas": "America/Chicago",
    "california": "America/Los_Angeles",
    "colorado": "America/Denver",
    "connecticut": "America/New_York",
    "delaware": "America/New_York",
    "florida": "America/New_York",
    "georgia": "America/New_York",
    "hawaii": "Pacific/Honolulu",
    "idaho": "America/Denver",
    "illinois": "America/Chicago",
    "indiana": "America/Indiana/Indianapolis",
    "iowa": "America/Chicago",
    "kansas": "America/Chicago",
    "kentucky": "America/Kentucky/Louisville",
    "louisiana": "America/Chicago",
    "maine": "America/New_York",
    "maryland": "America/New_York",
    "massachusetts": "America/New_York",
    "michigan": "America/Detroit",
    "minnesota": "America/Chicago",
    "mississippi": "America/Chicago",
    "missouri": "America/Chicago",
    "montana": "America/Denver",
    "nebraska": "America/Chicago",
    "nevada": "America/Los_Angeles",
    "new hampshire": "America/New_York",
    "new jersey": "America/New_York",
    "new mexico": "America/Denver",
    "new york": "America/New_York",
    "north carolina": "America/New_York",
    "north dakota": "America/Chicago",
    "ohio": "America/New_York",
    "oklahoma": "America/Chicago",
    "oregon": "America/Los_Angeles",
    "pennsylvania": "America/New_York",
    "rhode island": "America/New_York",
    "south carolina": "America/New_York",
    "south dakota": "America/Chicago",
    "tennessee": "America/Chicago",
    "texas": "America/Chicago",
    "utah": "America/Denver",
    "vermont": "America/New_York",
    "virginia": "America/New_York",
    "washington": "America/Los_Angeles",
    "washington dc": "America/New_York",
    "west virginia": "America/New_York",
    "wisconsin": "America/Chicago",
    "wyoming": "America/Denver",
    # Two-letter abbreviations
    "al": "America/Chicago",    "ak": "America/Anchorage",
    "az": "America/Phoenix",    "ar": "America/Chicago",
    "ca": "America/Los_Angeles","co": "America/Denver",
    "ct": "America/New_York",   "de": "America/New_York",
    "fl": "America/New_York",   "ga": "America/New_York",
    "hi": "Pacific/Honolulu",   "id": "America/Denver",
    "il": "America/Chicago",    "in": "America/Indiana/Indianapolis",
    "ia": "America/Chicago",    "ks": "America/Chicago",
    "ky": "America/Kentucky/Louisville", "la": "America/Chicago",
    "me": "America/New_York",   "md": "America/New_York",
    "ma": "America/New_York",   "mi": "America/Detroit",
    "mn": "America/Chicago",    "ms": "America/Chicago",
    "mo": "America/Chicago",    "mt": "America/Denver",
    "ne": "America/Chicago",    "nv": "America/Los_Angeles",
    "nh": "America/New_York",   "nj": "America/New_York",
    "nm": "America/Denver",     "ny": "America/New_York",
    "nc": "America/New_York",   "nd": "America/Chicago",
    "oh": "America/New_York",   "ok": "America/Chicago",
    "or": "America/Los_Angeles","pa": "America/New_York",
    "ri": "America/New_York",   "sc": "America/New_York",
    "sd": "America/Chicago",    "tn": "America/Chicago",
    "tx": "America/Chicago",    "ut": "America/Denver",
    "vt": "America/New_York",   "va": "America/New_York",
    "wa": "America/Los_Angeles","dc": "America/New_York",
    "wv": "America/New_York",   "wi": "America/Chicago",
    "wy": "America/Denver",
}

# ---------------------------------------------------------------------------
# Regional edge-case overrides
# ---------------------------------------------------------------------------

# Kansas western counties observe Mountain Time
WESTERN_KANSAS_CITIES: set[str] = {
    "goodland", "colby", "liberal", "garden city", "ulysses",
    "elkhart", "tribune", "lakin", "syracuse", "johnson city",
    "sublette", "hugoton", "scott city",
}

# Florida panhandle observes Central Time; the rest of the state is Eastern
FLORIDA_PANHANDLE_CITIES: set[str] = {
    "pensacola", "fort walton beach", "destin", "crestview", "niceville",
    "navarre", "gulf breeze", "mary esther", "milton", "pace",
}

# Far-west Texas observes Mountain Time
WEST_TEXAS_CITIES: set[str] = {
    "el paso", "van horn", "sierra blanca", "marfa", "alpine", "presidio",
}

# ---------------------------------------------------------------------------
# Major city → IANA timezone
# ---------------------------------------------------------------------------
CITY_TIMEZONES: dict[str, str] = {
    # United States
    "new york": "America/New_York",       "new york city": "America/New_York",
    "nyc": "America/New_York",            "los angeles": "America/Los_Angeles",
    "la": "America/Los_Angeles",          "chicago": "America/Chicago",
    "houston": "America/Chicago",         "phoenix": "America/Phoenix",
    "philadelphia": "America/New_York",   "san antonio": "America/Chicago",
    "san diego": "America/Los_Angeles",   "dallas": "America/Chicago",
    "san jose": "America/Los_Angeles",    "austin": "America/Chicago",
    "jacksonville": "America/New_York",   "fort worth": "America/Chicago",
    "columbus": "America/New_York",       "charlotte": "America/New_York",
    "indianapolis": "America/Indiana/Indianapolis",
    "san francisco": "America/Los_Angeles", "sf": "America/Los_Angeles",
    "seattle": "America/Los_Angeles",     "denver": "America/Denver",
    "washington dc": "America/New_York",  "nashville": "America/Chicago",
    "oklahoma city": "America/Chicago",   "el paso": "America/Denver",
    "boston": "America/New_York",         "portland": "America/Los_Angeles",
    "las vegas": "America/Los_Angeles",   "memphis": "America/Chicago",
    "louisville": "America/Kentucky/Louisville",
    "baltimore": "America/New_York",      "milwaukee": "America/Chicago",
    "albuquerque": "America/Denver",      "tucson": "America/Phoenix",
    "fresno": "America/Los_Angeles",      "mesa": "America/Phoenix",
    "atlanta": "America/New_York",        "miami": "America/New_York",
    "omaha": "America/Chicago",           "honolulu": "Pacific/Honolulu",
    "minneapolis": "America/Chicago",     "wichita": "America/Chicago",
    "kansas city": "America/Chicago",     "kc": "America/Chicago",
    "topeka": "America/Chicago",          "salina": "America/Chicago",
    "overland park": "America/Chicago",   "olathe": "America/Chicago",
    "goodland": "America/Denver",         "liberal": "America/Denver",
    "garden city": "America/Denver",      "colby": "America/Denver",
    "anchorage": "America/Anchorage",
    # Europe
    "london": "Europe/London",     "paris": "Europe/Paris",
    "berlin": "Europe/Berlin",     "madrid": "Europe/Madrid",
    "rome": "Europe/Rome",         "amsterdam": "Europe/Amsterdam",
    "brussels": "Europe/Brussels", "vienna": "Europe/Vienna",
    "zurich": "Europe/Zurich",     "stockholm": "Europe/Stockholm",
    "oslo": "Europe/Oslo",         "copenhagen": "Europe/Copenhagen",
    "helsinki": "Europe/Helsinki", "warsaw": "Europe/Warsaw",
    "prague": "Europe/Prague",     "budapest": "Europe/Budapest",
    "bucharest": "Europe/Bucharest", "athens": "Europe/Athens",
    "istanbul": "Europe/Istanbul", "moscow": "Europe/Moscow",
    "kyiv": "Europe/Kiev",         "kiev": "Europe/Kiev",
    "lisbon": "Europe/Lisbon",     "dublin": "Europe/Dublin",
    # Asia / Pacific
    "tokyo": "Asia/Tokyo",         "beijing": "Asia/Shanghai",
    "shanghai": "Asia/Shanghai",   "hong kong": "Asia/Hong_Kong",
    "singapore": "Asia/Singapore", "seoul": "Asia/Seoul",
    "mumbai": "Asia/Kolkata",      "delhi": "Asia/Kolkata",
    "new delhi": "Asia/Kolkata",   "bangalore": "Asia/Kolkata",
    "bengaluru": "Asia/Kolkata",   "chennai": "Asia/Kolkata",
    "bangkok": "Asia/Bangkok",     "jakarta": "Asia/Jakarta",
    "kuala lumpur": "Asia/Kuala_Lumpur", "manila": "Asia/Manila",
    "taipei": "Asia/Taipei",       "dubai": "Asia/Dubai",
    "riyadh": "Asia/Riyadh",       "tehran": "Asia/Tehran",
    "karachi": "Asia/Karachi",     "islamabad": "Asia/Karachi",
    "lahore": "Asia/Karachi",      "dhaka": "Asia/Dhaka",
    "colombo": "Asia/Colombo",     "kathmandu": "Asia/Kathmandu",
    "kabul": "Asia/Kabul",
    # Oceania
    "sydney": "Australia/Sydney",     "melbourne": "Australia/Melbourne",
    "brisbane": "Australia/Brisbane", "perth": "Australia/Perth",
    "adelaide": "Australia/Adelaide", "darwin": "Australia/Darwin",
    "canberra": "Australia/Sydney",
    "auckland": "Pacific/Auckland",   "wellington": "Pacific/Auckland",
    "christchurch": "Pacific/Auckland", "suva": "Pacific/Fiji",
    # South America
    "sao paulo": "America/Sao_Paulo",  "são paulo": "America/Sao_Paulo",
    "rio de janeiro": "America/Sao_Paulo", "rio": "America/Sao_Paulo",
    "buenos aires": "America/Argentina/Buenos_Aires",
    "bogota": "America/Bogota",  "lima": "America/Lima",
    "santiago": "America/Santiago", "caracas": "America/Caracas",
    # Canada
    "toronto": "America/Toronto",    "vancouver": "America/Vancouver",
    "montreal": "America/Toronto",   "calgary": "America/Edmonton",
    "edmonton": "America/Edmonton",  "ottawa": "America/Toronto",
    "winnipeg": "America/Winnipeg",  "halifax": "America/Halifax",
    # Africa
    "cairo": "Africa/Cairo",
    "johannesburg": "Africa/Johannesburg", "nairobi": "Africa/Nairobi",
    "lagos": "Africa/Lagos",              "accra": "Africa/Accra",
    "addis ababa": "Africa/Addis_Ababa", "casablanca": "Africa/Casablanca",
}

# ---------------------------------------------------------------------------
# Country → Primary IANA timezone
# ---------------------------------------------------------------------------
COUNTRY_TIMEZONES: dict[str, str] = {
    "united states": "America/New_York", "usa": "America/New_York",
    "us": "America/New_York",            "canada": "America/Toronto",
    "mexico": "America/Mexico_City",     "brazil": "America/Sao_Paulo",
    "argentina": "America/Argentina/Buenos_Aires",
    "chile": "America/Santiago",         "colombia": "America/Bogota",
    "peru": "America/Lima",              "venezuela": "America/Caracas",
    "united kingdom": "Europe/London",   "uk": "Europe/London",
    "great britain": "Europe/London",    "england": "Europe/London",
    "ireland": "Europe/Dublin",          "france": "Europe/Paris",
    "germany": "Europe/Berlin",          "spain": "Europe/Madrid",
    "italy": "Europe/Rome",              "netherlands": "Europe/Amsterdam",
    "belgium": "Europe/Brussels",        "switzerland": "Europe/Zurich",
    "austria": "Europe/Vienna",          "sweden": "Europe/Stockholm",
    "norway": "Europe/Oslo",             "denmark": "Europe/Copenhagen",
    "finland": "Europe/Helsinki",        "poland": "Europe/Warsaw",
    "czech republic": "Europe/Prague",   "czechia": "Europe/Prague",
    "hungary": "Europe/Budapest",        "romania": "Europe/Bucharest",
    "greece": "Europe/Athens",           "turkey": "Europe/Istanbul",
    "russia": "Europe/Moscow",           "ukraine": "Europe/Kiev",
    "portugal": "Europe/Lisbon",         "iceland": "Atlantic/Reykjavik",
    "japan": "Asia/Tokyo",               "china": "Asia/Shanghai",
    "south korea": "Asia/Seoul",         "korea": "Asia/Seoul",
    "india": "Asia/Kolkata",             "indonesia": "Asia/Jakarta",
    "thailand": "Asia/Bangkok",          "vietnam": "Asia/Ho_Chi_Minh",
    "philippines": "Asia/Manila",        "malaysia": "Asia/Kuala_Lumpur",
    "singapore": "Asia/Singapore",       "taiwan": "Asia/Taipei",
    "hong kong": "Asia/Hong_Kong",       "pakistan": "Asia/Karachi",
    "bangladesh": "Asia/Dhaka",          "sri lanka": "Asia/Colombo",
    "nepal": "Asia/Kathmandu",           "myanmar": "Asia/Rangoon",
    "iran": "Asia/Tehran",               "iraq": "Asia/Baghdad",
    "saudi arabia": "Asia/Riyadh",       "uae": "Asia/Dubai",
    "united arab emirates": "Asia/Dubai","israel": "Asia/Jerusalem",
    "jordan": "Asia/Amman",              "lebanon": "Asia/Beirut",
    "uzbekistan": "Asia/Tashkent",       "kazakhstan": "Asia/Almaty",
    "afghanistan": "Asia/Kabul",
    "australia": "Australia/Sydney",     "new zealand": "Pacific/Auckland",
    "nz": "Pacific/Auckland",            "fiji": "Pacific/Fiji",
    "egypt": "Africa/Cairo",             "south africa": "Africa/Johannesburg",
    "kenya": "Africa/Nairobi",           "nigeria": "Africa/Lagos",
    "ghana": "Africa/Accra",             "ethiopia": "Africa/Addis_Ababa",
    "morocco": "Africa/Casablanca",      "algeria": "Africa/Algiers",
    "tanzania": "Africa/Dar_es_Salaam",
}

# ---------------------------------------------------------------------------
# Timezone abbreviation aliases → IANA
# Store only as display helpers; never persist abbreviations.
# ---------------------------------------------------------------------------
TZ_ALIASES: dict[str, str] = {
    "EST": "America/New_York",    "EDT": "America/New_York",
    "CST": "America/Chicago",     "CDT": "America/Chicago",
    "MST": "America/Denver",      "MDT": "America/Denver",
    "PST": "America/Los_Angeles", "PDT": "America/Los_Angeles",
    "GMT": "Etc/GMT",             "UTC": "UTC",
    "BST": "Europe/London",       "CET": "Europe/Paris",
    "CEST": "Europe/Paris",       "EET": "Europe/Helsinki",
    "IST": "Asia/Kolkata",        "JST": "Asia/Tokyo",
    "KST": "Asia/Seoul",          "AEST": "Australia/Sydney",
    "AEDT": "Australia/Sydney",   "AWST": "Australia/Perth",
    "ACST": "Australia/Darwin",   "NZST": "Pacific/Auckland",
    "NZDT": "Pacific/Auckland",   "AKST": "America/Anchorage",
    "HST": "Pacific/Honolulu",    "AST": "America/Halifax",
    "HKT": "Asia/Hong_Kong",      "SGT": "Asia/Singapore",
    "PKT": "Asia/Karachi",        "ICT": "Asia/Bangkok",
    "WIB": "Asia/Jakarta",        "EAT": "Africa/Nairobi",
    "BRT": "America/Sao_Paulo",   "ART": "America/Argentina/Buenos_Aires",
    "COT": "America/Bogota",      "PET": "America/Lima",
}
