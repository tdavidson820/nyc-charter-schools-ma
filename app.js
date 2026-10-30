// NYC charter schools page. Reads data/buildings.geojson and data/summary.json (built by scripts/build_site_data.py).
(async function () {
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const AUTH = [
    { key: "SUNY", label: "SUNY Trustees", color: css("--suny") },
    { key: "Board of Regents", label: "Board of Regents", color: css("--regents") },
    { key: "NYC DOE", label: "NYC Chancellor", color: css("--doe") },
  ];
  const AC = Object.fromEntries(AUTH.map((a) => [a.key, a.color]));
  const AL = Object.fromEntries(AUTH.map((a) => [a.key, a.label]));
  const BOROUGHS = ["Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"];
  const OTHER = "Independent and smaller networks";
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmt = (n) => Number(n).toLocaleString("en-US");
  const $ = (id) => document.getElementById(id);

  // On <user>.github.io/<repo>/, link the report to GitHub's rendered Markdown.
  const gh = location.hostname.match(/^([^.]+)\.github\.io$/);
  if (gh) {
    const repo = location.pathname.split("/").filter(Boolean)[0] || `${gh[1]}.github.io`;
    $("link-validation").href = $("link-validation-top").href = `https://github.com/${gh[1]}/${repo}/blob/main/VALIDATION.md`;
  }

  const load = (p) => fetch(p).then((r) => { if (!r.ok) throw new Error(p); return r.json(); });
  let buildings, S, districts, boroughs;
  try {
  [buildings, S, districts, boroughs] = await Promise.all([
    load("data/buildings.geojson"), load("data/summary.json"), load("data/districts.geojson"), load("data/boroughs.geojson"),
  ]);
  } catch (error) {
    console.error("Map data loading failed", error);
    const msg = document.createElement("p");
    msg.setAttribute("role", "alert");
    msg.textContent = "Map data could not be loaded. Check that the data folder was deployed in full.";
    msg.style.cssText = "padding:20px;background:#fff4e5;color:#633c00";
    document.querySelector(".map-wrap")?.prepend(msg);
    return;
  }
  document.querySelectorAll("[data-k]").forEach((el) => { el.textContent = fmt(S[el.dataset.k]); });

  // ---------- Breakdown charts (all bars share one scale per chart) ----------
  const camp = buildings.features.flatMap((f) => f.properties.campuses.map((c) => ({ ...c, borough: f.properties.borough })));
  $("key-auth").innerHTML = AUTH.map((a) => `<span><i style="background:${a.color}"></i>${esc(a.label)}</span>`).join("");
  const byBA = {};
  camp.forEach((c) => { byBA[c.borough] = byBA[c.borough] || {}; byBA[c.borough][c.authorizer] = (byBA[c.borough][c.authorizer] || 0) + 1; });
  const maxB = Math.max(...BOROUGHS.map((b) => S.campuses_by_borough[b] || 0));
  $("c-borough").innerHTML = BOROUGHS.map((b) => {
    const tot = S.campuses_by_borough[b] || 0;
    const segs = AUTH.map((a) => { const n = (byBA[b] || {})[a.key] || 0; return n ? `<span style="width:${(100 * n) / maxB}%;background:${a.color}" title="${esc(a.label)}: ${n}"></span>` : ""; }).join("");
    return `<div class="bar"><span class="lab">${b}</span><span class="track">${segs}</span><span class="val">${fmt(tot)}</span></div>`;
  }).join("");
  const maxA = Math.max(...AUTH.map((a) => S.schools_by_authorizer[a.key] || 0));
  $("c-auth").innerHTML = AUTH.map((a) => {
    const n = S.schools_by_authorizer[a.key] || 0;
    return `<div class="bar"><span class="lab">${esc(a.label)}</span><span class="track"><span style="width:${(100 * n) / maxA}%;background:${a.color}"></span></span><span class="val">${fmt(n)}</span></div>`;
  }).join("") + `<p class="note">${fmt(S.campuses_by_authorizer.SUNY)} SUNY, ${fmt(S.campuses_by_authorizer["Board of Regents"])} Regents and ${fmt(S.campuses_by_authorizer["NYC DOE"])} Chancellor campuses.</p>`;
  const nets = S.networks.filter((n) => n.network !== OTHER).slice(0, 8);
  const maxN = Math.max(...nets.map((n) => n.campuses));
  $("c-net").innerHTML = nets.map((n) => {
    const sa = n.network === "Success Academy";
    return `<div class="bar${sa ? " hl" : ""}"><span class="lab">${esc(n.network)}</span><span class="track"><span style="width:${(100 * n.campuses) / maxN}%;background:${sa ? css("--sa") : css("--muted")}"></span></span><span class="val">${n.campuses}</span></div>`;
  }).join("");
  const other = S.networks.find((n) => n.network === OTHER);
  $("net-note").textContent = `${other.schools} schools (${other.campuses} campuses) are independent or part of networks with fewer than three schools. Networks are grouped by school name.`;

  // ---------- Map ----------
  const map = L.map("map", { zoomSnap: 0.25, scrollWheelZoom: false, zoomControl: true });
  map.on("click focus", () => map.scrollWheelZoom.enable());
  map.on("mouseout", () => map.scrollWheelZoom.disable());
  const tiles = L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
    subdomains: "abcd", maxZoom: 19,
  }).addTo(map);

  const counts = S.campuses_by_district;
  const ramp = (n) => (n >= 20 ? css("--d4") : n >= 12 ? css("--d3") : n >= 6 ? css("--d2") : css("--d1"));
  const landLayer = L.geoJSON(boroughs, { style: { stroke: false, fillColor: css("--land"), fillOpacity: 0 }, interactive: false }).addTo(map);
  const distStyle = (f) => ({ color: "#8895a3", weight: 0.6, dashArray: "3 3", fillColor: ramp(counts[String(f.properties.district)] || 0), fillOpacity: state.dist ? 0.55 : 0 });
  const state = { boro: "", auth: new Set(AUTH.map((a) => a.key)), net: "", q: "", sa: true, dist: true };
  const distLayer = L.geoJSON(districts, {
    style: distStyle,
    onEachFeature: (f, l) => l.bindTooltip(`District ${f.properties.district}: ${counts[String(f.properties.district)] || 0} campuses`, { sticky: true, className: "dist-tip" }),
  }).addTo(map);
  const boroLayer = L.geoJSON(boroughs, { style: { color: "#4a5561", weight: 1.3, fill: false }, interactive: false }).addTo(map);
  // If street tiles cannot load (offline or a sandboxed preview), draw land on a water ground instead.
  let tileFail = false;
  tiles.on("tileerror", () => { if (!tileFail) { tileFail = true; landLayer.setStyle({ fillOpacity: 1 }); } });

  const boroBounds = {};
  boroLayer.eachLayer((l) => { boroBounds[l.feature.properties.name] = l.getBounds(); });
  const cityBounds = boroLayer.getBounds();

  // ---------- Controls ----------
  $("zoom").innerHTML = ["", ...BOROUGHS].map((b) => `<button type="button" data-b="${b}" aria-pressed="${b === "" ? "true" : "false"}">${b || "All NYC"}</button>`).join("");
  $("zoom").addEventListener("click", (e) => {
    const b = e.target.closest("button"); if (!b) return;
    state.boro = b.dataset.b;
    $("zoom").querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    map.closePopup();
    map.flyToBounds(state.boro ? boroBounds[state.boro] : cityBounds, { padding: [16, 16], duration: 0.6 });
    render();
  });
  $("f-auth").innerHTML = AUTH.map((a) => `<button type="button" class="chip" data-a="${esc(a.key)}" aria-pressed="true"><span class="sw" style="background:${a.color}"></span>${esc(a.label)}<span class="ct">${S.schools_by_authorizer[a.key]}</span></button>`).join("");
  $("f-auth").addEventListener("click", (e) => {
    const b = e.target.closest(".chip"); if (!b) return;
    const k = b.dataset.a;
    state.auth.has(k) ? state.auth.delete(k) : state.auth.add(k);
    b.setAttribute("aria-pressed", String(state.auth.has(k)));
    render();
  });
  $("f-net").insertAdjacentHTML("beforeend", S.networks.map((n) => `<option value="${esc(n.network)}">${esc(n.network)} (${n.schools})</option>`).join(""));
  $("f-net").addEventListener("change", (e) => { state.net = e.target.value; render(); });
  $("q").addEventListener("input", (e) => { state.q = e.target.value.trim().toLowerCase(); render(); });
  $("f-sa").addEventListener("change", (e) => { state.sa = e.target.checked; render(); });
  $("f-dist").addEventListener("change", (e) => { state.dist = e.target.checked; distLayer.setStyle(distStyle); });

  // ---------- Markers and list ----------
  const markers = L.layerGroup().addTo(map);
  let shown = [];
  const byBuilding = new Map();
  const popupHtml = (p, cs) => {
    const addr = [...new Set(cs.map((c) => c.address))].join(" / ");
    return `<div class="pop-addr">${esc(addr)} · ${esc(p.borough)} · District ${esc(p.district)}</div>` + cs.map((c) => `<div class="pop-c">
      <div class="pop-n">${esc(c.school)}</div>
      <div class="pop-m"><span class="tag" style="background:${AC[c.authorizer]}">${esc(AL[c.authorizer])}</span>${c.grades ? "Grades " + esc(c.grades) + " · " : ""}${esc(c.network === OTHER ? "Independent or small network" : c.network)}</div>
      <div class="pop-e">Confirmed by ${esc(c.evidence)}</div>${c.note ? `<div class="pop-e">${esc(c.note)}</div>` : ""}</div>`).join("") +
      `<div class="pop-v">Verified October 30, 2026</div>`;
  };
  const match = (c, p) => (!state.boro || p.borough === state.boro) && state.auth.has(c.authorizer) && (!state.net || c.network === state.net) &&
    (!state.q || c.school.toLowerCase().includes(state.q) || c.address.toLowerCase().includes(state.q));

  function render() {
    markers.clearLayers(); byBuilding.clear();
    const schools = new Map();
    let nCamp = 0;
    shown = [];
    buildings.features.forEach((f, i) => {
      const p = f.properties;
      const cs = p.campuses.filter((c) => match(c, p));
      if (!cs.length) return;
      nCamp += cs.length;
      cs.forEach((c) => {
        const s = schools.get(c.school) || { name: c.school, authorizer: c.authorizer, network: c.network, sa: c.sa, idx: [], boros: new Set() };
        s.idx.push(i); s.boros.add(p.borough); schools.set(c.school, s);
      });
      const auths = new Set(cs.map((c) => c.authorizer));
      const sa = state.sa && cs.some((c) => c.sa);
      const base = { color: sa ? css("--sa") : "#ffffff", weight: sa ? 2.6 : 1.3 };
      const [lon, lat] = f.geometry.coordinates;
      const m = L.circleMarker([lat, lon], {
        radius: 5.5 + Math.min(4.5, (cs.length - 1) * 1.6),
        fillColor: auths.size > 1 ? css("--multi") : AC[[...auths][0]], fillOpacity: 0.92, ...base,
      }).bindPopup(popupHtml(p, cs), { maxWidth: 360 });
      m._base = base;
      m.addTo(markers); byBuilding.set(i, m);
      const el = m.getElement();
      if (el) {
        el.setAttribute("tabindex", "0"); el.setAttribute("role", "button");
        el.setAttribute("aria-label", `${cs.length === 1 ? cs[0].school : cs.length + " schools"}, ${cs[0].address}, ${p.borough}`);
        el.addEventListener("keydown", (ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); m.openPopup(); } });
      }
      cs.forEach((c) => shown.push({ ...c, borough: p.borough, district: p.district, lat, lon }));
    });
    $("s-schools").textContent = fmt(schools.size);
    $("s-campuses").textContent = fmt(nCamp);
    $("s-buildings").textContent = fmt(byBuilding.size);

    const list = [...schools.values()].sort((a, b) => a.name.localeCompare(b.name));
    $("list-meta").textContent = `${fmt(list.length)} schools${state.boro ? " in " + state.boro : ""}. Select one to find it on the map.`;
    $("school-list").innerHTML = list.length ? list.map((s, k) => `<li><button type="button" data-k="${k}">
      <span class="sw${s.sa && state.sa ? " sa" : ""}" style="background:${AC[s.authorizer]}"></span>
      <span class="nm">${esc(s.name)}</span>
      <span class="cc">${s.idx.length} ${s.idx.length === 1 ? "campus" : "campuses"}</span>
      <span class="mt">${esc(s.network === OTHER ? "Independent or small network" : s.network)} · ${esc([...s.boros].join(", "))}</span>
    </button></li>`).join("") : `<li class="empty">No schools match these filters.</li>`;
    $("school-list").onclick = (e) => {
      const b = e.target.closest("button"); if (!b) return;
      const ms = list[+b.dataset.k].idx.map((i) => byBuilding.get(i));
      const open = () => ms[0].openPopup();
      if (ms.length === 1) map.flyTo(ms[0].getLatLng(), Math.max(map.getZoom(), 14.5), { duration: 0.6 });
      else map.flyToBounds(L.latLngBounds(ms.map((m) => m.getLatLng())), { padding: [60, 60], maxZoom: 14.5, duration: 0.6 });
      map.once("moveend", open);
    };
    const hi = (e, on) => {
      const b = e.target.closest("button"); if (!b) return;
      list[+b.dataset.k].idx.forEach((i) => { const m = byBuilding.get(i); m.setStyle(on ? { color: "#e4002b", weight: 3.5 } : m._base); if (on) m.bringToFront(); });
    };
    $("school-list").onmouseover = (e) => hi(e, true);
    $("school-list").onmouseout = (e) => hi(e, false);
  }

  // Reset every filter and return to the full city.
  $("reset").addEventListener("click", () => {
    Object.assign(state, { boro: "", net: "", q: "", sa: true });
    state.auth = new Set(AUTH.map((a) => a.key));
    $("f-net").value = ""; $("q").value = ""; $("f-sa").checked = true;
    $("f-auth").querySelectorAll(".chip").forEach((b) => b.setAttribute("aria-pressed", "true"));
    $("zoom").querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.b === "")));
    map.closePopup(); map.flyToBounds(cityBounds, { padding: [8, 8], duration: 0.6 });
    render();
  });
  // Download the campuses currently shown.
  $("csv").addEventListener("click", () => {
    const cols = ["school", "network", "authorizer", "address", "borough", "district", "grades", "lat", "lon", "evidence", "note"];
    const q = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const rows = [...shown].sort((a, b) => a.school.localeCompare(b.school)).map((c) => cols.map((k) => q(k === "authorizer" ? AL[c[k]] : c[k])).join(","));
    const blob = new Blob([cols.join(",") + "\n" + rows.join("\n") + "\n"], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `nyc-charter-campuses-2026-10-30${state.boro ? "-" + state.boro.toLowerCase().replace(/ /g, "-") : ""}.csv`;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  });

  map.fitBounds(cityBounds, { padding: [8, 8] });
  render();
  window.addEventListener("resize", () => map.invalidateSize());

  // ---------- Analysis ----------
  $("findings").innerHTML = S.findings.map((f) => `<div class="finding"><span class="fig">${esc(f.figure)}</span><p>${esc(f.text)}</p></div>`).join("");
  const REASON = { not_open: "Not yet open", closed: "Closed", merged: "Merged", not_operating: "Closed", consolidated: "Consolidated", transferred: "Transferred", renamed: "Renamed" };
  $("n-ex").textContent = S.excluded_schools.length;
  $("t-excluded").innerHTML = "<tbody>" + S.excluded_schools.map((r) =>
    `<tr><td>${esc(r.school)}${r.authorizer ? `<span class="s">${esc(AL[r.authorizer] || r.authorizer)}</span>` : ""}</td><td><b>${esc(REASON[r.reason] || r.reason)}.</b> ${esc(r.detail)}</td></tr>`).join("") + "</tbody>";
  const LS = { stale: "Old address", not_open: "Opens 2027" };
  $("n-ls").textContent = S.listings_not_mapped.length;
  $("t-listings").innerHTML = "<tbody>" + S.listings_not_mapped.map((r) =>
    `<tr><td>${esc(r.listing)}<span class="s">${esc(r.address)} · ${esc(r.source)}</span></td><td><b>${esc(LS[r.status] || r.status)}.</b> ${esc(r.resolution)}</td></tr>`).join("") + "</tbody>";
  if (S.under_review.length) $("review-line").textContent = `Under review: ${S.under_review.map((r) => r.school + ", " + r.address).join("; ")}.`;
})();
