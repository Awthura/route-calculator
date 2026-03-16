/**
 * Photon Autocomplete — drop-in replacement for Google Places Autocomplete.
 * Uses https://photon.komoot.io (OpenStreetMap data, free, no API key).
 *
 * Usage: initPhotonAutocomplete(inputElement)
 */
(function () {
  // Inject styles once
  if (!document.getElementById('photon-ac-style')) {
    const s = document.createElement('style');
    s.id = 'photon-ac-style';
    s.textContent =
      '.photon-dd{position:fixed;z-index:99999;background:#1a1d27;border:1px solid #2a2d3a;' +
      'border-top:none;border-radius:0 0 6px 6px;box-shadow:0 6px 20px rgba(0,0,0,0.55);' +
      'max-height:224px;overflow-y:auto;display:none;}' +
      '.photon-item{padding:8px 12px;font-size:12px;color:#e2e8f0;cursor:pointer;' +
      'border-bottom:1px solid #2a2d3a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}' +
      '.photon-item:last-child{border-bottom:none;}' +
      '.photon-item:hover,.photon-item.ac-on{background:rgba(79,142,247,0.13);color:#4f8ef7;}';
    document.head.appendChild(s);
  }

  // One shared dropdown element reused across all inputs
  const dd = document.createElement('div');
  dd.className = 'photon-dd';
  document.body.appendChild(dd);

  let activeInput = null;
  let items       = [];
  let activeIdx   = -1;
  let timer;

  /* ── Positioning ── */
  function pos() {
    if (!activeInput) return;
    const r = activeInput.getBoundingClientRect();
    dd.style.top   = r.bottom + 'px';
    dd.style.left  = r.left   + 'px';
    dd.style.width = r.width  + 'px';
  }
  window.addEventListener('scroll', pos, true);
  window.addEventListener('resize', pos);

  /* ── Hide ── */
  function hide() {
    dd.style.display = 'none';
    dd.innerHTML = '';
    items = [];
    activeIdx = -1;
  }

  /* ── Build readable label from Photon feature properties ── */
  function label(p) {
    const parts = [];
    if (p.name) parts.push(p.name);
    if (p.street && p.street !== p.name) parts.push(p.street);
    const city = p.city || p.town || p.village;
    if (city && city !== p.name) parts.push(city);
    if (p.state) parts.push(p.state);
    if (p.country) parts.push(p.country);
    return parts.join(', ');
  }

  /* ── Render items ── */
  function render(features) {
    items = features.map(f => label(f.properties)).filter(Boolean);
    if (!items.length) { hide(); return; }
    dd.innerHTML = items.map((t, i) =>
      `<div class="photon-item" data-i="${i}">${t}</div>`
    ).join('');
    dd.querySelectorAll('.photon-item').forEach(el =>
      el.addEventListener('mousedown', e => { e.preventDefault(); pick(items[+el.dataset.i]); })
    );
    pos();
    dd.style.display = 'block';
    activeIdx = -1;
    highlight();
  }

  /* ── Highlight active item ── */
  function highlight() {
    dd.querySelectorAll('.photon-item').forEach((el, i) =>
      el.classList.toggle('ac-on', i === activeIdx)
    );
  }

  /* ── Select a result ── */
  function pick(val) {
    if (!activeInput) return;
    activeInput.value = val;
    activeInput.dispatchEvent(new Event('change', { bubbles: true }));
    hide();
  }

  /* ── Fetch from Photon ── */
  async function fetch_(q) {
    try {
      const r = await fetch('https://photon.komoot.io/api/?q=' + encodeURIComponent(q) + '&limit=5');
      if (!r.ok) return;
      render((await r.json()).features || []);
    } catch { /* network error — silently ignore */ }
  }

  /* ── Close on outside click ── */
  document.addEventListener('click', e => {
    if (activeInput && !activeInput.contains(e.target) && !dd.contains(e.target)) hide();
  }, true);

  /* ── Public: attach to an input element ── */
  window.initPhotonAutocomplete = function (input) {
    if (!input || input._photonDone) return;
    input._photonDone = true;

    input.addEventListener('focus', () => { activeInput = input; });

    input.addEventListener('input', () => {
      clearTimeout(timer);
      activeIdx = -1;
      const q = input.value.trim();
      activeInput = input;
      if (q.length < 3) { hide(); return; }
      timer = setTimeout(() => fetch_(q), 300);
    });

    input.addEventListener('keydown', e => {
      if (activeInput !== input || dd.style.display === 'none') return;
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeIdx = Math.min(activeIdx + 1, items.length - 1);
        highlight();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeIdx = Math.max(activeIdx - 1, -1);
        highlight();
      } else if (e.key === 'Enter' && activeIdx >= 0) {
        e.preventDefault();
        pick(items[activeIdx]);
      } else if (e.key === 'Escape') {
        hide();
      }
    });

    // Small delay so mousedown on item fires before blur
    input.addEventListener('blur', () => {
      setTimeout(() => { if (activeInput === input) hide(); }, 150);
    });
  };
})();
