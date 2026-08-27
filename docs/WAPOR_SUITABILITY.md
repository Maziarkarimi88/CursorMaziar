# FAO WaPOR and groundwater: suitability for Kandahar–Zabul check dams

**Question:** can FAO **WaPOR** (Water Productivity through Open access of Remotely sensed derived data) replace or lead the groundwater assessment of small flood-control check dams on Kandahar–Zabul fans?

**Answer in one line:** **No as the primary method.** Use it only as **basin context** (rainfall, evapotranspiration, biomass). Proof that a dam wet the karez and wells remains **Form E + I4/I5** (treated vs control wadi after the same flood).

This note reviews what WaPOR actually measures, how published “groundwater” applications use it, and where that does and does not match this research.

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

Time: AETI is **10-day / monthly / annual**. PCP can be daily, but the ET side of a water balance is still dekad-scale. That cannot resolve **hours of detention**.

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

**What it cannot do for you:** Thornthwaite–Mather is a **vertical column** model at **monthly** steps. Focused recharge under a wadi or behind a check dam is **lateral, event-driven, and hours-to-days**. Monthly root-zone overflow will **miss** that pulse, or smear it into a pixel that is mostly dry fan.

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

Your design (protocol + Annex A):

- Dams are **flood/erosion** structures; water stands **hours**, not a monsoon tank.
- Groundwater is a **co-benefit**.
- Primary GW tests: **I4** extra well rise vs control after the **same flood**; **I5** extra karez-flow days.
- Influence expected **hundreds of metres to ~1.5–2 km**, on **alluvial-fan gravel** feeding *sarchah* / *owkura*.
- Rain **200–350 mm**; most recharge is **wadi transmission loss**, not rain on the fan.

| Requirement | WaPOR | Field protocol (I4/I5, Form E) |
|-------------|-------|--------------------------------|
| Detect hours of ponding | No (dekad ET) | Yes (staff, camera, logger, Form E) |
| Focused wadi-bed infiltration | No (root-zone / pixel ET) | Yes (falling-limb volume, I1 if logged) |
| Treated vs control fan | 300 m pixels mix both | Yes (adjacent untreated wadi) |
| Well mound (I4) | No water-table layer | Yes |
| Karez days / L/s (I5) | No | Yes |
| Silt sealing the bed | No (except maybe long-term biomass drop if irrigation fails) | Yes (Form D / sediment grid) |
| Peak-cut / lag (primary purpose) | No | Yes (upstream–downstream stage) |
| Annual basin P and ET context | **Yes** | Rain gauge is local only |
| Multi-year greening of karez command | **Maybe** (NPP/AETI, noisy) | I5 + farmer interviews |
| Cost | Free | Low, but needs observers |

**Process mismatch (the important one):**  
WaPOR-based recharge = *rainfall minus ET minus change in soil moisture in a 300 m column*.  
Your recharge = *flood water held for hours on gravel, leaking through a gabion or soaking the wadi*, then moving **down-fan** to wells and karez. Those are different hydrologic pathways. A pixel that is 90% dry gravel and 10% wetted channel will report almost no extra ET after a flood that emptied overnight.

---

## 5. Verdict for *this* research

**Do not use WaPOR to decide whether a check dam recharged groundwater.**

It is the wrong variable (ET, not head), the wrong time step (10 days, not hours), the wrong spatial grain (300 m, not the wadi), the wrong process (diffuse root-zone vs focused channel MAR), and the wrong climate niche (arid skill is the weak case). Published “WaPOR groundwater” tools (IGwA, WA+) were built for **irrigation accounting and basin residuals** in partner countries with 100 m coverage — not for small delay-action / leaky dams on Afghan fans.

**You may still use WaPOR as a supporting layer**, if you keep it in its lane:

1. **Context maps** for a proposal or thesis chapter: 2018–present annual PCP and AETI over the Arghandab / Tarnak / surrounding basins; show that rain is low and ET already consumes most of it.
2. **Irrigated-area / biomass co-benefit** (optional, after 2+ years): extract AETI or NPP on the **karez command polygon** vs a control village. Treat any greening as a **hypothesis** until I4/I5 agree. A wet year will green both.
3. **Do not** run Thornthwaite–Mather IGwA on 300 m pixels and call the residual “check-dam recharge.”
4. **Do not** cite GRACE or WA+ storage change as evidence for one dam.

**Primary evidence remains:** Form E per flood, detention hours × wetted area, treated vs control wells (I4), karez *sarchah* / *owkura* (I5), silt scorecard. That is the same logic as Balochistan leaky dams, Tigray treated vs untreated gullies, Arizona leaky weirs, and Spanish rambla check dams — none of which used WaPOR as the groundwater proof.

---

## 6. If a reviewer asks “why not remote sensing?”

Suggested short reply:

> WaPOR is FAO’s ET and biomass product. It is free and useful for basin water consumption. It does not observe groundwater. At 300 m and 10-day steps it cannot see hours of ponding in a wadi a few tens of metres wide. Studies that estimate recharge from WaPOR use a monthly soil-column model (IGwA) or a basin residual (WA+); both miss focused flood recharge. We therefore measure the flood and the wells, and we may add WaPOR only as background ET/P.

---

## 7. Sources (starting set)

- FAO WaPOR portal and data pages; WaPOR v2/v3 database methodology (ETLook / FAO-56).
- FAO WaPOR data coverage: L1 global 300 m; L2 ~100 m Africa–Near East (box to ~65°E) plus listed extras; L3 20 m named schemes only (no Afghanistan; Yemen Sana’a discontinued).
- IHE Delft / FAO IGwA: WaPOR AETI + PCP + soils → Thornthwaite–Mather recharge and irrigation abstraction (Jordan, Palestine; GEE).
- WA+ / WAPORWA applications: Nile, Awash, Niger, Jordan/Litani water accounts; green/blue ET split.
- FAO/IHE WaPOR quality assessments: AETI stronger for annual large areas; weaker seasonally and in arid zones; 100–250 m insufficient for small fields.
- This project: `docs/FIELD_PROTOCOL_Kandahar_Zabul.md`, `docs/ANNEX_A_Flood_Detention_Check_Dams.md`, `docs/COUNTRY_STORIES_AND_METHODS.md`.
