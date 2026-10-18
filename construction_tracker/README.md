# Construction Works Scheme Tracker

Excel register for tracking construction schemes from design through handover. Each **sub-project** is one row. Several canals or check dams that share one **Package / Contract Name** keep the same Package ID (Package #8-AF2 IS is two rows; Package #10-AF2 IS is four). Each pipeline step has its own date. The workbook then calculates:

- days taken to move from one step to the next
- days spent in the current step
- total days from the first dated step to the last
- whether the current step has exceeded its target days
- schedule health against expected award (Not awarded) or contract end (Awarded)

Open **`WBK_AF2_Construction_Works_Tracker.xlsx`**.

## Sheets

| Sheet | Use |
| --- | --- |
| `00_How_to_Use` | How to fill the register and how to add or remove columns and domains |
| `01_Scheme_Tracker` | Working register — one row per sub-project; collapse extra sites of a package with the outline +/- |
| `02_Dashboard` | Counts by status, region, major intervention, Awarded / Not awarded, average days per step |
| `03_Package_Summary` | One row per contract package (Package #8 and #10 sit here as single packages). Filter Contractor Name for unique contracts. |
| `10_By_Contractor` | One row per company: unique awarded contracts, not repeated sub-project rows (ZSCC = 1 contract / 4 canals) |
| `11_Package_Status` | How many **packages** are in each step, and the share of that step across Watershed Management, Irrigation Scheme, Drip, LLL, Agroforestry |
| `04_Date_Rules` | What each date means and the conditions behind green / amber / red |
| `05_Example_Filled` | Two worked examples so you can see the day-count formulas |
| `06_Status_Pipeline` | Ordered list of steps (edit spare slots to add a step) |
| `07_Domains` | Dropdown lists: major intervention, sub-type, donor, project, region, Awarded / Not awarded |
| `08_Geography` | Province and district lists |
| `09_Lookups` | Maps region/province names onto those lists |

## Interventions

**Major types** (dropdown on Major intervention):

- Watershed Management
- Irrigation Scheme
- Drip Irrigation
- Agroforestry saplings / seeds
- Laser Land Leveler (LLL)

**Sub-types** (dropdown on Intervention sub-type): irrigation canal, protection wall, check dam, boulder check dam, karez, drip plot, LLL unit, saplings and seeds, and so on.

**Awarded / Not awarded** replaces the old Remaining label.

## Packages

One Package / Contract Name can cover several sites in different districts. Keep one row per site so location and progress stay honest. Repeat the same Package ID and Package / Contract Name on every row. `Sub-project in package` shows `1 of 4`, `2 of 4`, …

Cells are **not merged** (that would break AutoFilter). Extra rows of the same package are grouped — use the outline control at the left of `01_Scheme_Tracker`. `03_Package_Summary` lists each package once, with a live sub-project count and total cost.

## Find contracts awarded to one company

The contractor name is repeated on every sub-project of that contract. Filtering `Contractor Name` on `01_Scheme_Tracker` for **Zahid Saeed Engineering and Construction Company (ZSCC)** shows four rows — those are four canals on **one** Package #10 contract (`057/2025`), not four contracts.

To list unique contracts:

1. Open `10_By_Contractor` and filter the company. ZSCC = **1 awarded contract**, 4 sub-projects.
2. Or open `03_Package_Summary` and filter **Contractor Name**.

Count **Package IDs / Contract Numbers**, not the number of tracker rows.

## How many packages are in each status

`02_Dashboard` still counts sub-project rows. That overstates a step when one contract has many sites (50 LLL units and 39 agroforestry rows are each **one** package still Under Awarding).

Open **`11_Package_Status`** for unique-package counts. Each status row also splits across the five major interventions (count and share of that status). A second table shows how each major is spread across statuses (for example what share of Irrigation Scheme packages is still Under Construction).

A package takes the **least-advanced status of its unfinished sites**. It is Completed only when every sub-project is completed. Filter **Package status** on `03_Package_Summary` to list the contracts.

## Status pipeline (default)

1. Under Design
2. Under Review of WRI
3. Under LTO Review
4. PR to be Raised
5. ITB Launched
6. Retendered (Re-ITB)
7. Under Technical Evaluation
8. Under Awarding
9. Awarded
10. Under Construction
11. Completed / Handover

Three spare slots sit after these. Type a name in a spare slot on `06_Status_Pipeline` and the matching date column on the tracker updates itself.

## How dates and schedule health work

Enter the date a scheme **reached** each step (the day that step started / was achieved). Full conditions are on `04_Date_Rules`.

| Column | Rule |
| --- | --- |
| `Days: A → B` | Date of B minus the last previous filled date (so a skipped step still measures from the last real date) |
| `Days in current status` | `TODAY()` minus the latest filled status date |
| `Total days first → last step` | Last filled date minus first filled date |
| `Days over target this step` | Days in current status minus the target days on `06_Status_Pipeline` |
| `Current Status (auto)` | Name of the latest step that has a date; if no dates yet, uses Reported Status |
| `Awarded Date` | Copies `Date: Awarded` |
| `Planned End Date` | Contract / expected end if filled, otherwise `EDATE(Awarded Date, Contract Duration months)` |
| `Schedule health` (Not awarded) | Watches **Expected award date** vs `TODAY()`: past it = Behind; within 30 days = At risk; else On track |
| `Schedule health` (Awarded) | Watches **Planned End Date** and physical progress: past end with progress &lt; 100 = Behind; elapsed-time % minus progress &gt; 15 = Behind; end within 30 days and progress &lt; 90 = At risk; else On track |
| `Days vs planned date` | Days remaining (positive) or overdue (negative) to the date above |

Grey cells are formulas. Do not type over them. White cells are inputs.

Negative day-counts mean a later step was dated earlier than a previous one — check the dates.

Colours:

- green — on track or completed
- amber — planned award or end date is within 30 days (close to off track)
- red — already past the planned award/end date, or physical progress is more than 15 points behind elapsed contract time

`TODAY()` is live, so health colours change as the calendar moves.

## Add or remove domains

**Major intervention, sub-type, donor, project, region, status, Awarded / Not awarded**

Type the new value in the first empty cell at the bottom of that column on `07_Domains`. Do not leave a blank cell in the middle of the list. Dropdowns expand automatically.

**District**

Type it under the province column on `08_Geography`.

**Province or a new region**

Add the name on `08_Geography`, add a matching row on `09_Lookups`, and create the `Prov_` / `Dist_` named range (Formulas → Name Manager). The reliable way is to edit `GEOGRAPHY` in `tracker_config.py` and regenerate.

## Add or remove status steps or columns

**Add a step at the end** — type the name in a spare slot on `06_Status_Pipeline`. No script needed.

**Insert a step in the middle, remove a step, or add a permanent extra column** (GPS, engineer, photo link, …) — edit `tracker_config.py` (`STATUS_PIPELINE`, `IDENTITY_COLUMNS`, or `CONTRACT_COLUMNS`) and run:

```bash
pip install -r construction_tracker/requirements.txt
python3 construction_tracker/generate_tracker.py
```

Copy any dates you already typed into a backup first; regenerating replaces the workbook file.

Hide columns you do not need rather than deleting formula columns.

## Pre-loaded schemes

`01_Scheme_Tracker` is one combined register built from the seven sheets in
`2- WBK-AF2_Master file contract status awarded and remaining contracts.xlsx`:

- awarded and not-awarded on/off-farm irrigation
- awarded and not-awarded WSM / check dams
- drip irrigation
- LLL supply
- agroforestry saplings and seeds

`05_Example_Filled` is demonstration data only.

Rebuild after the master file changes:

```bash
python3 construction_tracker/import_master.py
python3 construction_tracker/generate_tracker.py
```

## Rebuild

```bash
python3 construction_tracker/generate_tracker.py
python3 construction_tracker/verify_tracker.py
```
