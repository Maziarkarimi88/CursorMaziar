(() => {
  const PROGRAM_COLOR = {
    Irrigation: "#2a9d8f",
    Watershed: "#c4a35a",
  };
  const LINE_COLOR = {
    Irrigation: "#4cc3d9",
    Watershed: "#d4b06a",
  };

  const state = {
    program: "ALL",
    status: "ALL",
    province: "ALL",
    selected: null,
    map: null,
    areaLayer: null,
    lineLayer: null,
    charts: {},
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

  function money(value) {
    const n = num(value);
    if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(2)}M`;
    if (n >= 1_000) return `$${(n / 1_000).toFixed(1)}k`;
    return `$${fmt(n)}`;
  }

  function schemes() {
    return window.JICA_DATA.schemes || [];
  }

  function visibleSchemes() {
    return schemes().filter((row) => {
      if (state.program !== "ALL" && row.PROGRAM !== state.program) return false;
      if (state.status !== "ALL" && row.STATUS !== state.status) return false;
      if (state.province !== "ALL" && row.PROVINCE !== state.province) return false;
      return true;
    });
  }

  function visibleIds() {
    return new Set(visibleSchemes().map((row) => row.SCHEME_UID));
  }

  function schemeById(id) {
    return schemes().find((row) => row.SCHEME_UID === id);
  }

  function renderKpis() {
    const rows = visibleSchemes();
    const awarded = rows.filter((r) => r.STATUS === "Awarded");
    const cost = awarded.reduce((sum, r) => sum + num(r.COST_USD), 0);
    $("kpi-schemes").textContent = String(rows.length);
    $("kpi-awarded").textContent = String(awarded.length);
    $("kpi-awarded-hint").textContent = `${rows.length - awarded.length} not awarded`;
    $("kpi-cost").textContent = money(cost);
    $("kpi-area").textContent = fmt(rows.reduce((sum, r) => sum + num(r.AREA_HA), 0));
    $("kpi-hh").textContent = fmt(rows.reduce((sum, r) => sum + num(r.HOUSEHOLDS), 0));
    $("kpi-canal").textContent = fmt(
      rows.filter((r) => r.PROGRAM === "Irrigation").reduce((sum, r) => sum + num(r.CANAL_KM), 0),
      1
    );
  }

  function ensureChart(id, spec) {
    const canvas = $(id);
    if (state.charts[id]) state.charts[id].destroy();
    state.charts[id] = new Chart(canvas, spec);
  }

  function renderCharts() {
    const rows = visibleSchemes();
    const programs = { Irrigation: 0, Watershed: 0 };
    for (const row of rows) programs[row.PROGRAM] += 1;
    ensureChart("chart-program", {
      type: "doughnut",
      data: {
        labels: Object.keys(programs),
        datasets: [{
          data: Object.values(programs),
          backgroundColor: [PROGRAM_COLOR.Irrigation, PROGRAM_COLOR.Watershed],
          borderWidth: 0,
        }],
      },
      options: {
        maintainAspectRatio: false,
        cutout: "62%",
        plugins: {
          legend: { position: "right", labels: { color: "#93a89b", boxWidth: 10, font: { size: 11 } } },
        },
      },
    });

    const byProvince = new Map();
    for (const row of rows) {
      if (row.STATUS !== "Awarded") continue;
      byProvince.set(row.PROVINCE, (byProvince.get(row.PROVINCE) || 0) + num(row.COST_USD));
    }
    const labels = [...byProvince.keys()];
    ensureChart("chart-cost", {
      type: "bar",
      data: {
        labels,
        datasets: [{
          data: labels.map((name) => byProvince.get(name)),
          backgroundColor: "#2a9d8f",
          borderRadius: 4,
        }],
      },
      options: {
        indexAxis: "y",
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: "#93a89b", callback: (v) => money(v) }, grid: { color: "rgba(168,196,176,0.08)" } },
          y: { ticks: { color: "#93a89b" }, grid: { display: false } },
        },
      },
    });
  }

  function popupHtml(row, kind) {
    if (!row) return "";
    const cost = row.COST_USD ? money(row.COST_USD) : "—";
    return `<strong>${row.SCHEME_NAME}</strong><br>
      ${row.SCHEME_UID} · ${row.SCHEME_CODE}<br>
      ${row.PROGRAM} ${kind} · ${row.STATUS}<br>
      ${row.PROVINCE} / ${row.DISTRICT}<br>
      Cost ${cost} · ${fmt(row.AREA_HA)} ha · ${fmt(row.HOUSEHOLDS)} HH`;
  }

  function areaStyle(feature) {
    const id = feature.properties.SCHEME_UID;
    const active = visibleIds().has(id);
    const selected = state.selected === id;
    const color = PROGRAM_COLOR[feature.properties.PROGRAM] || "#2a9d8f";
    return {
      color: selected ? "#ffffff" : color,
      weight: selected ? 2.8 : 1.2,
      fillColor: color,
      fillOpacity: !active ? 0.06 : selected ? 0.55 : 0.28,
      opacity: active ? 1 : 0.25,
    };
  }

  function lineStyle(feature) {
    const id = feature.properties.SCHEME_UID;
    const active = visibleIds().has(id);
    const selected = state.selected === id;
    const color = LINE_COLOR[feature.properties.PROGRAM] || "#4cc3d9";
    return {
      color: selected ? "#ffffff" : color,
      weight: selected ? 5 : 2.4,
      opacity: active ? 1 : 0.2,
    };
  }

  function schemeExtent(id) {
    const layers = [];
    state.areaLayer.eachLayer((layer) => {
      if (layer.feature && layer.feature.properties.SCHEME_UID === id) layers.push(layer);
    });
    state.lineLayer.eachLayer((layer) => {
      if (layer.feature && layer.feature.properties.SCHEME_UID === id) layers.push(layer);
    });
    if (!layers.length) return null;
    let bounds = layers[0].getBounds();
    for (const layer of layers.slice(1)) bounds = bounds.extend(layer.getBounds());
    return bounds;
  }

  function visibleExtent() {
    const ids = visibleIds();
    const layers = [];
    state.areaLayer.eachLayer((layer) => {
      if (ids.has(layer.feature.properties.SCHEME_UID)) layers.push(layer);
    });
    state.lineLayer.eachLayer((layer) => {
      if (ids.has(layer.feature.properties.SCHEME_UID)) layers.push(layer);
    });
    if (!layers.length) return null;
    let bounds = layers[0].getBounds();
    for (const layer of layers.slice(1)) bounds = bounds.extend(layer.getBounds());
    return bounds;
  }

  function zoomToScheme(id) {
    const bounds = id ? schemeExtent(id) : visibleExtent();
    if (!bounds || !bounds.isValid()) return;
    state.map.invalidateSize();
    state.map.fitBounds(bounds, { padding: [36, 36], maxZoom: 13, animate: true });
    $("map-hint").textContent = id
      ? `Zoomed to ${id} polygon + line`
      : "Polygon = area · line = canal or check-dam alignment";
  }

  function selectScheme(id, zoom = true) {
    state.selected = state.selected === id && !zoom ? null : id;
    if (!visibleIds().has(state.selected)) state.selected = id;
    refreshStyles();
    renderList();
    if (zoom) zoomToScheme(state.selected);
  }

  function refreshStyles() {
    if (state.areaLayer) state.areaLayer.setStyle(areaStyle);
    if (state.lineLayer) state.lineLayer.setStyle(lineStyle);
  }

  function renderList() {
    const rows = [...visibleSchemes()].sort((a, b) => Number(a.PACKAGE_NO) - Number(b.PACKAGE_NO) || a.PROGRAM.localeCompare(b.PROGRAM));
    $("scheme-list").innerHTML = rows.map((row) => {
      const active = state.selected === row.SCHEME_UID ? "active" : "";
      const statusClass = row.STATUS === "Awarded" ? "awarded" : "";
      return `<article class="row ${active}" data-id="${row.SCHEME_UID}">
        <span class="pill ${row.PROGRAM.toLowerCase()}">${row.PROGRAM === "Irrigation" ? "IS" : "WSM"}</span>
        <div>
          <div class="title">${row.SCHEME_NAME}</div>
          <div class="meta">${row.SCHEME_CODE} · ${row.PROVINCE} · ${row.DISTRICT}</div>
        </div>
        <div class="status ${statusClass}">${row.STATUS}</div>
      </article>`;
    }).join("");
    $("scheme-list").querySelectorAll(".row").forEach((el) => {
      el.addEventListener("click", () => selectScheme(el.dataset.id, true));
    });
  }

  function bindLayer(layer, kind) {
    layer.on("click", () => {
      const id = layer.feature.properties.SCHEME_UID;
      selectScheme(id, true);
      layer.bindPopup(popupHtml(schemeById(id), kind)).openPopup();
    });
  }

  function rebuildLayers() {
    if (state.areaLayer) state.map.removeLayer(state.areaLayer);
    if (state.lineLayer) state.map.removeLayer(state.lineLayer);
    state.areaLayer = L.geoJSON(window.JICA_DATA.areas, {
      style: areaStyle,
      onEachFeature: (_feature, layer) => bindLayer(layer, "area"),
    }).addTo(state.map);
    state.lineLayer = L.geoJSON(window.JICA_DATA.lines, {
      style: lineStyle,
      onEachFeature: (_feature, layer) => bindLayer(layer, "alignment"),
    }).addTo(state.map);
  }

  function initMap() {
    state.map = L.map("map", { zoomControl: true, attributionControl: true });
    L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}", {
      attribution: "Tiles © Esri",
      maxZoom: 16,
    }).addTo(state.map);
    rebuildLayers();
    const fit = () => zoomToScheme(state.selected);
    fit();
    setTimeout(fit, 250);
    window.addEventListener("resize", () => state.map.invalidateSize());
  }

  function fillFilters() {
    const programs = [...new Set(schemes().map((r) => r.PROGRAM))];
    const statuses = [...new Set(schemes().map((r) => r.STATUS))];
    const provinces = [...new Set(schemes().map((r) => r.PROVINCE))].sort();
    $("filter-program").innerHTML = `<option value="ALL">All programs</option>` +
      programs.map((v) => `<option value="${v}">${v}</option>`).join("");
    $("filter-status").innerHTML = `<option value="ALL">All status</option>` +
      statuses.map((v) => `<option value="${v}">${v}</option>`).join("");
    $("filter-province").innerHTML = `<option value="ALL">All provinces</option>` +
      provinces.map((v) => `<option value="${v}">${v}</option>`).join("");
  }

  function refresh() {
    if (state.selected && !visibleIds().has(state.selected)) state.selected = null;
    renderKpis();
    renderCharts();
    renderList();
    refreshStyles();
    if (state.map) zoomToScheme(state.selected);
  }

  function readGeojson(file, kind) {
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const geo = JSON.parse(reader.result);
        if (!geo.features || !geo.features.length) throw new Error("No features");
        const missing = geo.features.filter((f) => !f.properties || !f.properties.SCHEME_UID);
        if (missing.length) throw new Error("Each feature needs SCHEME_UID");
        window.JICA_DATA[kind] = geo;
        rebuildLayers();
        zoomToScheme(state.selected);
        $("stamp").textContent = `Loaded ${kind} ${new Date().toLocaleTimeString()}`;
      } catch (err) {
        alert("Could not use that GeoJSON: " + err.message);
      }
    };
    reader.readAsText(file);
  }

  function boot() {
    fillFilters();
    $("stamp").textContent = window.JICA_DATA.generatedAt || "Ready";
    $("filter-program").addEventListener("change", (e) => { state.program = e.target.value; refresh(); });
    $("filter-status").addEventListener("change", (e) => { state.status = e.target.value; refresh(); });
    $("filter-province").addEventListener("change", (e) => { state.province = e.target.value; refresh(); });
    $("btn-reset").addEventListener("click", () => {
      state.program = "ALL";
      state.status = "ALL";
      state.province = "ALL";
      state.selected = null;
      $("filter-program").value = "ALL";
      $("filter-status").value = "ALL";
      $("filter-province").value = "ALL";
      refresh();
    });
    $("file-areas").addEventListener("change", (e) => {
      if (e.target.files[0]) readGeojson(e.target.files[0], "areas");
    });
    $("file-lines").addEventListener("change", (e) => {
      if (e.target.files[0]) readGeojson(e.target.files[0], "lines");
    });
    renderKpis();
    renderCharts();
    renderList();
    initMap();
  }

  boot();
})();
