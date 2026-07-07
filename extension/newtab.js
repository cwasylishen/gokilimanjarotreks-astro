/* Kilimanjaro New Tab — Go Kilimanjaro Treks
   No servers, no tracking. Photos and facts are bundled; weather comes from
   the free open-meteo API (CORS-enabled, no key). */
(function () {
  'use strict';

  var SITE = 'https://gokilimanjarotreks.com';
  var UTM = '?utm_source=chrome_extension&utm_medium=newtab&utm_campaign=kili_tab';
  var $ = function (id) { return document.getElementById(id); };

  /* ---- storage wrapper: chrome.storage.local with localStorage fallback ---- */
  var hasChrome = typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local;
  function sGet(keys, cb) {
    if (hasChrome) { chrome.storage.local.get(keys, cb); return; }
    var out = {};
    keys.forEach(function (k) {
      try { var v = localStorage.getItem('gkt_' + k); if (v !== null) out[k] = JSON.parse(v); } catch (e) {}
    });
    cb(out);
  }
  function sSet(obj, cb) {
    if (hasChrome) { chrome.storage.local.set(obj, cb || function () {}); return; }
    Object.keys(obj).forEach(function (k) {
      try { localStorage.setItem('gkt_' + k, JSON.stringify(obj[k])); } catch (e) {}
    });
    if (cb) cb();
  }

  /* ---------------- photo of the day ---------------- */
  var dayIndex = Math.floor(Date.now() / 864e5);
  function showPhoto(offset) {
    var i = ((dayIndex + offset) % GKT_PHOTOS.length + GKT_PHOTOS.length) % GKT_PHOTOS.length;
    var p = GKT_PHOTOS[i];
    var img = $('bg');
    img.classList.remove('on');
    img.onload = function () { img.classList.add('on'); };
    img.src = p.file;
    $('caption').textContent = p.caption;
  }
  sGet(['photoOffset'], function (st) {
    var off = st.photoOffset || 0;
    showPhoto(off);
    $('next-photo').addEventListener('click', function () {
      off += 1; sSet({ photoOffset: off }); showPhoto(off);
    });
  });

  /* ---------------- clock + greeting ---------------- */
  function tickClock() {
    var d = new Date();
    $('clock').textContent = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    var h = d.getHours();
    $('greet').textContent = h < 5 ? 'The mountain is sleeping. So should you.'
      : h < 12 ? 'Good morning. Pole pole.'
      : h < 18 ? 'Good afternoon. Keep climbing.'
      : 'Good evening. Camp is earned.';
  }
  tickClock(); setInterval(tickClock, 15000);

  /* ---------------- daily Swahili word / fact ---------------- */
  var f = GKT_FACTS[dayIndex % GKT_FACTS.length];
  $('daily').innerHTML = f.sw
    ? '<span class="sw">' + f.sw + '</span> &middot; ' + f.en
    : f.fact;

  /* ---------------- Moshi time + weather (cached 30 min) ---------------- */
  var WMO = { 0: '☀️', 1: '☀️', 2: '⛅', 3: '☁️', 45: '🌫️', 48: '🌫️', 51: '🌦️', 53: '🌦️', 55: '🌧️', 61: '🌧️', 63: '🌧️', 65: '🌧️', 80: '🌦️', 81: '🌦️', 82: '🌧️', 95: '⛈️' };
  function moshiTime() {
    return new Intl.DateTimeFormat('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'Africa/Nairobi' }).format(new Date());
  }
  function renderMoshi(temp, code) {
    var wx = temp != null ? ' · ' + Math.round(temp) + '°C ' + (WMO[code] || '🌤️') : '';
    $('moshi-line').textContent = moshiTime() + wx;
  }
  function loadWeather() {
    sGet(['wx'], function (st) {
      var wx = st.wx;
      if (wx && Date.now() - wx.ts < 30 * 60 * 1000) { renderMoshi(wx.t, wx.c); return; }
      renderMoshi(wx && wx.t, wx && wx.c);
      fetch('https://api.open-meteo.com/v1/forecast?latitude=-3.3731&longitude=37.3441&current=temperature_2m,weather_code&timezone=Africa%2FNairobi', { cache: 'no-store' })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (d) {
          if (!d || !d.current) return;
          var rec = { t: d.current.temperature_2m, c: d.current.weather_code, ts: Date.now() };
          sSet({ wx: rec }); renderMoshi(rec.t, rec.c);
        }).catch(function () {});
    });
  }
  loadWeather(); setInterval(function () { renderMoshi(); loadWeather(); }, 60000);

  /* ---------------- brand links ---------------- */
  $('lnk-routes').href = SITE + '/kilimanjaro' + UTM;
  $('lnk-prices').href = SITE + '/prices' + UTM;
  $('lnk-blog').href = SITE + '/blog' + UTM;
  $('lnk-credit').href = SITE + '/gallery' + UTM;
  $('lnk-real').href = SITE + '/prices' + UTM;

  /* ---------------- Climb Mode ---------------- */
  var CAMPS = [
    { n: 0, name: 'Machame Gate', alt: 1800 },
    { n: 3, name: 'Machame Camp', alt: 3000 },
    { n: 6, name: 'Shira Camp', alt: 3840 },
    { n: 8, name: 'Lava Tower', alt: 4600 },
    { n: 10, name: 'Barranco Camp', alt: 3950 },
    { n: 12, name: 'Karanga Camp', alt: 4035 },
    { n: 14, name: 'Barafu Camp', alt: 4673 },
    { n: 16, name: 'Uhuru Peak', alt: 5895 }
  ];
  var TOTAL = 16;
  var climb = { sessions: 0, summits: 0, active: null };
  var tickTimer = null;

  function campFor(sessions) {
    var cur = CAMPS[0], next = null;
    for (var i = 0; i < CAMPS.length; i++) {
      if (sessions >= CAMPS[i].n) cur = CAMPS[i];
      else { next = CAMPS[i]; break; }
    }
    return { cur: cur, next: next };
  }
  function fmtAlt(a) { return a.toLocaleString('en-US') + ' m'; }

  function renderClimb() {
    var c = campFor(climb.sessions);
    $('camp-now').textContent = c.cur.name + ' · ' + fmtAlt(c.cur.alt);
    $('camp-next').textContent = c.next ? 'Next: ' + c.next.name + ' (' + (c.next.n - climb.sessions) + ' session' + (c.next.n - climb.sessions === 1 ? '' : 's') + ')' : 'Summit reached';
    $('bar-fill').style.width = Math.min(100, climb.sessions / TOTAL * 100) + '%';
    $('climb-stats').textContent = climb.sessions + ' / ' + TOTAL + ' sessions this climb' + (climb.summits ? ' · ' + climb.summits + ' summit' + (climb.summits === 1 ? '' : 's') + ' total' : '');
    $('summit').hidden = climb.sessions < TOTAL;
    var running = !!climb.active;
    $('t-start').hidden = running || climb.sessions >= TOTAL;
    $('t-50').hidden = running || climb.sessions >= TOTAL;
    $('t-stop').hidden = !running;
    if (!running) $('timer').textContent = climb.sessions >= TOTAL ? 'SUMMIT' : '25:00';
  }

  function buildMarks() {
    var wrap = $('bar-marks');
    CAMPS.forEach(function (c) {
      if (c.n === 0 || c.n === TOTAL) return;
      var i = document.createElement('i');
      i.style.left = (c.n / TOTAL * 100) + '%';
      i.title = c.name;
      wrap.appendChild(i);
    });
  }

  function saveClimb(cb) { sSet({ climb: climb }, cb); }

  function finishIfDue() {
    if (!climb.active) return false;
    if (Date.now() >= climb.active.end) {
      climb.sessions = Math.min(TOTAL, climb.sessions + 1);
      climb.active = null;
      saveClimb();
      renderClimb();
      return true;
    }
    return false;
  }

  function tick() {
    if (!climb.active) { clearInterval(tickTimer); tickTimer = null; return; }
    if (finishIfDue()) { clearInterval(tickTimer); tickTimer = null; return; }
    var left = Math.max(0, climb.active.end - Date.now());
    var m = Math.floor(left / 60000), s = Math.floor(left % 60000 / 1000);
    $('timer').textContent = (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
  }

  function startSession(mins) {
    climb.active = { start: Date.now(), end: Date.now() + mins * 60000 };
    saveClimb(); renderClimb();
    if (!tickTimer) tickTimer = setInterval(tick, 1000);
    tick();
  }

  sGet(['climb', 'panelOpen'], function (st) {
    if (st.climb) climb = st.climb;
    finishIfDue();
    buildMarks();
    renderClimb();
    if (climb.active) { tickTimer = setInterval(tick, 1000); tick(); }
    if (st.panelOpen) $('climb').hidden = false;
  });

  if (hasChrome) {
    chrome.storage.onChanged.addListener(function (ch, area) {
      if (area === 'local' && ch.climb) {
        climb = ch.climb.newValue || climb;
        renderClimb();
        if (climb.active && !tickTimer) { tickTimer = setInterval(tick, 1000); }
      }
    });
  }

  $('climb-toggle').addEventListener('click', function () {
    var el = $('climb');
    el.hidden = !el.hidden;
    sSet({ panelOpen: !el.hidden });
  });
  $('climb-close').addEventListener('click', function () {
    $('climb').hidden = true; sSet({ panelOpen: false });
  });
  $('t-start').addEventListener('click', function () { startSession(25); });
  $('t-50').addEventListener('click', function () { startSession(50); });
  $('t-stop').addEventListener('click', function () {
    climb.active = null; saveClimb(); renderClimb();
  });
  $('new-climb').addEventListener('click', function () {
    climb.summits += 1; climb.sessions = 0; climb.active = null;
    saveClimb(); renderClimb();
  });

  /* ---------------- summit certificate ---------------- */
  $('cert-btn').addEventListener('click', function () {
    var name = ($('cert-name').value || 'A Focused Climber').trim();
    var cv = $('cert-canvas'), ctx = cv.getContext('2d');
    var W = cv.width, H = cv.height;
    ctx.fillStyle = '#0b1a2e'; ctx.fillRect(0, 0, W, H);
    /* mountain silhouette */
    ctx.fillStyle = '#1d3557';
    ctx.beginPath();
    ctx.moveTo(0, H * 0.86); ctx.lineTo(W * 0.30, H * 0.46); ctx.lineTo(W * 0.44, H * 0.62);
    ctx.lineTo(W * 0.58, H * 0.34); ctx.lineTo(W * 0.72, H * 0.56); ctx.lineTo(W, H * 0.80);
    ctx.lineTo(W, H); ctx.lineTo(0, H); ctx.closePath(); ctx.fill();
    /* snow cap */
    ctx.fillStyle = 'rgba(255,255,255,.92)';
    ctx.beginPath();
    ctx.moveTo(W * 0.52, H * 0.425); ctx.lineTo(W * 0.58, H * 0.34); ctx.lineTo(W * 0.635, H * 0.43);
    ctx.lineTo(W * 0.605, H * 0.405); ctx.lineTo(W * 0.575, H * 0.44); ctx.lineTo(W * 0.545, H * 0.405);
    ctx.closePath(); ctx.fill();
    /* borders */
    ctx.strokeStyle = '#fbbf24'; ctx.lineWidth = 6; ctx.strokeRect(28, 28, W - 56, H - 56);
    ctx.lineWidth = 2; ctx.strokeRect(44, 44, W - 88, H - 88);
    ctx.textAlign = 'center';
    ctx.fillStyle = '#fbbf24'; ctx.font = '700 30px Georgia, serif';
    ctx.fillText('GO KILIMANJARO TREKS', W / 2, 130);
    ctx.fillStyle = '#ffffff'; ctx.font = '700 76px Georgia, serif';
    ctx.fillText('Certificate of Summit', W / 2, 240);
    ctx.font = '400 30px Georgia, serif'; ctx.fillStyle = 'rgba(255,255,255,.85)';
    ctx.fillText('This certifies that', W / 2, 320);
    ctx.fillStyle = '#fbbf24'; ctx.font = 'italic 700 60px Georgia, serif';
    ctx.fillText(name, W / 2, 405);
    ctx.fillStyle = 'rgba(255,255,255,.85)'; ctx.font = '400 30px Georgia, serif';
    ctx.fillText('climbed the Machame Route in ' + TOTAL + ' focused work sessions,', W / 2, 470);
    ctx.fillText('pole pole, all the way to Uhuru Peak.', W / 2, 515);
    ctx.fillStyle = '#ffffff'; ctx.font = '700 44px Georgia, serif';
    ctx.fillText('5,895 m · The Roof of Africa', W / 2, 600);
    ctx.fillStyle = 'rgba(255,255,255,.7)'; ctx.font = '400 26px Georgia, serif';
    ctx.fillText(new Date().toLocaleDateString([], { year: 'numeric', month: 'long', day: 'numeric' }), W / 2, 660);
    ctx.fillStyle = '#fbbf24'; ctx.font = '700 28px Georgia, serif';
    ctx.fillText('Climb the real one: gokilimanjarotreks.com', W / 2, H - 90);
    var a = document.createElement('a');
    a.download = 'kilimanjaro-summit-certificate.png';
    a.href = cv.toDataURL('image/png');
    a.click();
  });
})();
