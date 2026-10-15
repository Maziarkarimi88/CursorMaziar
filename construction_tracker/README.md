# Construction Works Scheme Tracker

Excel register for tracking construction schemes from design through handover. Each scheme is one row. Each pipeline step has its own date. The workbook then calculates:

- days taken to move from one step to the next
- days spent in the current step
- total days from the first dated step to the last
- whether the current step has exceeded its target days

Open **`WBK_AF2_Construction_Works_Tracker.xlsx`**.

## Sheets

| Sheet | Use |
| --- | --- |
| `00_How_to_Use` | How to fill the register and how to add or remove columns and domains |
| `01_Scheme_Tracker` | Working register — type here |
| `02_Dashboard` | Counts by status / region / intervention, average days per step |
| `03_Example_Filled` | Two worked examples so you can see the day-count formulas |
| `04_Status_Pipeline` | Ordered list of steps (edit spare slots to add a step) |
| `05_Domains` | Dropdown lists: intervention, donor, project, region, status |
| `06_Geography` | Province and district lists |
| `07_Lookups` | Maps region/province names onto those lists |

## Status pipeline (default)

1. Under Design
2. Under Review of WRI
3. Under LTO Review
4. ITB Launched
5. Under Technical Evaluation
6. Under Awarding
7. Awarded
8. Under Construction
9. Completed / Handover

Three spare slots sit after these. Type a name in a spare slot on `04_Status_Pipeline` and the matching date column on the tracker updates itself.

## How days are calculated

Enter the date a scheme **reached** each step (the day that step started / was achieved).

| Column | Rule |
| --- | --- |
| `Days: A → B` | Date of B minus the last previous filled date (so a skipped step still measures from the last real date) |
| `Days in current status` | `TODAY()` minus the latest filled status date |
| `Total days first → last step` | Last filled date minus first filled date |
| `Days over target this step` | Days in current status minus the target days on `04_Status_Pipeline` |
| `Current Status (auto)` | Name of the latest step that has a date; if no dates yet, uses Reported Status |
| `Awarded Date` | Copies `Date: Awarded` |
| `Planned End Date` | `EDATE(Awarded Date, Contract Duration months)` |

Grey cells are formulas. Do not type over them. White cells are inputs.

Negative day-counts mean a later step was dated earlier than a previous one — check the dates.

## Add or remove domains

**Intervention type, donor, project, region, status**

Type the new value in the first empty cell at the bottom of that column on `05_Domains`. Do not leave a blank cell in the middle of the list. Dropdowns expand automatically.

**District**

Type it under the province column on `06_Geography`.

**Province or a new region**

Add the name on `06_Geography`, add a matching row on `07_Lookups`, and create the `Prov_` / `Dist_` named range (Formulas → Name Manager). The reliable way is to edit `GEOGRAPHY` in `tracker_config.py` and regenerate.

## Add or remove status steps or columns

**Add a step at the end** — type the name in a spare slot on `04_Status_Pipeline`. No script needed.

**Insert a step in the middle, remove a step, or add a permanent extra column** (GPS, engineer, photo link, …) — edit `tracker_config.py` (`STATUS_PIPELINE`, `IDENTITY_COLUMNS`, or `CONTRACT_COLUMNS`) and run:

```bash
pip install -r construction_tracker/requirements.txt
python3 construction_tracker/generate_tracker.py
```

Copy any dates you already typed into a backup first; regenerating replaces the workbook file.

Hide columns you do not need rather than deleting formula columns.

## Pre-loaded schemes

`01_Scheme_Tracker` already lists the WBK/AF-2 WSM / Check Dam schemes from the contract list (identity, location, reported status, contract cost where known). **Status dates are blank** so the team can enter official dates. `03_Example_Filled` is demonstration data only.

## Rebuild

```bash
python3 construction_tracker/generate_tracker.py
python3 construction_tracker/verify_tracker.py
```
