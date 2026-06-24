/* ============================================================
   app.js — TZ-Convert
   Theme toggle, tabs, converter, resolver, world clocks,
   all-timezones browser.
   ============================================================ */

(function () {
  'use strict';

  /* ── Theme ─────────────────────────────────────────────── */

  const html = document.documentElement;

  function applyTheme(theme) {
    html.setAttribute('data-theme', theme);
    localStorage.setItem('tzc-theme', theme);
  }

  document.getElementById('theme-toggle')?.addEventListener('click', () => {
    const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    applyTheme(next);
  });

  /* ── Toast ─────────────────────────────────────────────── */

  const toastEl = document.getElementById('toast');
  let toastTimer;

  function showToast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove('show'), 2000);
  }

  /* ── Tabs ──────────────────────────────────────────────── */

  const tabBtns = document.querySelectorAll('.tab-btn');
  const panels  = document.querySelectorAll('.panel');
  let zonesBuilt = false;

  function switchTab(name) {
    tabBtns.forEach(b => b.classList.toggle('active', b.dataset.tab === name));
    panels.forEach(p => {
      const on = p.id === `tab-${name}`;
      p.hidden = !on;
      p.classList.toggle('active', on);
    });
    if (name === 'world')  renderWorldClocks();
    if (name === 'zones' && !zonesBuilt) buildZonesTab();
  }

  tabBtns.forEach(b => b.addEventListener('click', () => switchTab(b.dataset.tab)));

  /* ── Live UTC clock ────────────────────────────────────── */

  const clockEl = document.getElementById('live-clock');
  function tickClock() {
    const now = new Date(), p = n => String(n).padStart(2, '0');
    if (clockEl) clockEl.textContent =
      `UTC  ${p(now.getUTCHours())}:${p(now.getUTCMinutes())}:${p(now.getUTCSeconds())}  ·  ${now.toUTCString().slice(5,16)}`;
  }
  setInterval(tickClock, 1000);
  tickClock();

  /* ── Autocomplete (shared) ─────────────────────────────── */

  function bindAutocomplete(inputId, suggestId, searchFn, onSelect) {
    const input   = document.getElementById(inputId);
    const suggest = document.getElementById(suggestId);
    if (!input || !suggest) return;
    let idx = -1;

    function show(items) {
      suggest.innerHTML = '';
      idx = -1;
      if (!items.length) { suggest.hidden = true; return; }
      items.forEach(item => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.textContent = item;
        btn.addEventListener('mousedown', e => {
          e.preventDefault();
          input.value = item;
          suggest.hidden = true;
          if (onSelect) onSelect(item);
        });
        suggest.appendChild(btn);
      });
      suggest.hidden = false;
    }

    input.addEventListener('input', () => {
      const q = input.value.trim();
      q ? show(searchFn(q, 8)) : (suggest.hidden = true);
    });

    input.addEventListener('keydown', e => {
      const btns = [...suggest.querySelectorAll('button')];
      if (!btns.length) return;
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        idx = (idx + 1) % btns.length;
        btns.forEach((b, i) => b.classList.toggle('active', i === idx));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        idx = (idx - 1 + btns.length) % btns.length;
        btns.forEach((b, i) => b.classList.toggle('active', i === idx));
      } else if (e.key === 'Enter' && idx >= 0) {
        e.preventDefault();
        input.value = btns[idx].textContent;
        suggest.hidden = true;
        idx = -1;
        if (onSelect) onSelect(input.value);
      } else if (e.key === 'Escape') {
        suggest.hidden = true;
      }
    });

    document.addEventListener('click', e => {
      if (!input.contains(e.target) && !suggest.contains(e.target))
        suggest.hidden = true;
    });
  }

  bindAutocomplete('from-tz',  'from-suggest', TZResolver.searchTimezones);
  bindAutocomplete('to-tz',    'to-suggest',   TZResolver.searchTimezones);
  bindAutocomplete('loc-input','loc-suggest',  TZResolver.searchLocations, () => doResolve());

  /* ── Converter ─────────────────────────────────────────── */

  const fromTzInput = document.getElementById('from-tz');
  const toTzInput   = document.getElementById('to-tz');
  const dtInput     = document.getElementById('dt-input');
  const convResult  = document.getElementById('conv-result');

  if (fromTzInput) fromTzInput.value = 'UTC';
  if (toTzInput)   toTzInput.value   = 'Australia/Sydney';

  document.getElementById('btn-now')?.addEventListener('click', () => {
    const now = new Date(), p = n => String(n).padStart(2,'0');
    dtInput.value = `${now.getFullYear()}-${p(now.getMonth()+1)}-${p(now.getDate())} ${p(now.getHours())}:${p(now.getMinutes())}`;
  });

  document.getElementById('btn-swap')?.addEventListener('click', () => {
    [fromTzInput.value, toTzInput.value] = [toTzInput.value, fromTzInput.value];
  });

  function setConv(html_, state = '') {
    convResult.innerHTML = html_;
    convResult.className = `result-box${state ? ' '+state : ''}`;
  }

  function doConvert() {
    const fromRaw = fromTzInput.value.trim();
    const toRaw   = toTzInput.value.trim();
    const timeStr = dtInput.value.trim();

    if (!timeStr) { setConv('Enter a date and time first.', 'err'); return; }
    if (!fromRaw) { setConv('Enter a source timezone.', 'err'); return; }
    if (!toRaw)   { setConv('Enter a target timezone.', 'err'); return; }
    if (!/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(timeStr)) {
      setConv('Use format YYYY-MM-DD HH:MM  e.g. 2026-06-22 14:30', 'err'); return;
    }

    const { iana: fromTz } = TZResolver.resolveLocation(fromRaw);
    const { iana: toTz }   = TZResolver.resolveLocation(toRaw);

    if (!TZResolver.isValidIANA(fromTz)) { setConv(`Unknown timezone: "${fromRaw}"`, 'err'); return; }
    if (!TZResolver.isValidIANA(toTz))   { setConv(`Unknown timezone: "${toRaw}"`, 'err'); return; }

    try {
      const utc    = TZResolver.wallClockToUTC(timeStr, fromTz);
      const result = TZResolver.formatInTZ(utc, toTz);
      const offset = TZResolver.getOffsetString(toTz);
      const note   = toTz !== toRaw ? `  ·  resolved from "${toRaw}"` : '';
      setConv(
        `<span class="result-primary">${result}</span>` +
        `<span class="result-meta">${toTz}  ·  ${offset}${note}</span>`,
        'ok'
      );
    } catch (err) {
      setConv(`Conversion failed: ${err.message}`, 'err');
    }
  }

  document.getElementById('btn-convert')?.addEventListener('click', doConvert);
  dtInput?.addEventListener('keydown', e => { if (e.key === 'Enter') doConvert(); });

  /* ── Resolver ──────────────────────────────────────────── */

  const locInput  = document.getElementById('loc-input');
  const resResult = document.getElementById('res-result');

  const EXAMPLES = ['Denver','Goodland, KS','PST','Australia','Auckland','India','Kansas'];
  const chipRow  = document.getElementById('example-chips');
  if (chipRow) EXAMPLES.forEach(ex => {
    const b = document.createElement('button');
    b.className = 'chip'; b.textContent = ex;
    b.addEventListener('click', () => { locInput.value = ex; doResolve(); });
    chipRow.appendChild(b);
  });

  function doResolve() {
    const loc = locInput?.value.trim();
    if (!loc) return;
    document.getElementById('loc-suggest').hidden = true;

    const { iana, method } = TZResolver.resolveLocation(loc);
    if (!TZResolver.isValidIANA(iana)) {
      resResult.innerHTML = `Could not resolve "${loc}".`;
      resResult.className = 'result-box err'; return;
    }

    const now    = new Date();
    const time   = TZResolver.formatInTZ(now, iana, {
      hour:'2-digit', minute:'2-digit', second:'2-digit',
      weekday:'short', day:'numeric', month:'short', year:'numeric',
    });
    const offset = TZResolver.getOffsetString(iana);
    const mClean = method.replace(/~/g,'→').replace(/-/g,' ');

    resResult.innerHTML =
      `<span class="result-primary">${iana}</span>` +
      `<span class="result-meta">${time}  ·  ${offset}  ·  via ${mClean}</span>` +
      `<button class="btn-copy" id="copy-btn">Copy IANA string</button>`;
    resResult.className = 'result-box ok';

    document.getElementById('copy-btn')?.addEventListener('click', () => {
      (navigator.clipboard
        ? navigator.clipboard.writeText(iana)
        : Promise.reject()
      ).catch(() => {
        const el = document.createElement('textarea');
        el.value = iana; document.body.appendChild(el);
        el.select(); document.execCommand('copy');
        document.body.removeChild(el);
      }).finally ? null : null;
      showToast(`Copied: ${iana}`);
    });
  }

  document.getElementById('btn-resolve')?.addEventListener('click', doResolve);
  locInput?.addEventListener('keydown', e => { if (e.key === 'Enter') doResolve(); });

  /* ── World clocks ──────────────────────────────────────── */

  const worldGrid = document.getElementById('world-grid');
  let worldCards  = [];
  let worldTicker = null;

  function renderWorldClocks() {
    if (!worldGrid || worldCards.length) return; // only build once
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
        timeEl.textContent = new Intl.DateTimeFormat('en-GB',{
          timeZone:tz, hour:'2-digit', minute:'2-digit', second:'2-digit', hour12:false
        }).format(now);
        dateEl.textContent = new Intl.DateTimeFormat('en-GB',{
          timeZone:tz, weekday:'short', day:'numeric', month:'short', year:'numeric'
        }).format(now);
        offsetEl.textContent = TZResolver.getOffsetString(tz);
      } catch(_e) { timeEl.textContent = '--:--:--'; }
    });
  }

  /* ── All Timezones tab ─────────────────────────────────── */

  const GROUP_ORDER = [
    'UTC','America','Europe','Asia','Pacific','Australia',
    'Africa','Atlantic','Indian','Arctic','Antarctica','Etc'
  ];

  function buildZonesTab() {
    zonesBuilt = true;
    const list     = document.getElementById('zones-list');
    const countEl  = document.getElementById('zones-count');
    const searchEl = document.getElementById('zones-search');
    if (!list) return;

    const allZones = Intl.supportedValuesOf('timeZone');
    const now      = new Date();

    // Group by region prefix
    const groups = {};
    allZones.forEach(tz => {
      const region = tz.includes('/') ? tz.split('/')[0] : 'Etc';
      (groups[region] = groups[region] || []).push(tz);
    });

    const frag = document.createDocumentFragment();
    const orderedKeys = [
      ...GROUP_ORDER.filter(k => groups[k]),
      ...Object.keys(groups).filter(k => !GROUP_ORDER.includes(k)).sort()
    ];

    orderedKeys.forEach(region => {
      const tzs = groups[region];
      const groupEl = document.createElement('div');
      groupEl.className = 'zone-group';
      groupEl.dataset.region = region.toLowerCase();

      const hdr = document.createElement('div');
      hdr.className = 'zone-group-header';
      hdr.innerHTML = `${region} <span class="zone-group-count">${tzs.length}</span>`;
      groupEl.appendChild(hdr);

      tzs.sort().forEach(tz => {
        const timeStr = new Intl.DateTimeFormat('en-GB', {
          timeZone: tz, hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
        }).format(now);
        const offset = TZResolver.getOffsetString(tz);

        const row = document.createElement('div');
        row.className = 'zone-row';
        row.dataset.search = tz.toLowerCase();
        row.title = `Click to use ${tz} as target timezone`;
        row.innerHTML =
          `<span class="zone-name">${tz}</span>` +
          `<span class="zone-time" data-tz="${tz}">${timeStr}</span>` +
          `<span class="zone-offset">${offset}</span>`;
        row.addEventListener('click', () => {
          if (toTzInput) toTzInput.value = tz;
          switchTab('converter');
          showToast(`Set target: ${tz}`);
        });
        groupEl.appendChild(row);
      });

      frag.appendChild(groupEl);
    });

    // Aliases group
    const aliasGroup = document.createElement('div');
    aliasGroup.className = 'zone-group';
    aliasGroup.dataset.region = 'aliases';

    const aliasHdr = document.createElement('div');
    aliasHdr.className = 'zone-group-header';
    const aliasEntries = Object.entries(TZC.TZ_ALIASES);
    aliasHdr.innerHTML = `Aliases <span class="zone-group-count">${aliasEntries.length}</span>`;
    aliasGroup.appendChild(aliasHdr);

    aliasEntries.sort((a,b) => a[0].localeCompare(b[0])).forEach(([alias, iana]) => {
      let timeStr = '--:--:--', offset = '';
      try {
        timeStr = new Intl.DateTimeFormat('en-GB', {
          timeZone: iana, hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
        }).format(now);
        offset = TZResolver.getOffsetString(iana);
      } catch(_) {}

      const row = document.createElement('div');
      row.className = 'zone-row';
      row.dataset.search = `${alias.toLowerCase()} ${iana.toLowerCase()}`;
      row.title = `${alias} → ${iana}`;
      row.innerHTML =
        `<span class="zone-name">${alias}<span class="zone-alias-label">→ ${iana}</span></span>` +
        `<span class="zone-time" data-tz="${iana}">${timeStr}</span>` +
        `<span class="zone-offset">${offset}</span>`;
      row.addEventListener('click', () => {
        if (toTzInput) toTzInput.value = iana;
        switchTab('converter');
        showToast(`Set target: ${iana}`);
      });
      aliasGroup.appendChild(row);
    });
    frag.appendChild(aliasGroup);

    list.appendChild(frag);

    const total = allZones.length + aliasEntries.length;
    if (countEl) countEl.textContent = `${total} timezones`;

    // Update times every 30s
    setInterval(() => {
      const n = new Date();
      list.querySelectorAll('.zone-time[data-tz]').forEach(el => {
        try {
          el.textContent = new Intl.DateTimeFormat('en-GB', {
            timeZone: el.dataset.tz, hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
          }).format(n);
        } catch(_) {}
      });
    }, 30000);

    // Search/filter
    if (searchEl) searchEl.addEventListener('input', () => {
      const q = searchEl.value.trim().toLowerCase();
      let visible = 0;

      list.querySelectorAll('.zone-row').forEach(row => {
        const match = !q || (row.dataset.search || '').includes(q);
        row.hidden = !match;
        if (match) visible++;
      });
      list.querySelectorAll('.zone-group').forEach(g => {
        g.hidden = ![...g.querySelectorAll('.zone-row')].some(r => !r.hidden);
      });
      if (countEl) countEl.textContent = q
        ? `${visible} match${visible !== 1 ? 'es' : ''}`
        : `${total} timezones`;
    });
  }

})();
