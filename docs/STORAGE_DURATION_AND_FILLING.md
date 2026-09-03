# Storage duration and rainfall needed to fill a check dam

**Correction to earlier notes.** The Afghan programme is **not** designed around a few hours of flood detention. Across provinces, the **design intent is to hold a full pond for about 1–3 months**. Inflow is **mostly rainfall runoff** (plus snowmelt where the catchment is high). Earlier Annex A (hours-only) still applies to **gabion / leaky** outliers that empty in hours; it is **not** the default for this research.

This note: (1) which parameters control how long water stays, (2) how to estimate the rainfall that fills the pond to **100%**, (3) what that means for I1–I5 and for WaPOR, (4) the papers to cite.

Workbook sheet `FillAndHold` implements the fill and hold formulae. Field log is **daily Form B** (Dashora / MARVI). Keep **I4/I5** against a control.

---

## 1. What “1–3 months at full storage” actually means

Two different clocks are often mixed:

| Clock | Meaning | Typical Afghan design intent |
|-------|---------|------------------------------|
| **Fill time** | How long from empty (or partly full) until the water surface reaches the spillway | One large storm, or several storms in the wet months |
| **Hold time** | How long water remains after inflow stops, from full down to dry (or to a useful residual) | **About 30–90 days** if the bed and wall behave as designed |

A dam can **fill in one night** and still **hold for two months**. Hold time is **not** the storm duration. It is a **volume / loss-rate** problem:

\[
\frac{\mathrm{d}V}{\mathrm{d}t}=Q_{\mathrm{in}}-Q_{\mathrm{spill}}-E\,A(h)-i\,A_{\mathrm{bed}}(h)-Q_{\mathrm{wall}}-Q_{\mathrm{outlet}}-Q_{\mathrm{pump}}
\]

After the catchment stops running and the spillway is dry:

\[
t_{\mathrm{hold}}\approx\int_{V_{\mathrm{full}}}^{0}\frac{\mathrm{d}V}{E A+i A_{\mathrm{bed}}+Q_{\mathrm{wall}}+Q_{\mathrm{outlet}}+Q_{\mathrm{pump}}}
\]

A first look (constant full-supply area — **shortest** hold; real hold is longer as the water surface shrinks):

\[
t_{\mathrm{hold,min}}\approx\frac{V_{\mathrm{crest}}}{(E+i)\,A_{\mathrm{crest}}+Q_{\mathrm{wall}}}
\]

Mean depth \(d=V/A\) makes the same point: \(t\approx d/(E+i)\).

**Worked scale.** A 2 m mean depth, evaporation 6 mm d⁻¹, bed infiltration 25 mm d⁻¹ (Rajasthan check-dam band) → \(t\approx 2000/31\approx 65\) days. That **is** the 1–3 month window. Clean gravel at 200 mm d⁻¹ would empty in ~10 days and **miss** the design. A silt-sealed bed at 3 mm d⁻¹ would hold ~7 months but most of the water would **evaporate** (Balochistan delay-action failure).

India’s CGWB percolation tanks are explicitly meant to **extend recharge 2–3 months after monsoon** (CGWB 2007). That is the same design family as a 1–3 month Afghan check dam, not a leaky weir.

---

## 2. Parameters that control storage duration

Group them the way a water-balance audit does. Record once on Form A; confirm while ponded on Form B.

### 2.1 Geometry (volume versus area)

| Parameter | Effect on hold time | Why |
|-----------|---------------------|-----|
| Crest height / spillway invert | Taller crest → more \(V\) | More water to lose |
| Valley shape (stage–area–volume) | Deep, narrow pond holds longer than a wide, shallow pan of the same \(V\) | \(E\) and \(i\) scale with **area**; a pancake evaporates and soaks faster |
| Mean depth \(V/A\) at full supply | Primary geometric KPI | Target 1–3 months needs roughly \(d \gtrsim (E+i)\times 30\)–\(90\) days |
| Dead storage / silted bed raising the floor | Less \(V\), often more area per volume | Silt both **cuts \(i\)** (longer hold) and **steals storage** |

Survey a stage–area–volume table for the **pond** (Form A4), from DEM Surface Volume or tape. Without \(A(h)\) you cannot convert a falling gauge into m³ or days. You are **not** filling the catchment; see `docs/ARCGIS_STORAGE_FROM_DEM.md`.

### 2.2 Bed infiltration \(i\) (usually the largest term)

| Parameter | Longer hold | Shorter hold |
|-----------|-------------|--------------|
| Bed texture | Silt, fine sand, weathered rock | Clean gravel/cobble |
| Fresh silt drape | Thick drape after the first floods | Scraped / coarse after desilting |
| Connection to water table | Pond **connected** (mound reaches the bed; infiltration slows) | **Disconnected** deep table (free drainage) |
| Antecedent wetness | Already wet (lower suction, sometimes lower \(K\)) | Dry cracked bed at season start (fast first days) |
| Bioturbation, livestock, desilting | Trampling can seal; careful scrape can restore \(i\) | Mechanical scrape that smears fines can **reduce** \(i\) (Dashora/MARVI) |

**Literature band.** Dashora et al. (2018, 2019): mean dry-weather infiltration **10–57 mm d⁻¹** (site means ~18–48 mm d⁻¹), **5–8 × evaporation**. Sukhija et al. (1997): if stage falls **>20 mm d⁻¹**, the structure is still “effective” relative to evaporation (~10 mm d⁻¹). Oman dry dams: infiltration dropped by about **an order of magnitude** after decades of silt (from ~16 cm h⁻¹ toward 0.18 cm h⁻¹ in related tests).

For a **1–3 month** hold at a few metres depth you **need** \(i\) in a moderate band (~10–40 mm d⁻¹), not a gravel sieve and not a clay pan.

### 2.3 Evaporation \(E\) (first-class over months; negligible over hours)

| Parameter | Longer hold | Shorter hold |
|-----------|-------------|--------------|
| Season of the full pond | Winter / early spring (low \(E\)) | Summer (Kandahar-class open-water \(E\) often **6–12 mm d⁻¹**) |
| Wind, humidity, fetch | Sheltered, humid | Windy arid pan |
| Area/volume | Deep | Wide shallow |

Over **hours**, \(E\) is ~0.3–0.5 mm h⁻¹ and can be ignored next to gravel infiltration. Over **60 days** at 8 mm d⁻¹, \(E\) is **~480 mm** — a large fraction of a shallow pond. That is why Dashora track \(I/E\) and why Balochistan silted delay-action dams became **evaporation ponds**.

Use a Class-A pan × 0.7 (or Penman open-water) as in Dashora (they used ~5 mm d⁻¹ at Udaipur). WaPOR **RET** can supply a regional demand number; it is **not** pond \(E\) and **not** recharge.

### 2.4 The dam body and outlets

| Parameter | Longer hold | Shorter hold |
|-----------|-------------|--------------|
| Wall type | Masonry / well-compacted earth, cut-off to bedrock or clay | Gabion, leaky weir, poorly founded wall |
| Foundation / abutment seepage | Grouted, keyed | Permeable gravels under the wall (water bypasses) |
| Low-level drain / irrigation pipe | Closed | Open, leaking, or used for irrigation |
| Spillway | Only spills when full; does not leak at the crest | Crest leakage, pipes through the wall |

A “check dam” that is meant to hold 1–3 months is hydrologically a **small reservoir / percolation tank**. Gabions that drain through the mesh will **not** meet that spec unless they silt up (and then they may evaporate).

### 2.5 Catchment inflow while you are trying to hold water

Hold time is measured **after** inflow stops. During the wet season, extra storms **refill** the pond, so “days with water” can exceed the no-inflow hold time. Dashora’s **days stored per year** and **fillings per year (I2)** capture that. A cascade of upstream dams **starves** the downstream pond (Alderwish 2010, Sana’a).

### 2.6 Human use and climate

Pumping from the pond, livestock, and irrigation of the water spread **shorten** hold time and must be flagged on Form B (those days are excluded from MDWIR). Climate: 200 mm vs 600 mm provinces change **fill** more than **hold**; hold is local \(E\) and \(i\).

### 2.7 Checklist (design vs observed)

| If you want ~30–90 days from **full**, with no inflow | Then |
|--------------------------------------------------------|------|
| Mean depth 1.5–3 m | Survey \(V(h)\), \(A(h)\) |
| \(i\) roughly 10–40 mm d⁻¹ | Daily stage − \(E\); desilt if \(i\) falls toward \(E\) |
| Tight wall, drain closed | Masonry/earth, not an open gabion |
| Do not pump the pond if GW is the purpose | Form B pumped flag |
| Accept that summer \(E\) will eat a shallow pond | Prefer filling in winter/spring where possible |

---

## 3. Rainfall required to fill the dam to 100%

Filling is a **catchment yield** problem, not a pond problem. Direct rain on the water surface is usually tiny next to runoff from the hills.

### 3.1 Volume you must catch (the pond, not the catchment)

“100% full” is **water at the crest of that check dam** (height typically **2–6 m**). It is **not** flooding 100% of the catchment. Measure \(V_{\mathrm{crest}}=V(H_{\mathrm{crest}})\) in ArcGIS from the DEM (Surface Volume / Storage Capacity) or by tape; SOP: `docs/ARCGIS_STORAGE_FROM_DEM.md`.

\[
V_{\mathrm{need}}=V_{\mathrm{crest}}-V_{\mathrm{now}}+V_{\mathrm{loss,during fill}}
\]

\(V_{\mathrm{loss,during fill}}\) is infiltration + evaporation + wall leakage **while the storm is filling the pond**. For a short intense storm it is often 5–20% of \(V_{\mathrm{crest}}\); for a slow snowmelt fill it can be large (the pond never reaches 100% even though a lot of water entered). Conservative design: multiply \(V_{\mathrm{crest}}\) by **1.1–1.2**.

Transmission loss in the wadi **above** the dam (Lane-type infiltration in the channel) never arrives. In arid gravel streams this can be a large fraction of flood volume (Cyprus Peristerona; Oman). If the dam sits far down a sandy wadi, increase \(V_{\mathrm{need}}\) or shrink the **effective** catchment.

### 3.2 Method A — constant runoff coefficient (first look)

\[
P_{\mathrm{fill}}=\frac{V_{\mathrm{need}}}{C\,A_c}
\]

\(A_c\) = catchment area (m²), \(C\) = runoff coefficient (0–1), \(P_{\mathrm{fill}}\) in metres (×1000 → mm).

Equivalent: required **runoff depth** \(Q_{\mathrm{mm}}=V_{\mathrm{need}}/A_c\times 1000\), then \(P=Q/C\).

**Typical \(C\) (order of magnitude, not a substitute for local storms):**

| Surface | Gentle storm | Intense burst on dry hills |
|---------|--------------|----------------------------|
| Bare / rocky mountain | 0.15–0.30 | 0.35–0.55 |
| Sparse rangeland | 0.08–0.20 | 0.20–0.40 |
| Agriculture / soil | 0.05–0.15 | 0.15–0.30 |
| Forest / dense shrub | 0.05–0.12 | 0.10–0.20 |

FAO water-harvesting tables and the Rational-method \(C\) tables (used with \(Q=CIA/360\) for **peak**, not volume) are starting points. **Seasonal** \(C\) in drylands is often **0.05–0.15**; a **single cloudburst** can be much higher. Do not use annual rainfall × a high \(C\) — that overstates fill.

### 3.3 Method B — SCS / NRCS curve number (recommended)

Storm rainfall \(P\) (mm) produces runoff depth (mm):

\[
S=\frac{25400}{\mathrm{CN}}-254,\quad I_a=\lambda S\quad(\lambda=0.2\ \mathrm{standard};\ 0.05\ \mathrm{often\ better\ in\ arid\ lands})
\]

\[
Q=\frac{(P-I_a)^2}{P-I_a+S}\quad\text{if }P>I_a;\quad else\ Q=0
\]

Invert for the rainfall that yields the \(Q\) you need:

\[
P_{\mathrm{fill}}=I_a+\frac{Q+\sqrt{Q^2+4QS}}{2}
\]

**This is the important arid-zone result:** many small showers **never fill the dam**, even if the seasonal total looks large, because each \(P < I_a\). A few **deep** storms do all the work. That matches Afghan hydrology (few rainy days, intense events) better than a constant \(C\).

**CN (Antecedent runoff condition II, as a start):** rocky/poor rangeland often **70–85**; fair pasture **60–75**; after a wet spell CN rises (ARC III). Hawkins and others argue \(\lambda=0.05\) in drylands — report both.

### 3.4 Method C — several storms (how 100% is actually reached)

Number the storms in the wet season. After each event \(j\):

\[
V_{j}=\min\bigl(V_{\mathrm{crest}},\ V_{j-1}+C_j P_j A_c - L_j\bigr)
\]

100% fill is the first \(j\) with \(V_j=V_{\mathrm{crest}}\). \(C_j\) rises after the catchment wets. The **seasonal rainfall** to first spill is therefore **not unique**; it depends on the **hyetograph**. Report:

1. **Single-storm \(P_{\mathrm{fill}}\)** from Method B (design storm, dry start).
2. **Observed** date of first spill from Form B (truth).
3. **Catchment rain between empty and first spill** from the village gauge.

### 3.5 Worked example (numbers you can reuse)

Take \(V_{\mathrm{crest}}=20\,000\) m³, \(A_c=200\) ha \(=2.0\times10^6\) m², start empty, 15% extra for fill-period losses → \(V_{\mathrm{need}}=23\,000\) m³.

Required runoff depth \(Q=23\,000/2.0\times10^6\times1000=11.5\) mm.

| Method | Assumption | Rainfall to reach 100% |
|--------|------------|-------------------------|
| Constant \(C\) | \(C=0.12\) | \(P=11.5/0.12\approx 96\) mm in **one** storm |
| Constant \(C\) | \(C=0.25\) (intense) | \(P\approx 46\) mm |
| SCS CN 70, \(\lambda=0.2\) | \(S=109\) mm, \(I_a=22\) mm | \(P\approx 63\) mm |
| SCS CN 80, \(\lambda=0.2\) | \(S=64\) mm, \(I_a=13\) mm | \(P\approx 43\) mm |
| Ten showers of 10 mm | Each \(P<I_a\) for CN 70 | **Never fills** |

Capacity expressed as depth on the catchment is \(V/A_c=10\) mm here. Dashora (webinar summary of the Rajasthan set) found **capacity / catchment ≈ 8–59 mm** (mean ~16 mm): same order. If your dam is **tiny** on a **huge** catchment, it will fill (and spill) often; I2 will be high. If capacity / catchment is **>40–50 mm** in a 200–350 mm climate, it may **rarely** reach 100%.

### 3.6 Peak flow is a different calculation

Spillway **size** uses a peak formula (Rational \(Q=CIA/360\), or a regional flood). That does **not** tell you whether the **volume** fills the pond. Use CN or a rainfall–runoff model for volume; use Rational/unit hydrograph for the weir.

---

## 4. What we change in the assessment (relative to the hours-only story)

| Topic | Hours-detention (Annex A) | 1–3 month rainfall-fed pond (this note) |
|-------|---------------------------|----------------------------------------|
| Core pond log | Form E per flood | **Daily Form B** (07:00 stage + rain) |
| Evaporation | Almost ignore | **Must** subtract; compute \(I/E\) |
| I1 / I3 / MDWIR | Optional if logger exists | **Primary pond KPIs** (Dashora) |
| I2 fillings/year | Weak KPI | Meaningful |
| Days with water | Hours | **Design check:** median hold after last inflow vs 30–90 days |
| I4 / I5 | Still required | **Still required** (control wells and karez) |
| WaPOR | Cannot see hours | Can inform **regional \(E\) demand** over months; still **not** water table |
| Closest literature | Arizona leaky weirs, Tigray, Oman dry dams | **Dashora/MARVI, CGWB percolation tanks, Gujarat daily WB** |

I4/I5 do not go away: a pond that holds 90 days can still evaporate or sit on a sealed bed. Balochistan showed that.

---

## 5. Strong references (cite these)

**Water balance, hold time, infiltration vs evaporation**

- Dashora Y. et al. (2018). *A simple method to quantify the impact of check dams on water resources*. IAH MAR / *Sustainable Water Resources Management*. Farmer daily stage; MDWIR **18–57 mm d⁻¹**; recharge **1–2 × capacity** in two years; \(I/E\) **5–8**.
- Dashora Y. et al. (2019). *Hydrologic and cost-benefit analysis… Rajasthan*. **Hydrogeology Journal**. Three years; spill vs recharge vs \(E\); MDWIR **10–57 mm d⁻¹** (mean 27).
- Sukhija B.S. et al. (1997). *Evaluation of groundwater resources…* (and related NGRI check-dam papers). Rule of thumb: stage drop **>2 cm d⁻¹** ⇒ still infiltrating vs evaporation.
- Mozzi G. et al. (2021). *Hydrologic assessment of check dam performances in semi-arid areas: Gujarat*. **Frontiers in Water** 3:628955. Daily WB; SCS-CN inflow; Penman \(E\); KPIs: infiltration rate, fraction of runoff captured, **\(I/E\)**, **fillings per year**, **days stored**.
- Djuma H. et al. (2017). *The impact of a check dam on groundwater recharge and sedimentation in an ephemeral stream*. **Water** 9:813. Cyprus; daily \(Q_r=Q_{\mathrm{in}}-Q_{\mathrm{out}}-E+\Delta V\); ~30% of streamflow recharged.
- Martín-Rosales W. et al. (2007). *Estimating groundwater recharge from ephemeral streams in south-eastern Spain*. Check-dam recharge **6–53%** of inflow.

**Design manuals (rainfall, catchment, 2–3 month recharge window)**

- CGWB (2007). *Manual on Artificial Recharge of Ground Water*. Percolation tanks / check dams; **extend recharge ~three months** after monsoon; source-water assessment from rainfall frequency and non-committed runoff.
- USDA-NRCS. *National Engineering Handbook*, Part 630, Hydrology (curve number). Standard \(P\)–\(Q\) method; document \(\lambda=0.2\) vs 0.05.
- Critchley W., Siegert K. (1991). *Water Harvesting*. FAO. Catchment:cultivated ratios and runoff coefficients for drylands.
- Strange W.L. *Runoff tables* (classic Indian irrigation). Still used in South Asia for rainfall-to-runoff volume; treat as empirical, not physics.

**Silt, wall type, and why hold time changes over years**

- Al-Maktoumi et al. / Oman recharge-dam studies: silt → storage loss and **order-of-magnitude** drop in \(K\).
- Alderwish A.M. (2010). Sana’a basin cascade check dams.
- Kahlown M.A., Abdullah M. (2004). Balochistan gabions / delay-action vs leaky dams (evaporation if the bed seals).

**SCS-CN in check-dam studies**

- Mozzi et al. (2021), above; many Indian GIS siting papers use CN + Strange for **volume** and Rational for **peak** (e.g. J. Earth Syst. Sci. siting work, 2009).

Do not cite WaPOR IGwA (monthly Thornthwaite–Mather) as the method to fill or empty **this** pond. Use it only as basin \(P\)/ET context (`docs/WAPOR_SUITABILITY.md`).
