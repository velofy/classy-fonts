/* Classy Fonts — specimen cabinet */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const CAT_LABEL = {
    "display-serif": "Display serif", "editorial-serif": "Editorial serif",
    "display-expressive": "Display", "grotesk": "Grotesk", "mono": "Mono",
  };
  const CAT_ORDER = ["display-serif", "editorial-serif", "display-expressive", "grotesk", "mono"];

  const startTab = location.hash.replace("#", "") === "personal" ? "personal" : "commercial";
  const state = { tab: startTab, cat: "all", q: "", size: 50, text: "anishfyi", data: null };
  const lit = new Set();          // activated cards (fonts requested)
  const injected = new Set();     // fontshare css already injected

  // ---- theme ----
  const themeBtn = $("#themeBtn");
  const saved = localStorage.getItem("cf-theme");
  if (saved) document.documentElement.setAttribute("data-theme", saved);
  themeBtn.addEventListener("click", () => {
    const cur = document.documentElement.getAttribute("data-theme");
    const isDark = cur ? cur === "dark" : matchMedia("(prefers-color-scheme:dark)").matches;
    const next = isDark ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("cf-theme", next);
  });

  // ---- lazy font activation ----
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (!e.isIntersecting) continue;
      const el = e.target; io.unobserve(el);
      activate(el);
    }
  }, { rootMargin: "300px 0px" });

  function activate(el) {
    const big = $(".big", el);
    if (big && !el.dataset.lit) {
      const cssUrl = el.dataset.cssurl;
      if (cssUrl && !injected.has(cssUrl)) {
        const l = document.createElement("link");
        l.rel = "stylesheet"; l.href = cssUrl; document.head.appendChild(l);
        injected.add(cssUrl);
      }
      big.textContent = state.text || " ";
      el.dataset.lit = "1"; lit.add(el);
    }
    requestAnimationFrame(() => el.classList.add("shown"));
  }

  // ---- render ----
  const grid = $("#grid");
  function currentList() {
    const list = state.data[state.tab] || [];
    return list.filter((f) => {
      if (state.cat !== "all" && f.category !== state.cat) return false;
      if (state.q) {
        const hay = (f.family + " " + (f.designer || "") + " " + (f.tags || []).join(" ") + " " + CAT_LABEL[f.category]).toLowerCase();
        if (!hay.includes(state.q)) return false;
      }
      return true;
    });
  }

  function licBadge(f) {
    if (f.hosting === "image") return `<span class="lic personal"><span class="mark"></span>Personal use</span>`;
    if (f.licenseKind === "fontshare") return `<span class="lic"><span class="mark"></span>Free · commercial</span>`;
    return `<span class="lic"><span class="mark"></span>${f.licenseKind === "apache" ? "Apache" : "OFL"} · open</span>`;
  }

  function card(f, i) {
    const el = document.createElement(f.source || f.download ? "div" : "div");
    el.className = "spec enter";
    el.setAttribute("role", "listitem");
    el.tabIndex = 0;
    el.dataset.id = f.id;
    if (f.hosting === "cdn") el.dataset.cssurl = f.cssUrl;
    const catLabel = CAT_LABEL[f.category] || f.category;
    const face = f.css ? `font-family:'${f.css}',serif` : "";
    const body = f.hosting === "image"
      ? `<img class="img" loading="lazy" src="${f.specimen}" alt="${esc(f.family)} specimen">`
      : `<div class="big" style="${face}"></div>`;
    el.innerHTML = `
      <span class="go mono">${f.hosting === "image" ? "get ↗" : "open"}</span>
      ${body}
      <div class="meta">
        <div class="name"><b>${esc(f.family)}</b><span class="cat">${catLabel}</span></div>
        <div class="sub">
          ${f.designer ? `<span class="by">${esc(f.designer)}</span>` : ""}
          ${licBadge(f)}
        </div>
      </div>`;
    el.addEventListener("click", () => openModal(f));
    el.addEventListener("keydown", (ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); openModal(f); } });
    return el;
  }

  function paint() {
    lit.clear();
    const list = currentList();
    grid.classList.toggle("compact", state.tab === "commercial");
    grid.innerHTML = "";
    if (!list.length) { grid.innerHTML = `<div class="empty">No faces match that. Try clearing the search or category.</div>`; return; }
    const frag = document.createDocumentFragment();
    list.forEach((f, i) => { const c = card(f, i); frag.appendChild(c); });
    grid.appendChild(frag);
    $$(".spec", grid).forEach((el) => io.observe(el));
    document.documentElement.style.setProperty("--specimen-size", state.size + "px");
  }

  // ---- preview text ----
  const tester = $("#tester");
  let tTimer;
  tester.addEventListener("input", () => {
    clearTimeout(tTimer);
    tTimer = setTimeout(() => {
      state.text = (tester.textContent || "").trim() || "anishfyi";
      lit.forEach((el) => { const b = $(".big", el); if (b) b.textContent = state.text; });
    }, 90);
  });

  // ---- tabs ----
  function selectTab(name) {
    state.tab = name; state.cat = "all"; state.q = ""; $("#search").value = "";
    $$(".tab").forEach((x) => x.setAttribute("aria-selected", x.dataset.tab === name ? "true" : "false"));
    history.replaceState(null, "", name === "personal" ? "#personal" : "#");
    buildChips(); setTabNote(); paint();
  }
  $$(".tab").forEach((t) => t.addEventListener("click", () => {
    selectTab(t.dataset.tab); window.scrollTo({ top: chartTop(), behavior: "smooth" });
  }));
  function chartTop() { return $(".controls").offsetTop - 4; }

  // ---- chips ----
  function buildChips() {
    const list = state.data[state.tab] || [];
    const present = CAT_ORDER.filter((c) => list.some((f) => f.category === c));
    const chips = $("#chips");
    chips.innerHTML = `<button class="chip" data-cat="all" aria-pressed="true">All</button>` +
      present.map((c) => `<button class="chip" data-cat="${c}" aria-pressed="false">${CAT_LABEL[c]}</button>`).join("");
    $$(".chip", chips).forEach((ch) => ch.addEventListener("click", () => {
      state.cat = ch.dataset.cat;
      $$(".chip", chips).forEach((x) => x.setAttribute("aria-pressed", x === ch ? "true" : "false"));
      paint();
    }));
  }

  function setTabNote() {
    const n = $("#tabnote");
    n.innerHTML = state.tab === "commercial"
      ? `<span class="mark" style="color:var(--accent)"></span><span>Safe for commercial work, all free. Open faces are vendored in the repo as real files; Fontshare faces stream from the foundry's own CDN — click any for weights and downloads.</span>`
      : `<span class="mark"></span><span>Free for <b>personal</b> projects only. Shown as specimens; click through to the designer to download. Not for commercial use without a licence from the author.</span>`;
  }

  // ---- search / size ----
  let sTimer;
  $("#search").addEventListener("input", (e) => {
    clearTimeout(sTimer);
    sTimer = setTimeout(() => { state.q = e.target.value.trim().toLowerCase(); paint(); }, 120);
  });
  $("#size").addEventListener("input", (e) => {
    state.size = +e.target.value;
    document.documentElement.style.setProperty("--specimen-size", state.size + "px");
  });

  // ---- modal ----
  const modalBg = $("#modalBg"), modal = $("#modal");
  function openModal(f) {
    const face = f.css ? `font-family:'${f.css}',serif` : "";
    if (f.hosting === "cdn" && !injected.has(f.cssUrl)) {
      const l = document.createElement("link"); l.rel = "stylesheet"; l.href = f.cssUrl; document.head.appendChild(l); injected.add(f.cssUrl);
    }
    const sample = state.text || "anishfyi";
    const sizes = [72, 48, 34, 24, 18];
    const weightsTxt = (f.weights && f.weights.length) ? f.weights.join(" · ") : "";
    const body = f.hosting === "image"
      ? `<img class="img" src="${f.specimen}" alt="${esc(f.family)} specimen" style="aspect-ratio:auto;max-height:340px">`
      : `<div class="waterfall">${sizes.map((s) => `<div style="${face};font-size:${s}px">${esc(sample)}</div>`).join("")}</div>
         <div class="alpha" style="${face}">ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789 &amp; ? ! “ ” — @</div>`;
    const files = (f.files && f.files.length)
      ? `<div class="m-files"><h4>Download files</h4>${f.files.map((x) => `<a href="${x.ttf}" download>${x.w} · ttf ↓</a>`).join("")}</div>`
      : "";
    const actions = [];
    if (f.download) actions.push(`<a class="btn accent" href="${f.download}" ${f.hosting === "local" ? "download" : "target=_blank rel=noopener"}>${f.hosting === "image" ? "Get from designer ↗" : "Download ↓"}</a>`);
    if (f.source && f.source !== f.download) actions.push(`<a class="btn ghost" href="${f.source}" target="_blank" rel="noopener">Source ↗</a>`);
    modal.innerHTML = `
      <div class="modal-head">
        <div>
          <h2 id="mTitle" style="${face}">${esc(f.family)}</h2>
          <div class="m-sub">
            ${f.designer ? `<span>${esc(f.designer)}</span>` : ""}
            <span>${CAT_LABEL[f.category] || f.category}</span>
            ${licBadge(f)}
          </div>
        </div>
        <button class="icon-btn" id="mClose" aria-label="Close">✕</button>
      </div>
      <div class="modal-body">
        ${body}
        ${weightsTxt ? `<div class="wlist">${(f.weights || []).map((w) => `<span>${w}</span>`).join("")}</div>` : ""}
        <div class="m-sub" style="padding:4px 0 2px">${esc(f.license || "")}</div>
        <div class="m-actions">${actions.join("")}</div>
        ${files}
      </div>`;
    modalBg.classList.add("open");
    document.body.style.overflow = "hidden";
    $("#mClose").addEventListener("click", closeModal);
    $("#mClose").focus();
  }
  function closeModal() { modalBg.classList.remove("open"); document.body.style.overflow = ""; }
  modalBg.addEventListener("click", (e) => { if (e.target === modalBg) closeModal(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeModal(); });

  // ---- hero rotation ----
  function heroRotate(faces) {
    const t = $("#tester"), label = $("#heroFace");
    if (!faces.length || matchMedia("(prefers-reduced-motion:reduce)").matches) {
      t.style.fontFamily = `'${faces[0]}',serif`; label.textContent = faces[0]; return;
    }
    let i = 0;
    const tick = () => {
      const f = faces[i % faces.length];
      t.style.fontFamily = `'${f}',serif`; label.textContent = f;
      i++;
    };
    tick(); setInterval(tick, 3600);
  }

  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  // ---- boot ----
  fetch("data/fonts.json").then((r) => r.json()).then((data) => {
    state.data = data;
    $("#nCommercial").textContent = data.commercial.length;
    $("#nPersonal").textContent = data.personal.length;
    $("#totalCount").textContent = (data.commercial.length + data.personal.length) + " faces";
    $$(".tab").forEach((x) => x.setAttribute("aria-selected", x.dataset.tab === state.tab ? "true" : "false"));
    buildChips(); setTabNote(); paint();
    const heroFaces = data.commercial.filter((f) => f.hosting === "local" && f.category.includes("serif")).slice(0, 8).map((f) => f.css);
    heroRotate(heroFaces.length ? heroFaces : ["UI Display"]);
  }).catch((err) => {
    grid.innerHTML = `<div class="empty">Could not load the catalogue (${esc(err.message)}).</div>`;
  });
})();
