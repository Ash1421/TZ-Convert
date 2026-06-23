/* ============================================================
   resolver.js — TZ-Convert
   Location → IANA resolution and DST-aware time conversion.
   Depends on: data.js (TZC global)
   ============================================================ */

const TZResolver = (() => {
  'use strict';

  /* ── Helpers ───────────────────────────────────────────── */

  function norm(s) {
    return s.trim().toLowerCase().replace(/\s+/g, ' ');
  }

  /** Test whether the browser supports a given IANA timezone. */
  function isValidIANA(tz) {
    try {
      Intl.DateTimeFormat(undefined, { timeZone: tz });
      return true;
    } catch (_) {
      return false;
    }
  }

  /** Simple Levenshtein distance for fuzzy matching. */
  function levenshtein(a, b) {
    const m = a.length, n = b.length;
    const dp = Array.from({ length: m + 1 }, (_, i) => [i]);
    for (let j = 1; j <= n; j++) dp[0][j] = j;
    for (let i = 1; i <= m; i++) {
      for (let j = 1; j <= n; j++) {
        dp[i][j] = a[i - 1] === b[j - 1]
          ? dp[i - 1][j - 1]
          : 1 + Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]);
      }
    }
    return dp[m][n];
  }

  /** Find the best fuzzy match in a list (returns key or null). */
  function fuzzyMatch(query, keys, threshold = 0.70) {
    if (!query) return null;
    let best = null, bestScore = 0;
    for (const key of keys) {
      const maxLen = Math.max(query.length, key.length);
      if (maxLen === 0) continue;
      const dist = levenshtein(query, key);
      const score = 1 - dist / maxLen;
      if (score > bestScore && score >= threshold) {
        bestScore = score;
        best = key;
      }
    }
    return best;
  }

  /* ── Regional edge-case resolvers ─────────────────────── */

  function resolveKansasCity(city) {
    return TZC.WESTERN_KANSAS.has(city) ? 'America/Denver' : 'America/Chicago';
  }

  function resolveFloridaCity(city) {
    return TZC.FLORIDA_PANHANDLE.has(city) ? 'America/Chicago' : 'America/New_York';
  }

  function resolveTexasCity(city) {
    return TZC.WEST_TEXAS.has(city) ? 'America/Denver' : 'America/Chicago';
  }

  /* ── Main resolver ─────────────────────────────────────── */

  /**
   * Resolve a freeform location string to an IANA timezone.
   * Returns: { iana: string, method: string }
   */
  function resolveLocation(location) {
    if (!location || !location.trim()) {
      return { iana: getSystemTimezone(), method: 'system' };
    }

    const q = norm(location);
    const qUp = q.toUpperCase();

    // 1. Timezone alias (PST, NZST, etc.)
    if (TZC.TZ_ALIASES[qUp]) {
      return { iana: TZC.TZ_ALIASES[qUp], method: 'alias' };
    }

    // 2. Direct IANA string (contains '/' or is 'utc')
    if (q === 'utc' || q.includes('/') || q.startsWith('etc/')) {
      // Try original case first, then various capitalizations
      const candidates = [
        location.trim(),
        location.trim().split('/').map(p =>
          p.charAt(0).toUpperCase() + p.slice(1)
        ).join('/'),
      ];
      for (const c of candidates) {
        if (isValidIANA(c)) return { iana: c, method: 'iana' };
      }
    }

    // 3. City direct lookup
    if (TZC.CITY_TIMEZONES[q]) {
      let tz = TZC.CITY_TIMEZONES[q];
      // Regional overrides
      if (TZC.WESTERN_KANSAS.has(q))  tz = 'America/Denver';
      if (TZC.FLORIDA_PANHANDLE.has(q)) tz = 'America/Chicago';
      if (TZC.WEST_TEXAS.has(q))       tz = 'America/Denver';
      return { iana: tz, method: 'city' };
    }

    // 4. "City, State" or "City, Country" pattern
    if (q.includes(',')) {
      const [cityPart, regionPart] = q.split(',', 2).map(s => s.trim());

      if (TZC.CITY_TIMEZONES[cityPart]) {
        if (regionPart === 'kansas' || regionPart === 'ks') {
          return { iana: resolveKansasCity(cityPart), method: 'city-regional' };
        }
        if (regionPart === 'florida' || regionPart === 'fl') {
          return { iana: resolveFloridaCity(cityPart), method: 'city-regional' };
        }
        if (regionPart === 'texas' || regionPart === 'tx') {
          return { iana: resolveTexasCity(cityPart), method: 'city-regional' };
        }
        return { iana: TZC.CITY_TIMEZONES[cityPart], method: 'city' };
      }

      const stateTZ = TZC.US_STATE_TIMEZONES[regionPart];
      if (stateTZ) return { iana: stateTZ, method: 'state' };

      const countryTZ = TZC.COUNTRY_TIMEZONES[regionPart];
      if (countryTZ) return { iana: countryTZ, method: 'country' };
    }

    // 5. US state direct lookup
    if (TZC.US_STATE_TIMEZONES[q]) {
      return { iana: TZC.US_STATE_TIMEZONES[q], method: 'state' };
    }

    // 6. Country direct lookup
    if (TZC.COUNTRY_TIMEZONES[q]) {
      return { iana: TZC.COUNTRY_TIMEZONES[q], method: 'country' };
    }

    // 7. Fuzzy city
    const fCity = fuzzyMatch(q, Object.keys(TZC.CITY_TIMEZONES));
    if (fCity) {
      return { iana: TZC.CITY_TIMEZONES[fCity], method: `city ~ ${fCity}` };
    }

    // 8. Fuzzy state
    const fState = fuzzyMatch(q, Object.keys(TZC.US_STATE_TIMEZONES), 0.75);
    if (fState) {
      return { iana: TZC.US_STATE_TIMEZONES[fState], method: `state ~ ${fState}` };
    }

    // 9. Fuzzy country
    const fCountry = fuzzyMatch(q, Object.keys(TZC.COUNTRY_TIMEZONES), 0.75);
    if (fCountry) {
      return { iana: TZC.COUNTRY_TIMEZONES[fCountry], method: `country ~ ${fCountry}` };
    }

    // 10. System fallback
    return { iana: getSystemTimezone(), method: 'system-fallback' };
  }

  /* ── Timezone search (for autocomplete) ───────────────── */

  let _cachedIANA = null;
  function allIANA() {
    if (!_cachedIANA) {
      _cachedIANA = Intl.supportedValuesOf('timeZone');
    }
    return _cachedIANA;
  }

  function searchTimezones(query, limit = 10) {
    if (!query) return [];
    const q = query.toLowerCase();
    const all = allIANA();
    // Exact substring matches first
    const exact = all.filter(tz => tz.toLowerCase().includes(q));
    if (exact.length >= limit) return exact.slice(0, limit);
    // Add alias matches
    const aliases = Object.keys(TZC.TZ_ALIASES).filter(a =>
      a.toLowerCase().includes(q)
    );
    return [...new Set([...exact, ...aliases])].slice(0, limit);
  }

  /* ── Time conversion helpers ───────────────────────────── */

  /**
   * Get the UTC offset in minutes for a timezone at a given UTC Date.
   * Positive = ahead of UTC (e.g. Auckland = +720 in standard time).
   */
  function getUTCOffsetMinutes(tz, utcDate) {
    // Format the date in both UTC and the target tz,
    // parse both as Date objects, compare.
    const fmt = new Intl.DateTimeFormat('en-CA', {
      timeZone: tz,
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit',
      hour12: false,
    });
    const parts = fmt.formatToParts(utcDate);
    const p = {};
    parts.forEach(({ type, value }) => { p[type] = value; });
    const localStr = `${p.year}-${p.month}-${p.day}T${p.hour}:${p.minute}:${p.second}Z`;
    const localAsUTC = new Date(localStr);
    return (localAsUTC.getTime() - utcDate.getTime()) / 60000;
  }

  /**
   * Convert a "wall clock" datetime string in fromTz to a UTC Date.
   * Two-iteration approach handles DST transitions correctly.
   */
  function wallClockToUTC(dateStr, fromTz) {
    // Treat the string as if it were UTC initially
    const nominal = new Date(dateStr.replace(' ', 'T') + ':00Z');
    // Iteration 1
    const off1 = getUTCOffsetMinutes(fromTz, nominal);
    const guess = new Date(nominal.getTime() - off1 * 60000);
    // Iteration 2 (handles DST boundary)
    const off2 = getUTCOffsetMinutes(fromTz, guess);
    return new Date(nominal.getTime() - off2 * 60000);
  }

  /**
   * Format a UTC Date in a given IANA timezone.
   */
  function formatInTZ(utcDate, tz, opts = {}) {
    const defaults = {
      timeZone: tz,
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    };
    return new Intl.DateTimeFormat('en-GB', { ...defaults, ...opts }).format(utcDate);
  }

  /**
   * Get UTC offset string for a timezone right now. e.g. "UTC+12:00"
   */
  function getOffsetString(tz) {
    const now = new Date();
    const mins = getUTCOffsetMinutes(tz, now);
    const sign = mins >= 0 ? '+' : '-';
    const abs = Math.abs(mins);
    const h = Math.floor(abs / 60);
    const m = abs % 60;
    return `UTC${sign}${h}:${m.toString().padStart(2, '0')}`;
  }

  /* ── System timezone ───────────────────────────────────── */
  function getSystemTimezone() {
    try {
      return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
    } catch (_) {
      return 'UTC';
    }
  }

  /* ── Location name search (for resolver autocomplete) ─── */

  function titleCase(str) {
    return str.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  }

  function searchLocations(query, limit = 10) {
    if (!query) return [];
    const q = query.toLowerCase();
    const results = [];
    const seen = new Set();

    const add = (display) => {
      if (!seen.has(display) && results.length < limit) {
        results.push(display);
        seen.add(display);
      }
    };

    // Aliases first (PST, NZST…) — uppercase
    Object.keys(TZC.TZ_ALIASES).forEach(k => {
      if (k.toLowerCase().startsWith(q)) add(k);
    });

    // Cities — starts-with priority
    Object.keys(TZC.CITY_TIMEZONES).forEach(k => {
      if (k.startsWith(q)) add(titleCase(k));
    });

    // Countries
    Object.keys(TZC.COUNTRY_TIMEZONES).forEach(k => {
      if (k.startsWith(q)) add(titleCase(k));
    });

    // US States (full names only)
    Object.keys(TZC.US_STATE_TIMEZONES).forEach(k => {
      if (k.length > 2 && k.startsWith(q)) add(titleCase(k));
    });

    // Fill remaining slots with contains matches
    if (results.length < limit) {
      Object.keys(TZC.CITY_TIMEZONES).forEach(k => {
        if (k.includes(q) && !k.startsWith(q)) add(titleCase(k));
      });
      Object.keys(TZC.COUNTRY_TIMEZONES).forEach(k => {
        if (k.includes(q) && !k.startsWith(q)) add(titleCase(k));
      });
    }

    return results.slice(0, limit);
  }

  /* ── Public API ────────────────────────────────────────── */
  return {
    resolveLocation,
    searchTimezones,
    searchLocations,
    wallClockToUTC,
    formatInTZ,
    getOffsetString,
    getSystemTimezone,
    isValidIANA,
    getUTCOffsetMinutes,
  };
})();
