/* ============================================================
   app.js — TZ-Convert
   UI logic: tabs, converter, resolver, world clocks, autocomplete.
   Depends on: data.js, resolver.js
   ============================================================ */

(function () {
  'use strict';

  /* ── Tab switching ─────────────────────────────────────── */

  const tabBtns = document.querySelectorAll('.tab-btn');
  const panels  = document.querySelectorAll('.panel');

  function switchTab(name) {
    tabBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === name);
    });
    panels.forEach(panel => {
      const visible = panel.id === `tab-${name}`;
      panel.hidden = !visible;
      panel.classList.toggle('active', visible);
    });
    if (name === 'world') renderWorldClocks();
  }

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });

  /* ── Live UTC clock in header ──────────────────────────── */

  const clockEl = document.getElementById('live-clock');

  function tickClock() {
    const now = new Date();
    const pad = n => String(n).padStart(2, '0');
    if (clockEl) clockEl.textContent =
      `UTC  ${pad(now.getUTCHours())}:${pad(now.getUTCMinutes())}:${pad(now.getUTCSeconds())}` +
      `  ·  ` + now.toUTCString().slice(5, 16);
  }
  setInterval(tickClock, 1000);
  tickClock();

  /* ── Autocomplete (shared, accepts a search function) ──── */

  function bindAutocomplete(inputId, suggestId, searchFn) {
    const input   = document.getElementById(inputId);
    const suggest = document.getElementById(suggestId);
    if (!input || !suggest) return;

    let activeIdx = -1;

    function showSuggestions(items) {
      suggest.innerHTML = '';
      activeIdx = -1;
      if (!items.length) { suggest.hidden = true; return; }

      items.forEach(item => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.textContent = item;
        btn.addEventListener('mousedown', e => {
          e.preventDefault();
          input.value = item;
          suggest.hidden = true;
          // Auto-resolve if this is the loc-input
          if (inputId === 'loc-input') {
            setTimeout(doResolve, 0);
          }
        });
        suggest.appendChild(btn);
      });
      suggest.hidden = false;
    }

    input.addEventListener('input', () => {
      const q = input.value.trim();
      if (!q) { suggest.hidden = true; return; }
      showSuggestions(searchFn(q, 8));
    });

    input.addEventListener('keydown', e => {
      const items = suggest.querySelectorAll('button');
      if (!items.length) return;
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeIdx = (activeIdx + 1) % items.length;
        items.forEach((b, i) => b.classList.toggle('active', i === activeIdx));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeIdx = (activeIdx - 1 + items.length) % items.length;
        items.forEach((b, i) => b.classList.toggle('active', i === activeIdx));
      } else if (e.key === 'Enter' && activeIdx >= 0) {
        e.preventDefault();
        input.value = items[activeIdx].textContent;
        suggest.hidden = true;
        activeIdx = -1;
        if (inputId === 'loc-input') doResolve();
      } else if (e.key === 'Escape') {
        suggest.hidden = true;
      }
    });

    document.addEventListener('click', e => {
      if (!input.contains(e.target) && !suggest.contains(e.target)) {
        suggest.hidden = true;
      }
    });
  }

  // Converter: search IANA timezone strings
  bindAutocomplete('from-tz',  'from-suggest', TZResolver.searchTimezones);
  bindAutocomplete('to-tz',    'to-suggest',   TZResolver.searchTimezones);
  // Resolver: search location names (cities, countries, states, aliases)
  bindAutocomplete('loc-input', 'loc-suggest', TZResolver.searchLocations);

  /* ── Converter defaults ────────────────────────────────── */

  const fromTzInput = document.getElementById('from-tz');
  const toTzInput   = document.getElementById('to-tz');
  const dtInput     = document.getElementById('dt-input');
  const convResult  = document.getElementById('conv-result');

  if (fromTzInput) fromTzInput.value = 'UTC';
  if (toTzInput)   toTzInput.value   = 'Australia/Sydney';

  /* ── Converter: Use Now ────────────────────────────────── */

  document.getElementById('btn-now')?.addEventListener('click', () => {
    const now = new Date();
    const pad = n => String(n).padStart(2, '0');
    dtInput.value =
      `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ` +
      `${pad(now.getHours())}:${pad(now.getMinutes())}`;
  });

  /* ── Converter: Swap ───────────────────────────────────── */

  document.getElementById('btn-swap')?.addEventListener('click', () => {
    const tmp = fromTzInput.value;
    fromTzInput.value = toTzInput.value;
    toTzInput.value = tmp;
  });

  /* ── Converter: Convert ────────────────────────────────── */

  function setConvResult(text, state = '') {
    convResult.textContent = text;
    convResult.className = `result-box${state ? ' ' + state : ''}`;
  }

  function setConvResultHTML(html, state = '') {
    convResult.innerHTML = html;
    convResult.className = `result-box${state ? ' ' + state : ''}`;
  }

  function doConvert() {
    const fromRaw = fromTzInput.value.trim();
    const toRaw   = toTzInput.value.trim();
    const timeStr = dtInput.value.trim();

    if (!timeStr) { setConvResult('Enter a date and time first.', 'err'); return; }
    if (!fromRaw) { setConvResult('Enter a source timezone.', 'err'); return; }
    if (!toRaw)   { setConvResult('Enter a target timezone.', 'err'); return; }

    const { iana: fromTz } = TZResolver.resolveLocation(fromRaw);
    const { iana: toTz }   = TZResolver.resolveLocation(toRaw);

    if (!TZResolver.isValidIANA(fromTz)) {
      setConvResult(`Unknown timezone: "${fromRaw}"`, 'err'); return;
    }
    if (!TZResolver.isValidIANA(toTz)) {
      setConvResult(`Unknown timezone: "${toRaw}"`, 'err'); return;
    }

    if (!/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(timeStr)) {
      setConvResult('Use format YYYY-MM-DD HH:MM  e.g. 2026-06-22 14:30', 'err');
      return;
    }

    try {
      const utcDate = TZResolver.wallClockToUTC(timeStr, fromTz);
      const result  = TZResolver.formatInTZ(utcDate, toTz);
      const offset  = TZResolver.getOffsetString(toTz);
      const toNote  = toTz !== toRaw ? ` · resolved from "${toRaw}"` : '';

      setConvResultHTML(
        `<span class="result-primary">${result}</span>` +
        `<span class="result-meta">${toTz}  ·  ${offset}${toNote}</span>`,
        'ok'
      );
    } catch (err) {
      setConvResult(`Conversion failed: ${err.message}`, 'err');
    }
  }

  document.getElementById('btn-convert')?.addEventListener('click', doConvert);
  dtInput?.addEventListener('keydown', e => { if (e.key === 'Enter') doConvert(); });

  /* ── Resolver: example chips ───────────────────────────── */

  const EXAMPLES = ['Denver', 'Goodland, KS', 'PST', 'Australia', 'Auckland', 'India', 'Kansas'];
  const chipRow  = document.getElementById('example-chips');
  if (chipRow) {
    EXAMPLES.forEach(ex => {
      const btn = document.createElement('button');
      btn.className = 'chip';
      btn.textContent = ex;
      btn.addEventListener('click', () => {
        document.getElementById('loc-input').value = ex;
        doResolve();
      });
      chipRow.appendChild(btn);
    });
  }

  /* ── Resolver: resolve ─────────────────────────────────── */

  const locInput  = document.getElementById('loc-input');
  const resResult = document.getElementById('res-result');

  function setResResultHTML(html, state = '') {
    resResult.innerHTML = html;
    resResult.className = `result-box${state ? ' ' + state : ''}`;
  }

  function doResolve() {
    const loc = locInput?.value.trim();
    if (!loc) return;

    // Close the suggestion dropdown
    const locSuggest = document.getElementById('loc-suggest');
    if (locSuggest) locSuggest.hidden = true;

    const { iana, method } = TZResolver.resolveLocation(loc);

    if (!TZResolver.isValidIANA(iana)) {
      setResResultHTML(`Could not resolve "${loc}" to a valid timezone.`, 'err');
      return;
    }

    const now    = new Date();
    const time   = TZResolver.formatInTZ(now, iana, {
      hour: '2-digit', minute: '2-digit', second: '2-digit',
      weekday: 'short', day: 'numeric', month: 'short', year: 'numeric',
    });
    const offset       = TZResolver.getOffsetString(iana);
    const methodClean  = method.replace(/~/g, '→').replace(/-/g, ' ');

    setResResultHTML(
      `<span class="result-primary">${iana}</span>` +
      `<span class="result-meta">` +
        `${time}  ·  ${offset}  ·  via ${methodClean}` +
      `</span>` +
      `<button class="btn-copy" id="copy-btn">Copy IANA string</button>`,
      'ok'
    );

    document.getElementById('copy-btn')?.addEventListener('click', () => {
      const copyFn = navigator.clipboard
        ? navigator.clipboard.writeText(iana)
        : Promise.reject();

      copyFn.then(() => {
        const btn = document.getElementById('copy-btn');
        if (btn) { btn.textContent = 'Copied!'; setTimeout(() => { btn.textContent = 'Copy IANA string'; }, 1500); }
      }).catch(() => {
        // file:// fallback
        const el = document.createElement('textarea');
        el.value = iana;
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        const btn = document.getElementById('copy-btn');
        if (btn) { btn.textContent = 'Copied!'; setTimeout(() => { btn.textContent = 'Copy IANA string'; }, 1500); }
      });
    });
  }

  document.getElementById('btn-resolve')?.addEventListener('click', doResolve);
  locInput?.addEventListener('keydown', e => { if (e.key === 'Enter') doResolve(); });

  /* ── World clocks ──────────────────────────────────────── */

  const worldGrid = document.getElementById('world-grid');
  let worldCards  = [];
  let worldTicker = null;

  function renderWorldClocks() {
    if (!worldGrid) return;
    worldGrid.innerHTML = '';
    worldCards = [];

    TZC.WORLD_CLOCKS.forEach(({ label, tz }) => {
      const card = document.createElement('div');
      card.className = 'clock-card';
      card.innerHTML =
        `<div class="clock-city">${label}</div>` +
        `<div class="clock-tz">${tz}</div>` +
        `<div class="clock-time">--:--:--</div>` +
        `<div class="clock-date"></div>` +
        `<div class="clock-offset"></div>`;
      worldGrid.appendChild(card);
      worldCards.push({
        tz,
        timeEl:   card.querySelector('.clock-time'),
        dateEl:   card.querySelector('.clock-date'),
        offsetEl: card.querySelector('.clock-offset'),
      });
    });

    tickWorld();
    clearInterval(worldTicker);
    worldTicker = setInterval(tickWorld, 1000);
  }

  function tickWorld() {
    const now = new Date();
    worldCards.forEach(({ tz, timeEl, dateEl, offsetEl }) => {
      try {
        timeEl.textContent = new Intl.DateTimeFormat('en-GB', {
          timeZone: tz, hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
        }).format(now);
        dateEl.textContent = new Intl.DateTimeFormat('en-GB', {
          timeZone: tz, weekday: 'short', day: 'numeric', month: 'short', year: 'numeric',
        }).format(now);
        offsetEl.textContent = TZResolver.getOffsetString(tz);
      } catch (_e) {
        timeEl.textContent = '--:--:--';
      }
    });
  }

  if (!document.getElementById('tab-world')?.hidden) {
    renderWorldClocks();
  }

})();
