# FAO WaPOR and groundwater: suitability for Afghan rainfall-fed check dams

**Question:** can FAO **WaPOR** replace or lead the groundwater assessment of small check dams designed to hold a full pond about **1–3 months**, filled mostly by **rainfall runoff**?

**Answer in one line:** **No as the primary method.** Use it as **basin P / ET context** (and, if you wish, as a regional open-water evaporation demand). Proof that a dam recharged wells and karez remains **daily Form B + I4/I5** (treated vs control). Form E is only for structures that empty in hours.

This note reviews what WaPOR actually measures, how published “groundwater” applications use it, and where that does and does not match this research. Hold time and rainfall-to-fill: `docs/STORAGE_DURATION_AND_FILLING.md`.

---

## 1. What WaPOR is (and is not)

WaPOR is FAO’s operational satellite water-productivity portal. The processing chain (ETLook / FAO-56 Penman–Monteith family) estimates **how much water plants and soil consume**, not how deep the water table is.

| Layer (typical codes) | What it is | Typical time step |
|------------------------|------------|-------------------|
| **AETI** | Actual evapotranspiration + interception (E + T + I) | Dekad (10 days), month, year |
| **PCP** | Precipitation | Daily / dekad / month |
| **RET** | Reference ET | Daily / dekad |
| **NPP / TBP** | Net primary production / total biomass | Dekad / season |
| **LCC** | Land-cover class | Annual (coarser levels) |
| **RSM** | Relative root-zone soil moisture (modelled, not a well) | Dekad |
| **GBWP / NBWP** | Gross / net biomass water productivity | Season |

There is **no WaPOR water-table, well, karez, or aquifer-storage product**. Papers that mention “groundwater” **derive** recharge or pumping as a **residual** of a soil-water or basin account, using WaPOR P and ET plus extra soil or hydro models.

Portal: [data.apps.fao.org/wapor](https://data.apps.fao.org/wapor/). Methodology wiki and FAO WaPOR database methodology reports (v2 and v3).

---

## 2. Coverage over southern Afghanistan (practical constraint)

WaPOR has three spatial levels:

| Level | Pixel | Where | Kandahar–Zabul? |
|-------|-------|-------|-----------------|
| **L1 / v3 continental** | **~300 m** | **Global** (v3 from ~2018) | **Yes — this is what you can download** |
| **L2 national** | ~100 m | Africa, Near East, plus Pakistan, Sri Lanka, Colombia in v3 | **Unreliable / likely no.** Classic L2 box is about **30°W–65°E**. Kandahar city is ~**65.7°E**, Qalat (Zabul) ~**66.9°E**. Afghanistan is **not** on the L2 country list (that list includes Yemen, Jordan, Iraq, Syria, Lebanon, Egypt, … not Afghanistan). Pakistan L2 does not cover Afghan fans. |
| **L3 scheme** | ~20–30 m | Named irrigation schemes only | **No.** Afghanistan is not listed. Nearest analogue was **Yemen Sana’a basin** (pilot, production stopped). |

**Consequence:** any WaPOR map of your fans will be **300 m pixels** (~9 ha). A check-dam pond, wetted wadi strip, and karez command area are usually **smaller than one pixel**, or mixed with bare gravel, village, and rainfed plots in the same cell.

Time: AETI is **10-day / monthly / annual**. PCP can be daily. A 1–3 month pond is long enough that **dekadal ET is in the right time family for evaporation demand**, but WaPOR still does not observe stage, infiltration, or the water table. It cannot resolve **hours** of detention on gabion outliers.

Arid-zone quality: FAO/IHE quality assessments report that WaPOR AETI is more defensible for **annual totals over large irrigated areas**. Seasonal AETI is often **underestimated (order 20–60%)**. Skill is **weaker in hyper-arid / arid** landscapes (Egypt, similar dry belts) than in humid cropland. 100–250 m pixels already struggle with small fields; 300 m is coarser still.

---

## 3. How researchers turned WaPOR into “groundwater” products

These are the main published pathways. None of them measure a check-dam mound.

### 3.1 IGwA — Incremental Groundwater Assessment (IHE Delft / FAO)

**Where used:** Jordan and Palestine (on-the-job training with national agencies); Google Earth Engine app.

**Recipe:**

1. WaPOR **AETI** and **PCP** (monthly).
2. Soil texture from OpenLandMap (or similar).
3. Convert texture to water-holding parameters (Saxton–Rawls).
4. Run a **Thornthwaite–Mather** monthly **root-zone** water balance.
5. Map **recharge** (when the root zone overflows) and **irrigation groundwater abstraction** (when ET exceeds rain + soil store, attributed to irrigation).

**What it is good at:** regional maps of **diffuse** recharge and of **irrigation pumping** where crops are green and fields are large enough for 100 m pixels.

**What it cannot do for you:** Thornthwaite–Mather is a **vertical column** model at **monthly** steps. Focused recharge under a wadi or through a check-dam bed is **lateral and event-fed**, then a **weeks-to-months** pond. Monthly root-zone overflow on a 300 m fan pixel will **smear** that signal into dry gravel.

### 3.2 WA+ / WAPORWA / PixSWAB — basin water accounting

**Where used:** Nile, Awash, Niger, Litani, Jordan, Amman–Zarqa, and other WaPOR partner basins.

**Recipe:** split WaPOR ET into **green** (from rain) and **blue** (from irrigation / surface water); close a basin account (P, ET, outflow, change in storage). Runoff and percolation are **modelled closures**, not gauged infiltration. Some studies add **GRACE** for large-scale groundwater storage change.

**What it is good at:** a **donor chapter** on “the basin consumes X km³, agriculture is Y% of ET.”

**What it cannot do for you:** GRACE pixels are **hundreds of kilometres**. A check-dam influence is **hundreds of metres to ~2 km**. WA+ residuals mix climate, land cover, pumping, and model error. They will not isolate one dam versus the next wadi.

### 3.3 Irrigation and biomass as a *proxy* for recovered water

Some WaPOR applications (and similar ET products) show **greening / higher AETI / biomass** after water-harvesting or after wells recover. That is a **livelihood co-benefit** signal: more irrigation ET because more water was available to pump or to karez.

**What it is good at:** after several seasons, a village command area that stayed green longer.

**What it cannot do for you:** extra ET can come from **new tubewells**, diverted flood irrigation, or a wet year. It does not prove the check dam recharged the aquifer. Arizona leaky weirs (see `docs/COUNTRY_STORIES_AND_METHODS.md`) wet **shallow alluvium** while deep groundwater stayed old mountain-block water — satellite ET would see the meadow, not the aquifer.

### 3.4 Related remote-sensing GW work that is *not* WaPOR

Do not confuse WaPOR with:

| Product | Scale | Use here |
|---------|-------|----------|
| **GRACE / GRACE-FO** | ~300 km | Provincial drought narrative only |
| **InSAR** | tens of m | Subsidence from **over-pumping**, not recharge from a small dam |
| **Soil-moisture satellites** (SMAP, etc.) | km-scale | Surface wetness, not karez |
| **High-res ET** (OpenET, EEFlux, 20–30 m if you commission it) | field | Still ET, still not wells; L3 WaPOR does not exist for Afghanistan |

---

## 4. Match against what this research is trying to measure

Your design (protocol + `docs/STORAGE_DURATION_AND_FILLING.md`):

- Dams are **rainfall-fed**; when full they are meant to hold about **1–3 months**.
- Groundwater is a **design purpose**, not only a flood co-benefit.
- Primary pond tests: daily Form B → **I1, I2, I3**, days stored, \(I/E\).
- Primary GW tests: **I4** extra well rise vs control; **I5** extra karez-flow days.
- Influence expected **hundreds of metres to ~1.5–2 km**, feeding *sarchah* / *owkura*.
- Rain often **200–350 mm** in the south (higher in some provinces); fill depends on **storm depth vs curve number**, not annual rain alone.

| Requirement | WaPOR | Field protocol |
|-------------|-------|----------------|
| 1–3 month pond still there | Dekadal ET sees **demand**, not stage | Daily Form B |
| Rainfall to fill 100% | PCP is a **regional** rain field | Village gauge + SCS-CN on `FillAndHold` |
| Bed infiltration I1/I3 | No | Dry-day stage drop − \(E\) |
| Treated vs control fan | 300 m pixels mix both | Adjacent untreated wadi |
| Well mound (I4) | No water-table layer | Yes |
| Karez days / L/s (I5) | No | Yes |
| Silt sealing the bed | No | Form D / sediment grid |
| Annual basin P and ET context | **Yes** | Rain gauge is local only |
| Open-water \(E\) order of magnitude | RET helps | Pan × 0.7 still better on site |
| Hours-only gabion outlier | Cannot see | Annex A / Form E |

**Process mismatch (the important one):**  
WaPOR-based recharge = *rainfall minus ET minus change in soil moisture in a 300 m column*.  
Your recharge = *runoff stored in the pond for weeks–months, then infiltrated through the bed*, moving **down-fan** to wells and karez. A 300 m pixel is still mostly dry fan. Dekadal AETI will not replace a staff gauge.

---

## 5. Verdict for *this* research

**Do not use WaPOR to decide whether a check dam recharged groundwater.**

It is the wrong variable (ET, not head), the wrong spatial grain (300 m, not the pond), the wrong process (diffuse root-zone vs focused pond MAR), and a weak climate niche (arid AETI). IGwA / WA+ remain irrigation-accounting tools.

A 1–3 month pond **does** make WaPOR **slightly more useful than for hour-scale detention**: RET and PCP can sit beside your pan and rain gauge as **context**. They still do not measure I4/I5.

**You may still use WaPOR as a supporting layer**, if you keep it in its lane:

1. **Context maps** for a proposal or thesis chapter: 2018–present annual PCP and AETI over the basin; show that rain is low and ET already consumes most of it.
2. **Irrigated-area / biomass co-benefit** (optional, after 2+ years): extract AETI or NPP on the **karez command polygon** vs a control village. Treat any greening as a **hypothesis** until I4/I5 agree. A wet year will green both.
3. **Do not** run Thornthwaite–Mather IGwA on 300 m pixels and call the residual “check-dam recharge.”
4. **Do not** cite GRACE or WA+ storage change as evidence for one dam.

**Primary evidence remains:** daily Form B, I1–I3 and \(I/E\), treated vs control wells (I4), karez *sarchah* / *owkura* (I5), silt scorecard. That is Dashora/MARVI plus a control fan. Annex A/Form E only if the dam fails to hold weeks.

---

## 6. If a reviewer asks “why not remote sensing?”

Suggested short reply:

> WaPOR is FAO’s ET and biomass product. It is free and useful for basin water consumption and as a check on evaporation demand while a pond sits for 1–3 months. It does not observe groundwater or pond stage. At 300 m it cannot isolate a small check dam from the dry fan. Studies that estimate recharge from WaPOR use a monthly soil-column model (IGwA) or a basin residual (WA+); both miss pond-bed infiltration. We therefore measure the pond and the wells, and we may add WaPOR only as background ET/P.

---

## 7. Sources (starting set)

- FAO WaPOR portal and data pages; WaPOR v2/v3 database methodology (ETLook / FAO-56).
- FAO WaPOR data coverage: L1 global 300 m; L2 ~100 m Africa–Near East (box to ~65°E) plus listed extras; L3 20 m named schemes only (no Afghanistan; Yemen Sana’a discontinued).
- IHE Delft / FAO IGwA: WaPOR AETI + PCP + soils → Thornthwaite–Mather recharge and irrigation abstraction (Jordan, Palestine; GEE).
- WA+ / WAPORWA applications: Nile, Awash, Niger, Jordan/Litani water accounts; green/blue ET split.
- FAO/IHE WaPOR quality assessments: AETI stronger for annual large areas; weaker seasonally and in arid zones; 100–250 m insufficient for small fields.
- This project: `docs/FIELD_PROTOCOL_Kandahar_Zabul.md`, `docs/STORAGE_DURATION_AND_FILLING.md`, `docs/ANNEX_A_Flood_Detention_Check_Dams.md`, `docs/COUNTRY_STORIES_AND_METHODS.md`.
