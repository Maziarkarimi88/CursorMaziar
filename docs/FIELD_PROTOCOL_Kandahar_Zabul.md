# Field protocol: groundwater impact of small check dams

**Setting:** rainfall-fed check dams on wadis and fans, Afghanistan (worked example: Kandahar–Zabul)  
**Purpose:** quantify whether a constructed check dam recharges the aquifer that supplies nearby wells and karez  
**Design hold:** when the pond is full, water is intended to remain about **1–3 months** (not a few hours)  
**Effort:** one trained village observer + one technician visit per month; about 1–2% of typical check-dam construction cost  
**Duration:** one full wet–dry cycle is useful; two years are needed before claiming a result  
**Method source:** daily pond water balance (Dashora / MARVI, Rajasthan) + water-table fluctuation and karez discharge (Sharda; Afghan karez practice)

Print this protocol (about six pages) with `docs/STORAGE_DURATION_AND_FILLING.md` (what controls 1–3 month hold; rainfall to fill the **pond** to crest). Get \(A(h), V(h)\) from DEM in ArcGIS (`docs/ARCGIS_STORAGE_FROM_DEM.md`) or tape. Use **Annex A** and Form E only if a structure actually empties in **hours** (gabion / leaky outlier). Daily **Form B** is the default pond log. Enter numbers in `templates/CheckDam_Recharge_Calculator.xlsx` (sheet `FillAndHold` for rainfall-to-fill and hold time). FAO **WaPOR** is **not** a substitute for I4/I5; see `docs/WAPOR_SUITABILITY.md`.

---

## 1. What this protocol does and does not measure

Check dams on Kandahar–Zabul fans slow snowmelt and storm floods as they leave the hills and spread onto coarse Quaternary gravels. Those gravels are the same deposits that feed karez (*sarchah* / mother well up-fan, *owkura* / outlet at the village). Local rainfall is only about 200–350 mm/year; most recharge historically comes from wadi infiltration, not from rain on the fan surface.

This protocol produces **five numbers** per dam per year:

| ID | Indicator | Why it matters |
|----|-----------|----------------|
| I1 | Annual infiltration volume (m³) | Water that left the pond into the ground |
| I2 | Fillings per year (I1 / storage capacity) | Efficiency of the structure |
| I3 | Mean dry-weather infiltration rate, MDWIR (mm/day) | Health of the pond bed; trigger for desilting |
| I4 | Extra water-table rise versus control (m) | Whether wells actually received the water |
| I5 | Extra karez-flow days and mean discharge (L/s) | Whether the karez, not only nearby tubewells, benefited |

It does **not** estimate basin-wide groundwater recovery, downstream flow taken from the next village, or water quality beyond a simple EC screen. Influence of one small dam is expected within hundreds of metres to about 1.5–2 km down-fan (Indian and Spanish check-dam studies). UNDP community reports of wells recovering (for example Inzergai / Loy Kariz) should be treated as hypotheses until I4 and I5 are measured against a control.

Two quantities must not be confused:

- **I1** is water leaving the pond (potential recharge).
- **I4 / I5** are water arriving in the used aquifer. They can be smaller if silt clogs the bed, if water is stranded in the unsaturated zone, or if new pumps intercept the mound (Massuel et al. found most percolated water pumped locally).

---

## 2. Site selection and sampling layout

Work on **one treated wadi–fan unit** and **one control**. A cascade of two or three low dams (2–4 m) on the same wadi is better than one high dam on a small catchment (Alderwish, Sana’a Basin). Monitor each pond, and interpret them as a chain: upstream dams reduce inflow to downstream ones.

**Treated unit**

1. Check dam on the ephemeral wadi at or just above the **fan apex**, where bed material is coarse gravel/sand, not silt or bare bedrock.
2. Village wells and at least one karez whose *sarchah* lies down-fan of the pond, or whose gallery crosses the wadi seepage zone.
3. Access for an observer on the morning after floods.

**Control unit**

An adjacent fan or tributary of similar size, geology and pumping, with **no check dam**, at least 2 km laterally from the treated pond. If no such fan exists, use wells **up-wadi of the dam** (above backwater) plus wells far on the fan flank. Do not use down-fan wells as controls.

**Points to install or adopt** (see `figures/sampling_layout.png`):

| Code | What | Where | Count |
|------|------|-------|-------|
| SG | Staff gauge | Pond abutment / spillway wall | 1 per dam |
| RG | Rain gauge | Open village compound, ~1 km from dam | 1 |
| BM | Benchmark pin | Concrete near gauge | 1 |
| W-N | Near wells | Both banks, 0–200 m from waterline at full supply | 2–3 |
| W-M | Mid wells | 200–800 m down-fan along the wadi or karez line | 2–3 |
| W-F | Far wells | 800–1,500 m down-fan | 1–2 |
| C | Control wells | Untreated fan or up-wadi / flank | 2–3 |
| KS | Karez *sarchah* | Mother well water level | 1 per karez |
| KO | Karez *owkura* | Outlet discharge | 1 per karez |
| SP | Sediment probes | Empty pond bed, marked grid | 5–9 |

Prefer **existing dug wells and karez shafts** over new piezometers. New holes are justified only if no well exists within a ring. Mark a painted triangle on the well rim as the measuring point; record rim height above ground.

If DACAAR or MEW already have a monitoring well in the district, copy its monthly reading as **regional background**. That well is not a local control; it shows the provincial trend against which local recovery is judged.

---

## 3. Equipment and gauge specifications

Buy locally. Nothing here requires a logger, though one pressure transducer in the pond is a useful backup if winter access is unreliable.

### 3.1 Staff gauge (SG)

- **Location:** vertical face of the spillway abutment or a timber/aluminium board bolted to the wing wall, in still water, not in the overflow nappe.
- **Datum:** gauge zero = lowest point of the pond bed, surveyed once. Record crest elevation on the same gauge (for example crest = 2.50 m). Write both values on Form A.
- **Range:** bed to crest + 0.50 m.
- **Graduation:** 1 cm minor ticks; 5 cm medium; 10 cm major ticks in red. Numerals every 10 cm. Paint black on white masonry, or use an enamelled plate.
- **Benchmark:** 12–16 mm steel pin in a 30 cm concrete block, away from scour. Level from BM to gauge zero with a hand level or dumpy. Recheck after the first large flood.
- **Reading:** nearest 1 cm, at **07:00** local time, while water is in the pond. Take a phone photo of the gauge with date stamp (MARVI quality-control method).
- **Do not** move the board or repaint zero without a new survey.

### 3.2 Rain gauge (RG)

- Ordinary cylinder, **100–203 mm** internal diameter (standard 8-inch gauge preferred).
- Rim **1.0 m** above ground, vertical, in an open yard. No tree, wall or building within a distance of **twice the object height**.
- Resolution **0.5 mm**. Read and empty at 07:00. If a storm is still falling, read, empty, and add a second reading the same day.
- If CHIRPS or a district station exists, still keep the village gauge; flash-flood catchments here are small and storms are local.

### 3.3 Area–volume of the **pond** (DEM or tape)

You need storage **behind the wall** at each water height up to **that dam’s crest (2–6 m)**. This is **not** the volume of the catchment.

**Preferred office method:** ArcGIS **Surface Volume** (3D Analyst, plane **Below**) or **Storage Capacity** (Spatial Analyst) on a DEM, with the dam wall burned in and a **pond zone** polygon. Step height 0.5 m from bed to crest. Full SOP: `docs/ARCGIS_STORAGE_FROM_DEM.md`.

**Field check:** empty-pond tape and hand level at 0.25–0.50 m intervals, or at least one cross-section at the wall to test GIS width.

Volume between contours (if you only have areas):

\[
V_{i,i+1} = \frac{h_{i+1}-h_i}{2}\,(A_i + A_{i+1})
\]

Enter the table on sheet `StageAreaVolume`. **100% full** = the row at crest height. Rainfall-to-fill uses this \(V_{\mathrm{crest}}\) and catchment **runoff**, not catchment volume.

### 3.4 Wells and karez

- **50 m** fibreglass tape and a **15 cm** wooden or plastic float (MARVI). Chalked steel tape is acceptable.
- Read depth to water from the painted rim mark to **1 cm**.
- **EC meter**, 0–20 mS/cm, calibrated weekly with 1,413 µS/cm standard. Measure pond, W-N, W-M, KS and KO on the same visit. Pond water is usually fresher than regional groundwater; wells that mix toward pond EC are in the benefited zone.
- **Karez discharge at KO:** 10–20 L jerrycan and stopwatch if Q is small; otherwise a board with a rectangular notch, or float–area in the canal. Always at the same hour. Do not measure inside the tunnel.

### 3.5 Evaporation

If a Class A pan exists (Kandahar airport or a farm), use **0.70 × pan** as open-water evaporation. If not, use the workbook defaults for Kandahar open water (about 2.5 mm/day in January to 9.5 mm/day in July). A village pan is optional.

---

## 4. What to measure and when

Start daily pond readings on the **first day water stands in the pond**, including winter–spring snowmelt floods, not only summer storms.

| Task | Frequency | Who | Form |
|------|-----------|-----|------|
| Pond stage + photo | Daily while ponded; skip when empty | Observer | B |
| Rainfall | Daily at 07:00 | Observer | B |
| Overflow (yes/no, and stage if above crest) | Each day ponded | Observer | B |
| Near wells (W-N) and *sarchah* | Daily while ponded; weekly otherwise | Observer | C |
| Mid, far, control wells | Weekly | Observer | C |
| Karez outlet discharge | Weekly; daily while ponded if flowing | Observer | C |
| EC (pond, 3 wells, karez) | Monthly, and once after each filling | Technician | C |
| Pumping / new wells / irrigated area | Monthly note | Observer | C |
| Sediment grid | Once in late summer when pond is dry | Technician | D |
| Gauge and BM check | After first large flood, then annually | Technician | A |

**Quality control (from MARVI):** each monthly visit, the technician re-measures **one in ten** wells at random and compares the gauge photo with the written stage. Differences >2 cm for stage or >5 cm for wells are flagged and the observer is retrained. Do not discard the original value; mark it `Q` in the workbook.

Record pumping. If families drill new wells after the dam (as in the Rawalpindi small-dam study), the water table may fall even while I1 is large. Note hours of pumping or a simple count of running pumps on the visit day.

---

## 5. Calculations (do these in the workbook)

### 5.1 Pond infiltration — primary volume (I1, I2, I3)

Let \(h_t\) be morning stage, \(A(h)\) and \(V(h)\) from the survey, \(E_t\) evaporation depth, \(P_t\) rainfall on the pond.

**Dry day** (no rain, stage below crest):

\[
\text{Infiltration volume}_t = \bigl[V(h_{t-1}) - V(h_t)\bigr] - E_t \cdot A_{\text{avg}}
\]

\[
A_{\text{avg}} = \tfrac12\bigl(A(h_{t-1})+A(h_t)\bigr),\quad
\text{MDWIR}_t = \frac{\text{Infiltration volume}_t}{A_{\text{avg}}}
\]

MDWIR is a depth per day. Annual I1 is the sum of daily infiltration volumes for all days with water in the pond.

**Wet day** (rain, or stage rising): do not use the drop in stage. Apply the **mean dry-weather MDWIR for that filling** to that day’s \(A_{\text{avg}}\):

\[
\text{Infiltration volume}_t = \text{MDWIR}_{\text{mean}} \cdot A_{\text{avg}}
\]

This is the Dashora shortcut. It avoids estimating flood inflow. Days above crest are the same: infiltration continues at MDWIR; spill is noted but not required for I1.

**Reject a dry-day MDWIR** if someone pumped from the pond, if a boat wake or ice is noted, or if the photo does not match the written stage.

**I2** = I1 / volume at crest.  
**I3** = mean of accepted dry-day MDWIR values for the year.

Healthy unclogged gravel beds in comparable climates infiltrate several times evaporation (Rajasthan check dams: MDWIR about 5–8 × E). If I3 falls to near E, the pond is evaporating, not recharging — desilt.

### 5.2 Water-table fluctuation — corroboration (I4)

For each well, seasonal rise \(\Delta h\) = highest post-flood water level minus pre-flood water level (use elevation, not depth, so rim height cancels).

\[
\Delta h_{\text{extra}} = \text{mean }\Delta h\text{ of W-N and W-M} - \text{mean }\Delta h\text{ of control wells}
\]

\[
\text{Recharge depth} \approx S_y \cdot \Delta h_{\text{extra}}
\]

Use **\(S_y = 0.10\)** as the default for Kandahar–Zabul fan gravels (value used in Afghan karez modelling). Report a range with \(S_y = 0.08\) and \(0.15\). Do not convert this depth to a volume unless you have mapped the mound; I1 remains the volume number.

If W-N rises and control does not, the dam is the likely cause. If all wells rise together, it was a wet year, not the dam.

### 5.3 Karez (I5)

Count days with measurable flow at KO. Extra flow days = treated karez days − control karez days (or versus the previous year if no control karez exists — mark as weaker evidence). Mean discharge is the average of weekly KO measurements while flowing.

A rise at *sarchah* with no extra outlet days means the tunnel is no longer in contact with the water table, or the gallery is collapsed. That is a maintenance finding, not a recharge failure.

### 5.4 EC screen

If a well’s EC moves toward pond EC after filling, and control EC does not, that well is in the mixing zone. This is a presence/absence test, not a volume. Typical benefited distance in analogous check-dam studies is 0.5–1.5 km.

---

## 6. Scorecard and decisions

Fill the annual scorecard (workbook sheet `Scorecard` and Form D). Use it in the watershed committee meeting before the next flood season.

| Result | Meaning | Action |
|--------|---------|--------|
| I3 ≥ 4 × E, I4 > 0.3 m vs control, I5 up | Dam is working | Maintain spillway; plan manual desilting when I3 drops |
| I3 high, I4 and I5 near zero | Water not reaching used aquifer | Check unsaturated-zone lag next year; look for new pumps; confirm karez is not clogged |
| I3 ≈ E or falling year on year | Bed clogged or water table drowning the pond | **Manual** desilting of the pond floor (Rajasthan: manual scraping raised recharge; machine scraping compacted the bed and reduced it) |
| I4 only in W-N, none in W-M/W-F | Very local mound | Do not promise village-wide recovery; consider a second dam further down-wadi only after this protocol is repeated |
| Upstream new dams, downstream I1 falls | Cascade intercept | Monitor the chain; Dashora (2022) showed extra upstream capacity can starve downstream ponds |

Do not add dams until two seasons of this protocol exist for the first one. Optimum cascade capacity is an economic question; the workbook at least shows whether the next dam is still infiltrating.

---

## 7. Roles, ethics, and data

- **Observer** (village, literate, present in the wet season): Forms B and C. Stipend should be enough to keep the person through the second year (MARVI’s main failure mode was unpaid volunteers).
- **Technician** (NGO / MEW / DACAAR): Form A survey, monthly QA, EC, sediment, workbook.
- **Community meeting:** after each wet season, read I1–I5 in cubic metres and in extra karez days — not in model jargon.

Data ownership stays with the community and the implementing agency. Share copies with DACAAR/MEW if they request them for the national well network.

Safety: never enter a karez tunnel; never read the gauge in a rising flood; mark sediment probe points when the bed is dry and firm.

---

## 8. Two-year timetable

| Period | Work |
|--------|------|
| Month 0–1 | Map treated and control fans; Form A; train observer; baseline DTW and EC |
| First filling | Daily B; daily W-N and KS; weekly remainder |
| Late summer, pond dry | Form D sediment; compute I1–I5; community meeting |
| Year 2 | Repeat. Compare a wet and a dry year if possible. Decide desilting and any extra dam |

Minimum evidence to report to a donor: completed Forms A–D, the workbook `Summary` sheet, gauge photos, and the sampling map with well IDs.

---

## 9. References (methods this protocol copies)

- Dashora et al. (2018, 2019) and Dashora et al. (2022, *Water*) — farmer stage readings, dry-weather infiltration, cascade effects, Rajasthan (MARVI / IAH).
- Jadeja et al. (2018); IWMI GRIPP MARVI notes — village observers, tape-and-float, photo QA.
- Sharda et al. (2006, *J. Hydrol.*) — water-table fluctuation at recharge structures.
- Massuel et al. (2014, *J. Hydrol.*) — pond efficiency versus local pumping, hard-rock / semi-arid India.
- Djuma et al. (2017, *Water*) — check dam versus natural ephemeral channel, Cyprus.
- Alderwish (2010) — cascade of low dams versus one gravity dam, Sana’a Basin, Yemen.
- Martín-Rosales et al. (2007) — recharge share 6–53% of inflow, SE Spain.
- Parimalarenganayaki and Elango — benefited wells typically within ~1.5 km of a check dam, Tamil Nadu.
- Macpherson et al. (2015, *Appl. Water Sci.*) — Afghan karez geometry (*sarchah* to ~20 m, gallery ~1–2 km).
- Uhl and Tahiri (2003) — Kandahar–Zabul fan aquifers; recharge dominated by wadi infiltration of snowmelt.
- DACAAR groundwater network — monthly background wells; do not replace local controls.
- UNDP / DRC Kandahar–Spin Boldak check-dam notes — community-reported well recovery; this protocol is the measurement layer those projects lacked.
