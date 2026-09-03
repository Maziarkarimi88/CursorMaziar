(() => {
  const PRIORITY_COLOR = {
    "P1-Expand": "#f5c15a",
    "P2-Defend": "#2ee6d6",
    "P3-FixQoS": "#ff5c7a",
    "P4-Monitor": "#5b8cff",
  };

  const state = {
    selectedZone: "ALL",
    priority: "ALL",
    fiber: "ALL",
    charts: {},
    map: null,
    zoneLayer: null,
    siteLayer: null,
    competitorLayer: null,
    subscriberLayer: null,
  };

  const $ = (id) => document.getElementById(id);

  function num(value) {
    const n = Number(value);
    return Number.isFinite(n) ? n : 0;
  }

  function fmt(value, digits = 0) {
    return num(value).toLocaleString(undefined, {
      maximumFractionDigits: digits,
      minimumFractionDigits: digits,
    });
  }

  function kpiById() {
    const map = new Map();
    for (const row of window.PULSE_DATA.kpis) map.set(row.DIST_ID, row);
    return map;
  }

  function filteredKpis() {
    return window.PULSE_DATA.kpis.filter((row) => {
      if (state.selectedZone !== "ALL" && row.DIST_ID !== state.selectedZone) return false;
      if (state.priority !== "ALL" && row.PRIORITY !== state.priority) return false;
      if (state.fiber !== "ALL" && (row.FIBER_STATUS || "") !== state.fiber) return false;
      return true;
    });
  }

  function zoneIds() {
    return new Set(filteredKpis().map((row) => row.DIST_ID));
  }

  function computeKpis(rows) {
    const subscribers = rows.reduce((s, r) => s + num(r.SUBSCRIBERS), 0);
    const pop = rows.reduce((s, r) => s + num(r.POPULATION), 0);
    const arpu = subscribers
      ? rows.reduce((s, r) => s + num(r.AVG_ARPU) * num(r.SUBSCRIBERS), 0) / subscribers
      : 0;
    const churn = subscribers
      ? rows.reduce((s, r) => s + num(r.AVG_CHURN) * num(r.SUBSCRIBERS), 0) / subscribers
      : 0;
    const cov = pop
      ? rows.reduce((s, r) => s + num(r.COV_4G_PCT) * num(r.POPULATION), 0) / pop
      : 0;
    const p1 = rows.filter((r) => String(r.PRIORITY).startsWith("P1")).length;
    const open = window.PULSE_DATA.decisions.filter((d) => {
      if (d.STATUS === "Approved") return false;
      if (state.selectedZone !== "ALL" && d.ZONE !== state.selectedZone && d.ZONE !== "All") return false;
      return true;
    }).length;
    return { subscribers, arpu, churn, cov, p1, open, pop };
  }

  function renderKpis() {
    const k = computeKpis(filteredKpis());
    $("kpi-subs").textContent = fmt(k.subscribers);
    $("kpi-arpu").textContent = `$${fmt(k.arpu, 1)}`;
    $("kpi-churn").textContent = `${fmt(k.churn * 100, 1)}%`;
    $("kpi-p1").textContent = String(k.p1);
    $("kpi-cov").textContent = `${fmt(k.cov, 1)}%`;
    $("kpi-open").textContent = String(k.open);
    $("kpi-subs-hint").textContent = state.selectedZone === "ALL" ? "All marketing zones" : state.selectedZone;
    $("kpi-churn").style.color = k.churn >= 0.35 ? "var(--rose)" : "var(--text)";
    $("kpi-cov").style.color = k.cov < 85 ? "var(--gold)" : "var(--text)";
  }

  function ensureChart(id, spec) {
    const canvas = $(id);
    if (state.charts[id]) state.charts[id].destroy();
    state.charts[id] = new Chart(canvas, spec);
  }

  function renderCharts() {
    const rows = [...filteredKpis()].sort((a, b) => num(b.AVG_ARPU) - num(a.AVG_ARPU));
    const counts = { "P1-Expand": 0, "P2-Defend": 0, "P3-FixQoS": 0, "P4-Monitor": 0 };
    for (const row of filteredKpis()) {
      if (counts[row.PRIORITY] !== undefined) counts[row.PRIORITY] += 1;
    }

    ensureChart("chart-priority", {
      type: "doughnut",
      data: {
        labels: Object.keys(counts),
        datasets: [{
          data: Object.values(counts),
          backgroundColor: Object.keys(counts).map((k) => PRIORITY_COLOR[k]),
          borderWidth: 0,
        }],
      },
      options: {
        maintainAspectRatio: false,
        cutout: "62%",
        plugins: {
          legend: {
            position: "right",
            labels: { color: "#8b9bb4", boxWidth: 10, font: { size: 11 } },
          },
        },
      },
    });

    ensureChart("chart-arpu", {
      type: "bar",
      data: {
        labels: rows.map((r) => r.DIST_NAME.replace("Central Business District", "CBD")),
        datasets: [{
          label: "ARPU (USD)",
          data: rows.map((r) => num(r.AVG_ARPU)),
          backgroundColor: rows.map((r) => PRIORITY_COLOR[r.PRIORITY] || "#5b8cff"),
          borderRadius: 4,
        }],
      },
      options: {
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: { color: "#8b9bb4", maxRotation: 48, minRotation: 0, font: { size: 10 } },
            grid: { display: false },
          },
          y: {
            ticks: { color: "#8b9bb4" },
            grid: { color: "rgba(148,163,184,0.08)" },
          },
        },
      },
    });

    const months = window.PULSE_DATA.monthly;
    ensureChart("chart-trend", {
      type: "line",
      data: {
        labels: months.map((m) => m.MONTH.slice(5)),
        datasets: [
          {
            label: "Subscribers",
            data: months.map((m) => num(m.SUBSCRIBERS)),
            yAxisID: "y",
            borderColor: "#2ee6d6",
            backgroundColor: "rgba(46,230,214,0.12)",
            fill: true,
            tension: 0.35,
            pointRadius: 2,
          },
          {
            label: "ARPU",
            data: months.map((m) => num(m.ARPU_USD)),
            yAxisID: "y1",
            borderColor: "#f5c15a",
            tension: 0.35,
            pointRadius: 2,
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: { labels: { color: "#8b9bb4", boxWidth: 10 } },
        },
        scales: {
          x: { ticks: { color: "#8b9bb4" }, grid: { display: false } },
          y: {
            ticks: { color: "#8b9bb4" },
            grid: { color: "rgba(148,163,184,0.08)" },
            title: { display: true, text: "Subs", color: "#8b9bb4" },
          },
          y1: {
            position: "right",
            ticks: { color: "#f5c15a" },
            grid: { display: false },
            title: { display: true, text: "ARPU", color: "#f5c15a" },
          },
        },
      },
    });
  }

  function renderList() {
    const rows = window.PULSE_DATA.decisions.filter((d) => {
      if (state.selectedZone !== "ALL" && d.ZONE !== state.selectedZone && d.ZONE !== "All") return false;
      if (state.priority !== "ALL") {
        const kpi = window.PULSE_DATA.kpis.find((k) => k.DIST_ID === d.ZONE);
        if (d.ZONE !== "All" && kpi && kpi.PRIORITY !== state.priority) return false;
      }
      return true;
    });
    $("decision-list").innerHTML = rows
      .map((d) => {
        const pri = String(d.PRIORITY).toLowerCase();
        return `<article class="row" data-zone="${d.ZONE}">
          <span class="pill ${pri}">${d.PRIORITY}</span>
          <div>
            <div class="title">${d.TITLE}</div>
            <div class="meta">${d.THEME} · ${d.ZONE} · ${d.OWNER}</div>
          </div>
          <div class="status">${d.STATUS}</div>
        </article>`;
      })
      .join("");
    $("decision-list").querySelectorAll(".row").forEach((el) => {
      el.addEventListener("click", () => {
        if (el.dataset.zone && el.dataset.zone !== "All") setZone(el.dataset.zone);
      });
    });
  }

  function zoneStyle(feature) {
    const row = kpiById().get(feature.properties.DIST_ID);
    const active = zoneIds().has(feature.properties.DIST_ID);
    const selected = state.selectedZone === feature.properties.DIST_ID;
    const color = PRIORITY_COLOR[(row && row.PRIORITY) || "P4-Monitor"];
    return {
      color: selected ? "#ffffff" : color,
      weight: selected ? 2.4 : 1.1,
      fillColor: color,
      fillOpacity: active ? 0.42 : 0.08,
    };
  }

  function popupHtml(feature) {
    const row = kpiById().get(feature.properties.DIST_ID) || {};
    return `<strong>${row.DIST_NAME || feature.properties.DIST_NAME}</strong><br>
      ${row.PRIORITY || ""}<br>
      Subscribers ${fmt(row.SUBSCRIBERS)} · ARPU $${fmt(row.AVG_ARPU, 1)}<br>
      Churn ${fmt(num(row.AVG_CHURN) * 100, 1)}% · 4G ${fmt(row.COV_4G_PCT, 1)}%`;
  }

  function initMap() {
    state.map = L.map("map", { zoomControl: true, attributionControl: true }).setView([34.53, 69.16], 12);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
      attribution: "&copy; OpenStreetMap &copy; CARTO",
      subdomains: "abcd",
      maxZoom: 18,
    }).addTo(state.map);

    const geo = JSON.parse(JSON.stringify(window.PULSE_DATA.zones));
    state.zoneLayer = L.geoJSON(geo, {
      style: zoneStyle,
      onEachFeature: (feature, layer) => {
        layer.bindPopup(popupHtml(feature));
        layer.on("click", () => setZone(feature.properties.DIST_ID));
      },
    }).addTo(state.map);

    state.siteLayer = L.layerGroup().addTo(state.map);
    state.competitorLayer = L.layerGroup().addTo(state.map);
    state.subscriberLayer = L.layerGroup().addTo(state.map);
    refreshMapLayers();
    state.map.fitBounds(state.zoneLayer.getBounds(), { padding: [16, 16] });
  }

  function refreshMapLayers() {
    const ids = zoneIds();
    state.zoneLayer.setStyle(zoneStyle);

    state.siteLayer.clearLayers();
    for (const site of window.PULSE_DATA.sites) {
      if (!ids.has(site.DIST_ID)) continue;
      const candidate = site.STATUS === "Candidate";
      L.circleMarker([site.LAT, site.LON], {
        radius: candidate ? 7 : 5,
        color: candidate ? "#f5c15a" : "#e8eef7",
        fillColor: candidate ? "#f5c15a" : "#2ee6d6",
        fillOpacity: 0.9,
        weight: 1.5,
      })
        .bindPopup(`<strong>${site.SITE_ID}</strong> · ${site.STATUS}<br>${site.SITE_NAME} · ${site.TECH}`)
        .addTo(state.siteLayer);
    }

    state.competitorLayer.clearLayers();
    for (const comp of window.PULSE_DATA.competitors || []) {
      if (comp.DIST_ID && !ids.has(comp.DIST_ID)) continue;
      L.circleMarker([comp.LAT, comp.LON], {
        radius: 4,
        color: "#ff5c7a",
        fillColor: "#ff5c7a",
        fillOpacity: 0.7,
        weight: 1,
      })
        .bindPopup(`<strong>${comp.COMP_ID}</strong> · ${comp.OPERATOR} ${comp.TECH}`)
        .addTo(state.competitorLayer);
    }

    state.subscriberLayer.clearLayers();
    const showSubs = $("toggle-subs") && $("toggle-subs").checked;
    if (showSubs) {
      for (const sub of window.PULSE_DATA.subscribers || []) {
        if (!ids.has(sub.DIST_ID)) continue;
        L.circleMarker([sub.LAT, sub.LON], {
          radius: 2,
          color: "transparent",
          fillColor: "#8b9bb4",
          fillOpacity: 0.45,
          weight: 0,
        }).addTo(state.subscriberLayer);
      }
    }
  }

  function setZone(id) {
    state.selectedZone = id === state.selectedZone ? "ALL" : id;
    $("filter-zone").value = state.selectedZone;
    refresh();
  }

  function fillFilters() {
    const zoneSel = $("filter-zone");
    const prioSel = $("filter-priority");
    const fiberSel = $("filter-fiber");
    zoneSel.innerHTML = `<option value="ALL">All zones</option>` +
      window.PULSE_DATA.kpis
        .map((r) => `<option value="${r.DIST_ID}">${r.DIST_NAME}</option>`)
        .join("");
    const prios = [...new Set(window.PULSE_DATA.kpis.map((r) => r.PRIORITY))];
    prioSel.innerHTML = `<option value="ALL">All priorities</option>` +
      prios.map((p) => `<option value="${p}">${p}</option>`).join("");
    const fibers = [...new Set(window.PULSE_DATA.kpis.map((r) => r.FIBER_STATUS || "").filter(Boolean))];
    fiberSel.innerHTML = `<option value="ALL">All fiber</option>` +
      fibers.map((f) => `<option value="${f}">${f}</option>`).join("");
  }

  function refresh() {
    renderKpis();
    renderCharts();
    renderList();
    if (state.zoneLayer) refreshMapLayers();
  }

  function parseCsv(text) {
    const lines = text.trim().split(/\r?\n/);
    const headers = lines[0].split(",").map((h) => h.trim());
    return lines.slice(1).map((line) => {
      const cols = line.split(",");
      const row = {};
      headers.forEach((h, i) => {
        row[h] = cols[i] === undefined ? "" : cols[i].trim();
      });
      return row;
    });
  }

  function ingestZoneCsv(text) {
    const rows = parseCsv(text);
    const needed = ["DIST_ID", "DIST_NAME", "SUBSCRIBERS", "AVG_ARPU", "AVG_CHURN"];
    const missing = needed.filter((k) => !Object.keys(rows[0] || {}).includes(k));
    if (missing.length) {
      alert("CSV is missing required columns: " + missing.join(", ") +
        "\nSee agol/field_map.json for the template schema.");
      return;
    }
    window.PULSE_DATA.kpis = rows.map((row) => ({
      ...row,
      POPULATION: num(row.POPULATION),
      SUBSCRIBERS: num(row.SUBSCRIBERS),
      AVG_ARPU: num(row.AVG_ARPU),
      AVG_CHURN: num(row.AVG_CHURN) > 1 ? num(row.AVG_CHURN) / 100 : num(row.AVG_CHURN),
      COV_4G_PCT: num(row.COV_4G_PCT),
      COV_GAP_POP: num(row.COV_GAP_POP),
      SUITABILITY: num(row.SUITABILITY),
      PRIORITY: row.PRIORITY || "P4-Monitor",
      FIBER_STATUS: row.FIBER_STATUS || "",
    }));
    fillFilters();
    state.selectedZone = "ALL";
    refresh();
    $("data-source").textContent = "Custom CSV loaded";
  }

  function wireEvents() {
    $("filter-zone").addEventListener("change", (e) => {
      state.selectedZone = e.target.value;
      refresh();
    });
    $("filter-priority").addEventListener("change", (e) => {
      state.priority = e.target.value;
      refresh();
    });
    $("filter-fiber").addEventListener("change", (e) => {
      state.fiber = e.target.value;
      refresh();
    });
    $("btn-reset").addEventListener("click", () => {
      state.selectedZone = "ALL";
      state.priority = "ALL";
      state.fiber = "ALL";
      $("filter-zone").value = "ALL";
      $("filter-priority").value = "ALL";
      $("filter-fiber").value = "ALL";
      refresh();
    });
    $("toggle-subs").addEventListener("change", refreshMapLayers);
    $("file-kpi").addEventListener("change", (e) => {
      const file = e.target.files && e.target.files[0];
      if (!file) return;
      file.text().then(ingestZoneCsv);
    });
    document.addEventListener("dragover", (e) => {
      e.preventDefault();
      document.body.classList.add("dragging");
    });
    document.addEventListener("dragleave", () => document.body.classList.remove("dragging"));
    document.addEventListener("drop", (e) => {
      e.preventDefault();
      document.body.classList.remove("dragging");
      const file = e.dataTransfer.files && e.dataTransfer.files[0];
      if (file && /\.csv$/i.test(file.name)) file.text().then(ingestZoneCsv);
    });
  }

  function boot() {
    if (!window.PULSE_DATA) {
      document.body.innerHTML = "<p style='padding:24px'>Missing assets/embedded-data.js. Run scripts/build_embedded_data.py.</p>";
      return;
    }
    fillFilters();
    wireEvents();
    initMap();
    refresh();
    $("stamp").textContent = new Date().toISOString().slice(0, 16).replace("T", " ") + " UTC";
  }

  window.MetroTelPulse = { refresh, ingestZoneCsv, computeKpis, filteredKpis };
  document.addEventListener("DOMContentLoaded", boot);
})();
