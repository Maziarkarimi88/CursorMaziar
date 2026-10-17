#!/usr/bin/env python3
"""Build the Construction Works Scheme Tracker workbook.

Run from this folder::

    python3 generate_tracker.py

Edit ``tracker_config.py`` to add/remove status steps, domains, extra
columns, or schemes, then run this script again.
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.comments import Comment
from openpyxl.formatting.rule import CellIsRule, DataBarRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

from tracker_config import (
    AWARD_GROUPS,
    CONTRACT_COLUMNS,
    DONORS,
    EXAMPLE_SCHEMES,
    GEOGRAPHY,
    IDENTITY_COLUMNS,
    INTERVENTION_FAMILIES,
    INTERVENTION_TYPES,
    MAX_DATA_ROWS,
    NEAR_OFFTRACK_DAYS,
    PROGRESS_LAG_PCT,
    PROJECTS,
    SCHEMES,
    SPARE_STATUS_SLOTS,
    STATUS_PIPELINE,
    STUCK_THRESHOLD_DAYS,
    WORKBOOK_SUBTITLE,
    WORKBOOK_TITLE,
)

# --- colours (muted, print-friendly) ----------------------------------------
NAVY = "1B365D"
STEEL = "2E5984"
GOLD = "8A6D3B"
FOREST = "3D5A3D"
SLATE = "4A5560"
WHITE = "FFFFFF"
INK = "1F2A33"
MUTED = "5B6770"
LINE = "C5CDD6"
FORMULA_BG = "F4F6F8"
ALT_ROW = "F7F9FC"
LIGHT_NAVY = "E8EEF4"
LIGHT_GOLD = "F7F1E3"
LIGHT_GREEN = "E8EFE8"
LIGHT_SLATE = "EEF1F4"
WARN_FILL = "F8D7DA"
WARN_FONT = "842029"
OK_FILL = "D4E6D4"
INPUT_BG = "FFFFFF"
SPARE_FILL = "F0F0F0"
TITLE_FILL = "1B365D"

STATUS_COLORS = {
    "Under Design": "E8EEF4",
    "Under Review of WRI": "D6E4F0",
    "Under LTO Review": "E6E0EF",
    "PR to be Raised": "F7F1E3",
    "ITB Launched": "F3E6D0",
    "Retendered (Re-ITB)": "F3E6D0",
    "Under Technical Evaluation": "F0E6C8",
    "Under Awarding": "D4E8E4",
    "Awarded": "D4E6D4",
    "Under Construction": "C5D5C5",
    "Completed / Handover": "1B365D",
    "Cancelled": "D0D4D8",
    "Not started": "FFFFFF",
}

# Traffic-light fills for schedule health (behind / close / on track)
HEALTH_GREEN = "C6E0B4"
HEALTH_AMBER = "FFE699"
HEALTH_RED = "F4B183"
HEALTH_GREY = "D0D4D8"

THIN = Border(
    left=Side(style="thin", color=LINE),
    right=Side(style="thin", color=LINE),
    top=Side(style="thin", color=LINE),
    bottom=Side(style="thin", color=LINE),
)
MED_NAVY = Border(
    left=Side(style="thin", color=NAVY),
    right=Side(style="thin", color=NAVY),
    top=Side(style="thin", color=NAVY),
    bottom=Side(style="thin", color=NAVY),
)

FONT_TITLE = Font(name="Calibri", size=16, bold=True, color=WHITE)
FONT_SUB = Font(name="Calibri", size=10, italic=True, color="D6DEE8")
FONT_GROUP = Font(name="Calibri", size=9, bold=True, color=WHITE)
FONT_HEAD = Font(name="Calibri", size=9, bold=True, color=WHITE)
FONT_BODY = Font(name="Calibri", size=10, color=INK)
FONT_HINT = Font(name="Calibri", size=9, italic=True, color=MUTED)
FONT_FORMULA = Font(name="Calibri", size=10, color=STEEL)
FONT_SECTION = Font(name="Calibri", size=13, bold=True, color=NAVY)
FONT_H2 = Font(name="Calibri", size=11, bold=True, color=STEEL)

ALIGN_C = Alignment(horizontal="center", vertical="center", wrap_text=True)
ALIGN_L = Alignment(horizontal="left", vertical="center", wrap_text=True)
ALIGN_R = Alignment(horizontal="right", vertical="center")

SHEET_HOWTO = "00_How_to_Use"
SHEET_TRACKER = "01_Scheme_Tracker"
SHEET_DASH = "02_Dashboard"
SHEET_EXAMPLE = "03_Example_Filled"
SHEET_PIPELINE = "04_Status_Pipeline"
SHEET_DOMAINS = "05_Domains"
SHEET_GEO = "06_Geography"
SHEET_LOOKUPS = "07_Lookups"

HEADER_ROW = 3
GROUP_ROW = 2
TITLE_ROW = 1
DATA_START = 4


def fill(hex_color: str) -> PatternFill:
    return PatternFill("solid", fgColor=hex_color)


def excel_name(prefix: str, label: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", str(label)).strip("_")
    if not cleaned:
        cleaned = "X"
    if cleaned[0].isdigit():
        cleaned = "N_" + cleaned
    return f"{prefix}_{cleaned}"[:250]


def quote_sheet(name: str) -> str:
    return f"'{name}'"


def colletter(idx: int) -> str:
    return get_column_letter(idx)


def parse_date(value):
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d")


def all_pipeline_slots() -> list[dict]:
    slots = list(STATUS_PIPELINE)
    for i in range(SPARE_STATUS_SLOTS):
        slots.append(
            {
                "name": "",
                "short": "",
                "description": "Spare slot — type a status name here to add a step.",
                "target_days": None,
                "spare": True,
            }
        )
    return slots


def all_provinces() -> list[str]:
    names = []
    for region in GEOGRAPHY.values():
        names.extend(region["provinces"].keys())
    return names


def all_districts() -> list[str]:
    names = []
    seen = set()
    for region in GEOGRAPHY.values():
        for districts in region["provinces"].values():
            for d in districts:
                if d not in seen:
                    seen.add(d)
                    names.append(d)
    return names


class Layout:
    """Column map for the scheme tracker (1-based Excel indexes)."""

    def __init__(self):
        self.idx: dict[str, int] = {}
        self.widths: dict[str, float] = {}
        self.kinds: dict[str, str] = {}
        self.headers: dict[str, str] = {}
        self.groups: list[tuple[str, int, int, str]] = []
        self.status_date_cols: list[int] = []
        self.duration_cols: list[int] = []
        self.slots = all_pipeline_slots()
        col = 1

        def take(key, header, width, kind):
            nonlocal col
            self.idx[key] = col
            self.headers[key] = header
            self.widths[key] = width
            self.kinds[key] = kind
            col += 1
            return col - 1

        start = col
        for key, header, width, kind in IDENTITY_COLUMNS:
            take(key, header, width, kind)
        self.groups.append(("1. Scheme identity", start, col - 1, NAVY))

        start = col
        for key, header, width, kind in CONTRACT_COLUMNS:
            take(key, header, width, kind)
        self.groups.append(("2. Contract and physical progress", start, col - 1, FOREST))

        start = col
        take("current_status", "Current Status (auto)", 24, "formula")
        take("days_in_current", "Days in current status", 12, "formula")
        take("total_pipeline_days", "Total days first → last step", 12, "formula")
        take("over_target", "Days over target this step", 12, "formula")
        take("schedule_health", "Schedule health", 26, "formula")
        take("days_vs_plan", "Days vs planned date", 14, "formula")
        self.groups.append(("3. Live status and schedule health (calculated)", start, col - 1, GOLD))

        start = col
        for i, slot in enumerate(self.slots):
            key = f"date_{i}"
            label = slot["name"] or f"(spare {i + 1})"
            take(key, f"Date: {label}", 16, "date")
            self.status_date_cols.append(self.idx[key])
        self.groups.append(
            ("4. Status dates — enter the date each step was reached", start, col - 1, STEEL)
        )

        start = col
        for i in range(1, len(self.slots)):
            key = f"dur_{i}"
            take(key, f"Days into step {i + 1}", 24, "formula")
            self.duration_cols.append(self.idx[key])
        self.groups.append(
            ("5. Days between steps (calculated)", start, col - 1, SLATE)
        )

        start = col
        take("helper_prov_range", "_ProvinceList", 14, "formula")
        take("helper_dist_range", "_DistrictList", 14, "formula")
        self.groups.append(("Helpers (hidden)", start, col - 1, LINE))
        self.helper_start = start
        self.last_col = col - 1
        self.n_slots = len(self.slots)

    def letter(self, key: str) -> str:
        return colletter(self.idx[key])

    def addr(self, key: str, row: int) -> str:
        return f"{self.letter(key)}{row}"

    def date_range(self, row: int) -> str:
        a = colletter(self.status_date_cols[0])
        b = colletter(self.status_date_cols[-1])
        return f"{a}{row}:{b}{row}"

    def date_header_range(self) -> str:
        a = colletter(self.status_date_cols[0])
        b = colletter(self.status_date_cols[-1])
        return f"${a}${HEADER_ROW}:${b}${HEADER_ROW}"


def apply_cell(cell, *, font=None, fill_hex=None, align=None, border=THIN, fmt=None, wrap=True):
    if font:
        cell.font = font
    if fill_hex:
        cell.fill = fill(fill_hex)
    if align:
        cell.alignment = align
    elif wrap:
        cell.alignment = ALIGN_L
    if border is not None:
        cell.border = border
    if fmt:
        cell.number_format = fmt


def set_col_widths(ws, mapping: dict[int, float]):
    for idx, width in mapping.items():
        ws.column_dimensions[colletter(idx)].width = width


# --- sheets -----------------------------------------------------------------


def write_howto(wb: Workbook, layout: Layout) -> None:
    ws = wb.create_sheet(SHEET_HOWTO)
    ws.sheet_properties.tabColor = NAVY
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 28
    ws.column_dimensions["C"].width = 92
    ws.column_dimensions["D"].width = 36
    ws.row_dimensions[1].height = 28
    ws.merge_cells("B1:D1")
    c = ws["B1"]
    c.value = WORKBOOK_TITLE
    apply_cell(c, font=FONT_TITLE, fill_hex=NAVY, align=ALIGN_L, border=None)
    for col in ("C", "D"):
        apply_cell(ws[f"{col}1"], fill_hex=NAVY, border=None)
    ws.merge_cells("B2:D2")
    c = ws["B2"]
    c.value = WORKBOOK_SUBTITLE + "  ·  How to use and how to add or remove columns and domains"
    apply_cell(c, font=FONT_SUB, fill_hex=NAVY, align=ALIGN_L, border=None)
    for col in ("C", "D"):
        apply_cell(ws[f"{col}2"], fill_hex=NAVY, border=None)

    rows = [
        ("", "", ""),
        ("What this workbook does", "section", ""),
        (
            "Purpose",
            "Track every construction scheme from design through handover. "
            "Each scheme is one row. Each pipeline step has its own date. "
            "Excel then calculates how many days it took to move from one step to the next, "
            "how long the scheme has sat in the current step, and the total days from the first date to the last.",
            "",
        ),
        (
            "Sheets",
            "01_Scheme_Tracker is the working register (type here). "
            "02_Dashboard summarises counts and average durations. "
            "03_Example_Filled shows two worked examples so you can see the day-count formulas. "
            "04_Status_Pipeline is the ordered list of steps. "
            "05_Domains holds dropdown lists (intervention, donor, project, region). "
            "06_Geography holds province and district lists. "
            "07_Lookups maps region/province names to those lists.",
            "",
        ),
        ("Daily use", "section", ""),
        (
            "Add a scheme",
            "Go to 01_Scheme_Tracker and type in the next empty row. "
            "Dropdowns are already attached for Project, Intervention Type, Region, Province, District, Donor, and Reported Status. "
            "Choose Region first, then Province, then District (the province list follows the region).",
            "01_Scheme_Tracker",
        ),
        (
            "Enter status dates",
            "When a scheme reaches a step, type that day's date in the matching 'Date:' column "
            "(for example Date: Under Design, Date: ITB Launched). "
            "Use a real date, not text. Current Status then switches automatically to the latest dated step. "
            "If no dates are entered yet, Current Status falls back to Reported Status.",
            "Section 4 of the tracker",
        ),
        (
            "Awarded date and contract duration",
            "Type the contract-signature (or notice of award) date in the Date: Awarded column in section 4. "
            "The Awarded Date field in section 2 copies it automatically. "
            "Contract Duration (months) is the period in the contract. "
            "Planned End Date is calculated with EDATE(Awarded Date, duration). "
            "Physical Works Progress % is 0–100. Contractor Name and Contract Number are free text.",
            "Sections 2 and 4 of the tracker",
        ),
        (
            "Reading the day counts",
            "Each 'Days … → …' column is the number of days from the previous filled date to this step's date. "
            "If a step is skipped, the count still uses the last previous date that was filled. "
            "'Days in current status' is TODAY minus the latest status date (this number changes every day). "
            "'Total days first → last step' is last filled date minus first filled date. "
            "'Days over target this step' is days in current status minus the target days set on 04_Status_Pipeline (blank if there is no target).",
            "Sections 3 and 5",
        ),
        (
            "Schedule health colours",
            "Schedule health is calculated from planned dates (not typed by hand). "
            "GREEN — On track, or completed on/before the plan. "
            "AMBER — At risk / close to off track: the planned award or contract end is within 30 days, or works are not yet far enough along. "
            "RED — Behind: today is after the planned award date (remaining contracts) or after the contract end date (awarded), "
            "or physical progress is more than 15 percentage points behind the share of the contract period that has already elapsed. "
            "'Days vs planned date' is days remaining (positive, green/amber) or days overdue (negative, red).",
            "Section 3 of the tracker",
        ),
        ("Add or remove domains (dropdown values)", "section", ""),
        (
            "Add an intervention type, donor, project, or region",
            "Open 05_Domains. Type the new value in the first empty cell at the bottom of that column. "
            "Do not leave a blank row in the middle of the list. The dropdowns expand automatically "
            "(named ranges use COUNTA). You do not need to re-run the generator for this.",
            "05_Domains",
        ),
        (
            "Remove a domain value",
            "Delete the cell on 05_Domains (or 06_Geography). Existing scheme rows that already use that value keep showing it; "
            "new rows will no longer offer it in the dropdown.",
            "05_Domains / 06_Geography",
        ),
        (
            "Add a province",
            "1) On 06_Geography, under the correct region code column in the province block, type the province name. "
            "2) Add a new district column for that province in the district block (copy an adjacent column). "
            "3) On 07_Lookups, add a row: Province name | Dist_<Province> named range. "
            "4) Define the named range Dist_<Province> (Formulas → Name Manager) pointing at the district cells. "
            "The reliable alternative is to add the province in tracker_config.py GEOGRAPHY and run generate_tracker.py.",
            "06_Geography + 07_Lookups",
        ),
        (
            "Add a district",
            "On 06_Geography find the province column in the district block and type the district in the next empty cell. "
            "The Dist_ named range grows automatically. No other change is required.",
            "06_Geography",
        ),
        ("Add or remove status steps (the tracking pipeline)", "section", ""),
        (
            "Add a step at the end (no script)",
            "Open 04_Status_Pipeline. Spare slots are already reserved at the bottom. "
            "Type the new status name, a short name, a description, and optional target days in the first spare row. "
            "The matching Date column header on 01_Scheme_Tracker updates itself. Start entering dates in that column. "
            "Duration headers also pick up the new name.",
            "04_Status_Pipeline spare slots",
        ),
        (
            "Add a step in the middle, or remove a step",
            "Changing order affects rows that already have dates, because dates sit in fixed columns. "
            "Preferred method: edit STATUS_PIPELINE in tracker_config.py (add, remove, or reorder dicts) "
            "and run python3 generate_tracker.py. That rebuilds date columns, duration formulas, dropdowns, and the dashboard. "
            "Copy any dates you already typed into a backup first — regenerating replaces the workbook file.",
            "tracker_config.py",
        ),
        (
            "Hide a column you do not need",
            "On 01_Scheme_Tracker, select the column → right-click → Hide. "
            "Do not delete formula columns (sections 3 and 5) or the tracker will break. "
            "Hidden columns can be unhidden later.",
            "01_Scheme_Tracker",
        ),
        (
            "Add an extra data column (GPS, engineer, photo link, …)",
            "Insert a column inside section 1 (identity) or section 2 (contract), not inside the date or duration blocks. "
            "Give it a header in row 3. Filters will include it after you re-apply AutoFilter if needed. "
            "To make it permanent in future rebuilds, append a tuple to IDENTITY_COLUMNS or CONTRACT_COLUMNS in tracker_config.py.",
            "01_Scheme_Tracker / tracker_config.py",
        ),
        ("Rules that keep the numbers honest", "section", ""),
        (
            "Dates must move forward",
            "A later step should not have an earlier date than a previous step. Negative day-counts mean the dates need checking.",
            "",
        ),
        (
            "One row = one scheme",
            "If a package has three check dams, use three rows (as in the pre-loaded AF-2 list). "
            "Package-level cost can sit on the first scheme of the package and stay blank on the others.",
            "",
        ),
        (
            "Grey cells are formulas",
            "Do not type over Current Status, Planned End Date, day-count columns, or helper columns. "
            "White cells are inputs.",
            "",
        ),
        (
            "DEMO rows",
            "03_Example_Filled is for learning. Do not copy those dates into official reports.",
            "03_Example_Filled",
        ),
    ]

    r = 3
    for title, body, where in rows:
        if body == "section":
            r += 1
            ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
            c = ws.cell(r, 2, title)
            apply_cell(c, font=FONT_SECTION, fill_hex=LIGHT_NAVY, align=ALIGN_L, border=None)
            ws.cell(r, 3).fill = fill(LIGHT_NAVY)
            ws.cell(r, 4).fill = fill(LIGHT_NAVY)
            ws.row_dimensions[r].height = 22
            r += 1
            continue
        ws.cell(r, 2, title)
        apply_cell(ws.cell(r, 2), font=Font(name="Calibri", size=10, bold=True, color=NAVY), fill_hex=LIGHT_SLATE, align=ALIGN_L)
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=3)
        apply_cell(ws.cell(r, 3, body), font=FONT_BODY, align=ALIGN_L)
        apply_cell(ws.cell(r, 4, where), font=FONT_HINT, align=ALIGN_L)
        ws.row_dimensions[r].height = 64
        r += 1

    r += 1
    ws.cell(r, 2, "Status pipeline (default)")
    apply_cell(ws.cell(r, 2), font=FONT_SECTION, fill_hex=LIGHT_NAVY, border=None)
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
    r += 1
    for i, col_h in enumerate(["Step", "Status", "What it means", "Target days"]):
        apply_cell(ws.cell(r, 2 + i, col_h), font=FONT_HEAD, fill_hex=STEEL, align=ALIGN_C)
    r += 1
    for i, step in enumerate(STATUS_PIPELINE, start=1):
        apply_cell(ws.cell(r, 2, i), font=FONT_BODY, align=ALIGN_C)
        apply_cell(ws.cell(r, 3, step["name"]), font=FONT_BODY, fill_hex=STATUS_COLORS.get(step["name"], WHITE))
        apply_cell(ws.cell(r, 4, step["description"]), font=FONT_BODY)
        apply_cell(ws.cell(r, 5, step["target_days"] or "—"), font=FONT_BODY, align=ALIGN_C)
        r += 1

    ws.freeze_panes = "B3"
    ws.print_title_rows = "1:2"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.oddHeader.left.text = WORKBOOK_TITLE
    ws.oddFooter.right.text = "Page &P of &N"


def write_pipeline(wb: Workbook) -> None:
    ws = wb.create_sheet(SHEET_PIPELINE)
    ws.sheet_properties.tabColor = STEEL
    ws.sheet_view.showGridLines = False
    headers = ["Slot", "Status name (edit / add here)", "Short name", "Description", "Target days", "Notes"]
    widths = [10, 36, 16, 72, 14, 44]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[colletter(i)].width = w
    ws.merge_cells("A1:F1")
    c = ws["A1"]
    c.value = "Status pipeline — add a name in a spare slot to create a new step on the tracker"
    apply_cell(c, font=FONT_TITLE, fill_hex=NAVY, align=ALIGN_L)
    for col in range(2, 7):
        apply_cell(ws.cell(1, col), fill_hex=NAVY)
    ws.row_dimensions[1].height = 26
    for i, h in enumerate(headers, 1):
        apply_cell(ws.cell(2, i, h), font=FONT_HEAD, fill_hex=STEEL, align=ALIGN_C)
    slots = all_pipeline_slots()
    for i, slot in enumerate(slots, start=1):
        row = i + 2
        is_spare = bool(slot.get("spare") or not slot["name"])
        bg = SPARE_FILL if is_spare else WHITE
        apply_cell(ws.cell(row, 1, i), font=FONT_BODY, fill_hex=bg, align=ALIGN_C)
        apply_cell(ws.cell(row, 2, slot["name"]), font=FONT_BODY, fill_hex=STATUS_COLORS.get(slot["name"], bg))
        apply_cell(ws.cell(row, 3, slot.get("short", "")), font=FONT_BODY, fill_hex=bg)
        apply_cell(ws.cell(row, 4, slot.get("description", "")), font=FONT_BODY, fill_hex=bg)
        td = slot.get("target_days")
        apply_cell(ws.cell(row, 5, td if td not in (None, "") else None), font=FONT_BODY, fill_hex=bg, align=ALIGN_C, fmt="0")
        note = "Type a status name in column B to activate this date column on the tracker." if is_spare else "Used by tracker date headers and duration labels."
        apply_cell(ws.cell(row, 6, note), font=FONT_HINT, fill_hex=bg)
        ws.row_dimensions[row].height = 22
    ws.freeze_panes = "A3"
    ws.data_validations.append(
        DataValidation(type="whole", operator="greaterThanOrEqual", formula1="0", allow_blank=True, sqref="E3:E20")
    )


def write_domains(wb: Workbook) -> dict:
    """Write dropdown source lists. Returns named-range metadata."""
    ws = wb.create_sheet(SHEET_DOMAINS)
    ws.sheet_properties.tabColor = GOLD
    ws.sheet_view.showGridLines = False
    ws.merge_cells("A1:H1")
    c = ws["A1"]
    c.value = "Domains — type a new value in the first empty cell of a column to add it to the dropdowns"
    apply_cell(c, font=FONT_TITLE, fill_hex=NAVY, align=ALIGN_L)
    for col in range(2, 9):
        apply_cell(ws.cell(1, col), fill_hex=NAVY)
    ws.row_dimensions[1].height = 26

    columns = [
        ("Interventions", INTERVENTION_TYPES, 28),
        ("Donors", DONORS, 28),
        ("Projects", PROJECTS, 52),
        ("Regions", list(GEOGRAPHY.keys()), 28),
        ("Statuses", [s["name"] for s in STATUS_PIPELINE] + ["Not started", "Cancelled"], 28),
        ("All_Provinces", all_provinces(), 22),
        ("All_Districts", all_districts(), 28),
        ("AwardGroups", AWARD_GROUPS, 16),
        ("Families", INTERVENTION_FAMILIES, 24),
    ]
    meta = {}
    for i, (name, values, width) in enumerate(columns, start=1):
        ws.column_dimensions[colletter(i)].width = width
        apply_cell(ws.cell(2, i, name), font=FONT_HEAD, fill_hex=STEEL, align=ALIGN_C)
        for r, val in enumerate(values, start=3):
            apply_cell(ws.cell(r, i, val), font=FONT_BODY, fill_hex=WHITE)
        # padding rows so users see where to type
        for r in range(3 + len(values), 3 + len(values) + 12):
            apply_cell(ws.cell(r, i, None), font=FONT_BODY, fill_hex="FBFCFD")
        letter = colletter(i)
        meta[name] = {
            "col": i,
            "letter": letter,
            "n": len(values),
            "first_row": 3,
        }
    ws.freeze_panes = "A3"
    ws.auto_filter.ref = "A2:I2"
    return meta


def write_geography(wb: Workbook) -> dict:
    """Province-by-region and district-by-province blocks + named range info."""
    ws = wb.create_sheet(SHEET_GEO)
    ws.sheet_properties.tabColor = FOREST
    ws.sheet_view.showGridLines = False
    ws.merge_cells("A1:P1")
    c = ws["A1"]
    c.value = (
        "Geography lists — add a province under its region code, or a district under its province column. "
        "Do not leave blank cells in the middle of a list."
    )
    apply_cell(c, font=FONT_TITLE, fill_hex=NAVY, align=ALIGN_L)
    for col in range(2, 17):
        apply_cell(ws.cell(1, col), fill_hex=NAVY)
    ws.row_dimensions[1].height = 28

    # Row 3 labels the province-by-region block
    apply_cell(ws.cell(3, 1, "PROVINCES BY REGION (column header is the region code used in named ranges)"), font=FONT_H2, fill_hex=LIGHT_GREEN, border=None)
    ws.merge_cells("A3:H3")

    region_items = list(GEOGRAPHY.items())
    prov_meta = {}  # region display -> {code, col, n, named}
    for i, (region_name, spec) in enumerate(region_items):
        col = i + 1
        code = spec["code"]
        provinces = list(spec["provinces"].keys())
        apply_cell(ws.cell(4, col, code), font=FONT_HEAD, fill_hex=FOREST, align=ALIGN_C)
        for r, prov in enumerate(provinces, start=5):
            apply_cell(ws.cell(r, col, prov), font=FONT_BODY)
        for r in range(5 + len(provinces), 5 + len(provinces) + 8):
            apply_cell(ws.cell(r, col, None), font=FONT_BODY, fill_hex="FBFCFD")
        ws.column_dimensions[colletter(col)].width = 22
        prov_meta[region_name] = {
            "code": code,
            "col": col,
            "n": len(provinces),
            "named": excel_name("Prov", code if False else region_name),
            "range_name": f"Prov_{code}",
            "start_row": 5,
        }
        # named range uses Prov_<code>
        prov_meta[region_name]["range_name"] = f"Prov_{code}"

    # District block starts after province rows
    max_prov_rows = max(len(spec["provinces"]) for spec in GEOGRAPHY.values())
    dist_header_row = 5 + max_prov_rows + 10
    apply_cell(
        ws.cell(dist_header_row, 1, "DISTRICTS BY PROVINCE (column header is the province; add districts below)"),
        font=FONT_H2,
        fill_hex=LIGHT_GOLD,
        border=None,
    )
    ws.merge_cells(start_row=dist_header_row, start_column=1, end_row=dist_header_row, end_column=8)

    dist_meta = {}
    col = 1
    name_row = dist_header_row + 1
    data_row = dist_header_row + 2
    max_dist = 1
    for region_name, spec in region_items:
        for prov, districts in spec["provinces"].items():
            apply_cell(ws.cell(name_row, col, prov), font=FONT_HEAD, fill_hex=GOLD, align=ALIGN_C)
            for r, dist in enumerate(districts, start=data_row):
                apply_cell(ws.cell(r, col, dist), font=FONT_BODY)
            for r in range(data_row + len(districts), data_row + len(districts) + 8):
                apply_cell(ws.cell(r, col, None), font=FONT_BODY, fill_hex="FBFCFD")
            ws.column_dimensions[colletter(col)].width = max(16, ws.column_dimensions[colletter(col)].width or 16)
            dist_meta[prov] = {
                "col": col,
                "n": len(districts),
                "range_name": excel_name("Dist", prov),
                "start_row": data_row,
                "header_row": name_row,
            }
            max_dist = max(max_dist, len(districts))
            col += 1

    return {
        "prov_meta": prov_meta,
        "dist_meta": dist_meta,
        "prov_start_row": 5,
        "dist_start_row": data_row,
        "dist_header_row": name_row,
    }


def write_lookups(wb: Workbook, geo: dict) -> None:
    ws = wb.create_sheet(SHEET_LOOKUPS)
    ws.sheet_properties.tabColor = SLATE
    ws.merge_cells("A1:D1")
    apply_cell(
        ws["A1"],
        font=FONT_TITLE,
        fill_hex=NAVY,
        align=ALIGN_L,
    )
    ws["A1"] = "Lookups used by cascading dropdowns — add a row when you add a region or province"
    for col in range(2, 5):
        apply_cell(ws.cell(1, col), fill_hex=NAVY)
    ws.row_dimensions[1].height = 26

    apply_cell(ws.cell(3, 1, "Region display name"), font=FONT_HEAD, fill_hex=STEEL, align=ALIGN_C)
    apply_cell(ws.cell(3, 2, "Province named range"), font=FONT_HEAD, fill_hex=STEEL, align=ALIGN_C)
    apply_cell(ws.cell(3, 3, "Region code"), font=FONT_HEAD, fill_hex=STEEL, align=ALIGN_C)
    apply_cell(ws.cell(3, 5, "Province"), font=FONT_HEAD, fill_hex=FOREST, align=ALIGN_C)
    apply_cell(ws.cell(3, 6, "District named range"), font=FONT_HEAD, fill_hex=FOREST, align=ALIGN_C)

    for i, (region, spec) in enumerate(GEOGRAPHY.items(), start=4):
        apply_cell(ws.cell(i, 1, region), font=FONT_BODY)
        apply_cell(ws.cell(i, 2, geo["prov_meta"][region]["range_name"]), font=FONT_BODY)
        apply_cell(ws.cell(i, 3, spec["code"]), font=FONT_BODY)

    r = 4
    for prov, meta in geo["dist_meta"].items():
        apply_cell(ws.cell(r, 5, prov), font=FONT_BODY)
        apply_cell(ws.cell(r, 6, meta["range_name"]), font=FONT_BODY)
        r += 1

    ws.column_dimensions["A"].width = 32
    ws.column_dimensions["B"].width = 28
    ws.column_dimensions["C"].width = 28
    ws.column_dimensions["D"].width = 4
    ws.column_dimensions["E"].width = 22
    ws.column_dimensions["F"].width = 28
    ws.freeze_panes = "A4"

    n_regions = len(GEOGRAPHY)
    n_prov = len(geo["dist_meta"])
    # Tables so VLOOKUP ranges stay obvious
    t1 = Table(displayName="RegionMap", ref=f"A3:B{3 + n_regions}")
    t1.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    ws.add_table(t1)
    t2 = Table(displayName="ProvinceMap", ref=f"E3:F{3 + n_prov}")
    t2.tableStyleInfo = TableStyleInfo(name="TableStyleMedium7", showRowStripes=True)
    ws.add_table(t2)


def register_named_ranges(wb: Workbook, domain_meta: dict, geo: dict) -> None:
    def add(name: str, formula: str):
        if name[0].isdigit():
            raise ValueError(f"Excel named ranges cannot start with a digit: {name}")
        if not formula.startswith("="):
            formula = "=" + formula
        wb.defined_names.add(DefinedName(name=name, attr_text=formula))

    d = quote_sheet(SHEET_DOMAINS)
    g = quote_sheet(SHEET_GEO)

    for name, info in domain_meta.items():
        letter = info["letter"]
        formula = (
            f"OFFSET({d}!${letter}$3,0,0,COUNTA({d}!${letter}$3:${letter}$400),1)"
        )
        add(name, formula)

    for region, spec in geo["prov_meta"].items():
        letter = colletter(spec["col"])
        start = spec["start_row"]
        formula = (
            f"OFFSET({g}!${letter}${start},0,0,COUNTA({g}!${letter}${start}:${letter}$80),1)"
        )
        add(spec["range_name"], formula)

    for prov, spec in geo["dist_meta"].items():
        letter = colletter(spec["col"])
        start = spec["start_row"]
        formula = (
            f"OFFSET({g}!${letter}${start},0,0,COUNTA({g}!${letter}${start}:${letter}$80),1)"
        )
        add(spec["range_name"], formula)


def planned_end_formula(layout: Layout, row: int) -> str:
    awarded = layout.addr("awarded_date", row)
    months = layout.addr("contract_duration_months", row)
    explicit = layout.addr("contract_end_date", row)
    return (
        f'IF({explicit}<>"",{explicit},'
        f'IF(OR({awarded}="",{months}=""),"",EDATE({awarded},{months})))'
    )


def schedule_health_formula(layout: Layout, row: int) -> str:
    name = layout.addr("scheme_name", row)
    group = layout.addr("award_group", row)
    status = layout.addr("current_status", row)
    reported = layout.addr("reported_status", row)
    exp_award = layout.addr("expected_award_date", row)
    end = layout.addr("planned_end_date", row)
    start = layout.addr("awarded_date", row)
    progress = layout.addr("physical_progress_pct", row)
    actual = layout.addr("actual_completion_date", row)
    near = NEAR_OFFTRACK_DAYS
    lag = PROGRESS_LAG_PCT
    return (
        f'IF({name}="","",'
        f'IF(OR({reported}="Cancelled",{status}="Cancelled"),"Cancelled",'
        f'IF(OR({status}="Completed / Handover",{actual}<>"",{progress}>=100),"Completed — on track",'
        f'IF({group}="Remaining",'
        f'IF({exp_award}="",IF({end}="","No planned date",'
        f'IF(TODAY()>{end},"Behind — past planned date",'
        f'IF({end}-TODAY()<={near},"At risk — close to off track","On track"))),'
        f'IF(TODAY()>{exp_award},"Behind — award date passed",'
        f'IF({exp_award}-TODAY()<={near},"At risk — close to off track","On track"))),'
        f'IF({end}="","No planned date",'
        f'IF(AND(TODAY()>{end},OR({progress}="",{progress}<100)),"Behind — past end date",'
        f'IF(AND({start}<>"",{end}<>"",{progress}<>"",({progress}<100),'
        f'((TODAY()-{start})/MAX({end}-{start},1)*100)-{progress}>{lag}),'
        f'"Behind — progress lag",'
        f'IF(AND({end}-TODAY()<={near},{end}-TODAY()>=0,OR({progress}="",{progress}<90)),'
        f'"At risk — close to off track","On track"))))))))'
    )


def days_vs_plan_formula(layout: Layout, row: int) -> str:
    name = layout.addr("scheme_name", row)
    group = layout.addr("award_group", row)
    exp_award = layout.addr("expected_award_date", row)
    end = layout.addr("planned_end_date", row)
    status = layout.addr("current_status", row)
    return (
        f'IF(OR({name}="",{status}="Completed / Handover",{status}="Cancelled"),"",'
        f'IF({group}="Remaining",'
        f'IF({exp_award}<>"",{exp_award}-TODAY(),IF({end}="","",{end}-TODAY())),'
        f'IF({end}="","",{end}-TODAY())))'
    )


def current_status_formula(layout: Layout, row: int) -> str:
    dates = layout.date_range(row)
    headers = layout.date_header_range()
    reported = layout.addr("reported_status", row)
    # LOOKUP last non-empty date's header. Headers are "Date: <name>".
    # SUBSTITUTE strips the prefix. Fallback to reported status.
    return (
        f'IF({layout.addr("scheme_name", row)}="","",'
        f'IF(COUNT({dates})=0,IF({reported}="","Not started",{reported}),'
        f'SUBSTITUTE(LOOKUP(2,1/({dates}<>""),{headers}),"Date: ","")))'
    )


def days_in_current_formula(layout: Layout, row: int) -> str:
    dates = layout.date_range(row)
    return (
        f'IF(OR({layout.addr("scheme_name", row)}="",COUNT({dates})=0),"",'
        f'TODAY()-LOOKUP(2,1/({dates}<>""),{dates}))'
    )


def total_days_formula(layout: Layout, row: int) -> str:
    dates = layout.date_range(row)
    return (
        f'IF(OR({layout.addr("scheme_name", row)}="",COUNT({dates})<2),"",'
        f'LOOKUP(2,1/({dates}<>""),{dates})-MIN({dates}))'
    )


def over_target_formula(layout: Layout, row: int) -> str:
    """Days in current status minus target days for that status name."""
    cur = layout.addr("current_status", row)
    days = layout.addr("days_in_current", row)
    # MATCH status name on pipeline sheet column B, return target days column E
    pipe = quote_sheet(SHEET_PIPELINE)
    return (
        f'IF(OR({days}="",{cur}="Not started",{cur}=""),"",'
        f'IFERROR({days}-IF(VLOOKUP({cur},{pipe}!$B$3:$E$20,4,FALSE)="",0,'
        f'VLOOKUP({cur},{pipe}!$B$3:$E$20,4,FALSE)),""))'
    )


def duration_formula(layout: Layout, row: int, slot_index: int) -> str:
    """Days from last previous filled date into this slot's date (slot_index >= 1)."""
    this_col = layout.status_date_cols[slot_index]
    prev_first = layout.status_date_cols[0]
    prev_last = layout.status_date_cols[slot_index - 1]
    this_addr = f"{colletter(this_col)}{row}"
    prev_range = f"{colletter(prev_first)}{row}:{colletter(prev_last)}{row}"
    return (
        f'IF(OR({layout.addr("scheme_name", row)}="",{this_addr}=""),"",'
        f'IF(COUNT({prev_range})=0,"",{this_addr}-LOOKUP(2,1/({prev_range}<>""),{prev_range})))'
    )


def helper_prov_formula(layout: Layout, row: int) -> str:
    region = layout.addr("region", row)
    look = quote_sheet(SHEET_LOOKUPS)
    return (
        f'IF({region}="","All_Provinces",'
        f'IFERROR(VLOOKUP({region},{look}!$A$4:$B$20,2,FALSE),"All_Provinces"))'
    )


def helper_dist_formula(layout: Layout, row: int) -> str:
    province = layout.addr("province", row)
    look = quote_sheet(SHEET_LOOKUPS)
    last = 3 + len(all_provinces()) + 5
    return (
        f'IF({province}="","All_Districts",'
        f'IFERROR(VLOOKUP({province},{look}!$E$4:$F${last},2,FALSE),"All_Districts"))'
    )


def duration_header_formula(slot_index: int) -> str:
    """slot_index is the destination step (1 = second pipeline slot)."""
    pipe = quote_sheet(SHEET_PIPELINE)
    # Pipeline data starts at row 3 (slot 1). Duration into slot k uses rows k+1 and k+2.
    prev_row = 2 + slot_index
    this_row = 3 + slot_index
    return (
        f'IF(AND({pipe}!B{prev_row}="",{pipe}!B{this_row}=""),"(spare)",'
        f'"Days: "&IF({pipe}!B{prev_row}="","(prev)",{pipe}!B{prev_row})'
        f'&" → "&IF({pipe}!B{this_row}="","(next)",{pipe}!B{this_row}))'
    )


def date_header_formula(slot_index: int) -> str:
    pipe = quote_sheet(SHEET_PIPELINE)
    row = 3 + slot_index  # slot 0 -> row 3
    return f'IF({pipe}!B{row}="","(spare slot {slot_index + 1})","Date: "&{pipe}!B{row})'


def write_tracker_sheet(
    wb: Workbook,
    layout: Layout,
    sheet_name: str,
    schemes: list[dict],
    *,
    fill_example_dates: bool,
    tab_color: str,
    banner: str,
) -> None:
    ws = wb.create_sheet(sheet_name)
    ws.sheet_properties.tabColor = tab_color
    last = layout.last_col
    end_letter = colletter(last)

    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last)
    apply_cell(ws.cell(1, 1, banner), font=FONT_TITLE, fill_hex=NAVY, align=ALIGN_L)
    for col in range(2, last + 1):
        apply_cell(ws.cell(1, col), fill_hex=NAVY)
    ws.row_dimensions[1].height = 24
    ws.row_dimensions[2].height = 20
    ws.row_dimensions[3].height = 36

    for title, start, end, color in layout.groups:
        if title.startswith("Helpers"):
            continue
        ws.merge_cells(start_row=2, start_column=start, end_row=2, end_column=end)
        apply_cell(ws.cell(2, start, title), font=FONT_GROUP, fill_hex=color, align=ALIGN_C)
        for col in range(start + 1, end + 1):
            apply_cell(ws.cell(2, col), fill_hex=color)

    # Headers
    for key, col in layout.idx.items():
        if key.startswith("date_"):
            i = int(key.split("_")[1])
            cell = ws.cell(HEADER_ROW, col, date_header_formula(i))
            apply_cell(cell, font=FONT_HEAD, fill_hex=STEEL, align=ALIGN_C)
        elif key.startswith("dur_"):
            i = int(key.split("_")[1])
            cell = ws.cell(HEADER_ROW, col)
            cell.value = duration_header_formula(i)
            apply_cell(cell, font=FONT_HEAD, fill_hex=SLATE, align=ALIGN_C)
        elif key.startswith("helper"):
            apply_cell(ws.cell(HEADER_ROW, col, layout.headers[key]), font=FONT_HEAD, fill_hex=LINE, align=ALIGN_C)
        else:
            color = NAVY
            for gtitle, start, end, gcolor in layout.groups:
                if start <= col <= end:
                    color = gcolor
                    break
            apply_cell(
                ws.cell(HEADER_ROW, col, layout.headers[key]),
                font=FONT_HEAD,
                fill_hex=color,
                align=ALIGN_C,
            )

    last_data = DATA_START + MAX_DATA_ROWS - 1

    # Pre-fill formulas for all data rows; values for provided schemes
    for offset in range(MAX_DATA_ROWS):
        row = DATA_START + offset
        scheme = schemes[offset] if offset < len(schemes) else None
        alt = ALT_ROW if offset % 2 else WHITE

        # SN
        sn_f = f'IF({layout.addr("scheme_name", row)}="","",ROW()-{DATA_START - 1})'
        cell = ws.cell(row, layout.idx["sn"], sn_f)
        apply_cell(cell, font=FONT_FORMULA, fill_hex=FORMULA_BG, align=ALIGN_C)

        # Identity / contract inputs
        for key, header, width, kind in IDENTITY_COLUMNS + CONTRACT_COLUMNS:
            col = layout.idx[key]
            if key == "sn":
                continue
            value = None
            formula = None
            if kind == "formula" and key == "planned_end_date":
                formula = planned_end_formula(layout, row)
            elif key == "awarded_date":
                awarded_i = next(
                    (i for i, slot in enumerate(layout.slots) if slot["name"] == "Awarded"),
                    None,
                )
                if awarded_i is not None:
                    src = f"{colletter(layout.status_date_cols[awarded_i])}{row}"
                    formula = f'IF({src}="","",{src})'
            elif scheme is not None:
                value = scheme.get(key)
                if key.endswith("_date"):
                    value = parse_date(value)

            cell = ws.cell(row, col)
            if formula is not None:
                cell.value = formula
                apply_cell(cell, font=FONT_FORMULA, fill_hex=FORMULA_BG, align=ALIGN_C, fmt="DD-MMM-YYYY")
            else:
                cell.value = value
                bg = alt if kind != "formula" else FORMULA_BG
                num_fmt = None
                align = ALIGN_L
                if kind == "date" or key.endswith("_date"):
                    num_fmt = "DD-MMM-YYYY"
                    align = ALIGN_C
                elif kind in ("number", "percent"):
                    num_fmt = "#,##0" if key == "contract_cost_usd" else "0"
                    align = ALIGN_C
                apply_cell(cell, font=FONT_BODY, fill_hex=bg, align=align, fmt=num_fmt)

        # Live status formulas
        for key, formula, fmt in (
            ("current_status", current_status_formula(layout, row), None),
            ("days_in_current", days_in_current_formula(layout, row), "0"),
            ("total_pipeline_days", total_days_formula(layout, row), "0"),
            ("over_target", over_target_formula(layout, row), "0"),
            ("schedule_health", schedule_health_formula(layout, row), None),
            ("days_vs_plan", days_vs_plan_formula(layout, row), "0"),
        ):
            cell = ws.cell(row, layout.idx[key], formula)
            apply_cell(cell, font=FONT_FORMULA, fill_hex=FORMULA_BG, align=ALIGN_C, fmt=fmt)

        # Status dates — live rows also get awarded/completed dates from the master file
        dates_map = (scheme or {}).get("status_dates")
        for i, col in enumerate(layout.status_date_cols):
            slot_name = layout.slots[i]["name"]
            value = None
            if dates_map and slot_name:
                value = parse_date(dates_map.get(slot_name))
            cell = ws.cell(row, col, value)
            bg = LIGHT_NAVY if (scheme and dates_map) else alt
            if not slot_name:
                bg = SPARE_FILL
            apply_cell(cell, font=FONT_BODY, fill_hex=bg, align=ALIGN_C, fmt="DD-MMM-YYYY")

        # Durations
        for i, col in enumerate(layout.duration_cols, start=1):
            cell = ws.cell(row, col, duration_formula(layout, row, i))
            apply_cell(cell, font=FONT_FORMULA, fill_hex=FORMULA_BG, align=ALIGN_C, fmt="0")

        # Helpers
        ws.cell(row, layout.idx["helper_prov_range"], helper_prov_formula(layout, row))
        apply_cell(
            ws.cell(row, layout.idx["helper_prov_range"]),
            font=FONT_HINT,
            fill_hex=SPARE_FILL,
        )
        ws.cell(row, layout.idx["helper_dist_range"], helper_dist_formula(layout, row))
        apply_cell(
            ws.cell(row, layout.idx["helper_dist_range"]),
            font=FONT_HINT,
            fill_hex=SPARE_FILL,
        )

        ws.row_dimensions[row].height = 18

    # Column widths
    for key, col in layout.idx.items():
        ws.column_dimensions[colletter(col)].width = layout.widths.get(key, 14)

    # Hide helper columns
    for key in ("helper_prov_range", "helper_dist_range"):
        ws.column_dimensions[layout.letter(key)].hidden = True

    # Freeze identity + header
    # Keep identity, contract, and live status visible while scrolling status dates.
    ws.freeze_panes = f"{colletter(layout.status_date_cols[0])}{DATA_START}"
    vis_end = colletter(layout.duration_cols[-1])
    ws.auto_filter.ref = f"A{HEADER_ROW}:{vis_end}{last_data}"
    ws.auto_filter.ref = f"A{HEADER_ROW}:{vis_end}{DATA_START + max(len(schemes), 1) - 1}"
    # Keep filter on header covering the used block; Excel expands when rows are added
    ws.auto_filter.ref = f"A{HEADER_ROW}:{vis_end}{last_data}"

    ws.print_title_rows = "1:3"
    ws.print_title_cols = "A:E"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_TABLOID
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.page_setup.horizontalCentered = True
    ws.sheet_view.zoomScale = 90
    ws.oddFooter.left.text = banner
    ws.oddFooter.right.text = "Page &P of &N"

    # Validations
    def dv_list(formula, sqref, extra=None):
        dv = DataValidation(
            type="list",
            formula1=formula,
            allow_blank=True,
            showDropDown=False,
            showErrorMessage=True,
            errorTitle="Not in list",
            error="Choose a value from the list, or add it on the Domains / Geography sheet first.",
        )
        dv.add(sqref)
        ws.add_data_validation(dv)

    first = DATA_START
    last_r = last_data
    dv_list("=Projects", f"{layout.letter('project_name')}{first}:{layout.letter('project_name')}{last_r}")
    dv_list("=Interventions", f"{layout.letter('intervention_type')}{first}:{layout.letter('intervention_type')}{last_r}")
    dv_list("=Regions", f"{layout.letter('region')}{first}:{layout.letter('region')}{last_r}")
    dv_list("=Donors", f"{layout.letter('donor')}{first}:{layout.letter('donor')}{last_r}")
    dv_list("=Statuses", f"{layout.letter('reported_status')}{first}:{layout.letter('reported_status')}{last_r}")
    dv_list("=AwardGroups", f"{layout.letter('award_group')}{first}:{layout.letter('award_group')}{last_r}")
    dv_list("=Families", f"{layout.letter('intervention_family')}{first}:{layout.letter('intervention_family')}{last_r}")
    dv_list("=All_Provinces", f"{layout.letter('province')}{first}:{layout.letter('province')}{last_r}")
    dv_list("=All_Districts", f"{layout.letter('district')}{first}:{layout.letter('district')}{last_r}")

    date_sq = f"{colletter(layout.status_date_cols[0])}{first}:{colletter(layout.status_date_cols[-1])}{last_r}"
    dv_date = DataValidation(
        type="date",
        operator="greaterThanOrEqual",
        formula1="=DATE(2018,1,1)",
        allow_blank=True,
        showErrorMessage=True,
        errorTitle="Date required",
        error="Enter a calendar date (for example 15-Mar-2026).",
    )
    dv_date.add(date_sq)
    dv_date.add(f"{layout.letter('awarded_date')}{first}:{layout.letter('awarded_date')}{last_r}")
    dv_date.add(f"{layout.letter('expected_award_date')}{first}:{layout.letter('expected_award_date')}{last_r}")
    dv_date.add(f"{layout.letter('contract_end_date')}{first}:{layout.letter('contract_end_date')}{last_r}")
    dv_date.add(f"{layout.letter('actual_completion_date')}{first}:{layout.letter('actual_completion_date')}{last_r}")
    ws.add_data_validation(dv_date)

    dv_pct = DataValidation(
        type="decimal",
        operator="between",
        formula1="0",
        formula2="100",
        allow_blank=True,
        errorTitle="0-100",
        error="Physical progress must be between 0 and 100.",
        showErrorMessage=True,
    )
    dv_pct.add(f"{layout.letter('physical_progress_pct')}{first}:{layout.letter('physical_progress_pct')}{last_r}")
    ws.add_data_validation(dv_pct)

    dv_months = DataValidation(
        type="decimal",
        operator="greaterThanOrEqual",
        formula1="0",
        allow_blank=True,
        showErrorMessage=True,
        errorTitle="Months",
        error="Enter contract duration in months (for example 5).",
    )
    dv_months.add(
        f"{layout.letter('contract_duration_months')}{first}:{layout.letter('contract_duration_months')}{last_r}"
    )
    ws.add_data_validation(dv_months)

    # Conditional formatting — current status
    status_range = f"{layout.letter('current_status')}{first}:{layout.letter('current_status')}{last_r}"
    for name, color in STATUS_COLORS.items():
        font_color = WHITE if name == "Completed / Handover" else INK
        rule = CellIsRule(
            operator="equal",
            formula=[f'"{name}"'],
            fill=fill(color),
            font=Font(name="Calibri", size=10, color=font_color, bold=name == "Completed / Handover"),
        )
        ws.conditional_formatting.add(status_range, rule)

    days_range = f"{layout.letter('days_in_current')}{first}:{layout.letter('days_in_current')}{last_r}"
    ws.conditional_formatting.add(
        days_range,
        CellIsRule(
            operator="greaterThan",
            formula=[str(STUCK_THRESHOLD_DAYS)],
            fill=fill(WARN_FILL),
            font=Font(name="Calibri", size=10, color=WARN_FONT, bold=True),
        ),
    )
    over_range = f"{layout.letter('over_target')}{first}:{layout.letter('over_target')}{last_r}"
    ws.conditional_formatting.add(
        over_range,
        CellIsRule(
            operator="greaterThan",
            formula=["0"],
            fill=fill(WARN_FILL),
            font=Font(name="Calibri", size=10, color=WARN_FONT),
        ),
    )
    prog_range = f"{layout.letter('physical_progress_pct')}{first}:{layout.letter('physical_progress_pct')}{last_r}"
    ws.conditional_formatting.add(
        prog_range,
        DataBarRule(
            start_type="num",
            start_value=0,
            end_type="num",
            end_value=100,
            color=FOREST,
            showValue=True,
            minLength=None,
            maxLength=None,
        ),
    )

    health_range = f"{layout.letter('schedule_health')}{first}:{layout.letter('schedule_health')}{last_r}"
    for text, color, font_color in (
        ("On track", HEALTH_GREEN, INK),
        ("Completed — on track", HEALTH_GREEN, INK),
        ("At risk — close to off track", HEALTH_AMBER, INK),
        ("Behind — past end date", HEALTH_RED, WARN_FONT),
        ("Behind — past planned date", HEALTH_RED, WARN_FONT),
        ("Behind — award date passed", HEALTH_RED, WARN_FONT),
        ("Behind — progress lag", HEALTH_RED, WARN_FONT),
        ("Cancelled", HEALTH_GREY, INK),
    ):
        ws.conditional_formatting.add(
            health_range,
            CellIsRule(
                operator="equal",
                formula=[f'"{text}"'],
                fill=fill(color),
                font=Font(name="Calibri", size=10, color=font_color, bold="Behind" in text),
            ),
        )
    dvs_range = f"{layout.letter('days_vs_plan')}{first}:{layout.letter('days_vs_plan')}{last_r}"
    ws.conditional_formatting.add(
        dvs_range,
        CellIsRule(operator="lessThan", formula=["0"], fill=fill(HEALTH_RED), font=Font(name="Calibri", size=10, color=WARN_FONT, bold=True)),
    )
    ws.conditional_formatting.add(
        dvs_range,
        CellIsRule(operator="between", formula=["0", str(NEAR_OFFTRACK_DAYS)], fill=fill(HEALTH_AMBER), font=Font(name="Calibri", size=10, color=INK)),
    )
    ws.conditional_formatting.add(
        dvs_range,
        CellIsRule(operator="greaterThan", formula=[str(NEAR_OFFTRACK_DAYS)], fill=fill(HEALTH_GREEN), font=Font(name="Calibri", size=10, color=INK)),
    )

    # Negative duration highlight
    dur_range = f"{colletter(layout.duration_cols[0])}{first}:{colletter(layout.duration_cols[-1])}{last_r}"
    ws.conditional_formatting.add(
        dur_range,
        CellIsRule(
            operator="lessThan",
            formula=["0"],
            fill=fill(WARN_FILL),
            font=Font(name="Calibri", size=10, color=WARN_FONT),
        ),
    )

    ws.cell(HEADER_ROW, layout.idx["current_status"]).comment = Comment(
        "Latest step that has a date. If no dates are entered, uses Reported Status.",
        "Tracker",
    )
    ws.cell(HEADER_ROW, layout.idx["days_in_current"]).comment = Comment(
        f"TODAY minus the latest status date. Turns red after {STUCK_THRESHOLD_DAYS} days.",
        "Tracker",
    )
    ws.cell(HEADER_ROW, layout.idx["reported_status"]).comment = Comment(
        "Use this until official step dates are entered. Current Status follows dates once they exist.",
        "Tracker",
    )
    ws.cell(HEADER_ROW, layout.idx["schedule_health"]).comment = Comment(
        "Green = on track. Amber = within 30 days of a planned date (close to off track). "
        "Red = behind the planned award or end date, or physical progress lagging the elapsed contract time by more than 15 points.",
        "Tracker",
    )
    ws.cell(HEADER_ROW, layout.idx["days_vs_plan"]).comment = Comment(
        "Positive = days remaining until the planned award (remaining) or contract end (awarded). Negative = days behind that date.",
        "Tracker",
    )
    ws.cell(HEADER_ROW, layout.idx["awarded_date"]).comment = Comment(
        "Copies Date: Awarded. Enter the contract signature date in the Awarded status-date column.",
        "Tracker",
    )


def write_dashboard(wb: Workbook, layout: Layout) -> None:
    ws = wb.create_sheet(SHEET_DASH, 2)
    ws.sheet_properties.tabColor = GOLD
    ws.sheet_view.showGridLines = False
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.merge_cells("A1:L1")
    apply_cell(ws.cell(1, 1, "Dashboard — scheme counts and time spent in each step"), font=FONT_TITLE, fill_hex=NAVY, align=ALIGN_L)
    for col in range(2, 13):
        apply_cell(ws.cell(1, col), fill_hex=NAVY)
    ws.row_dimensions[1].height = 26
    ws.merge_cells("A2:L2")
    apply_cell(
        ws.cell(
            2,
            1,
            f"Counts use Current Status (auto). Average days ignore blanks. "
            f"Schemes with no scheme name are ignored. Red threshold for 'stuck' is {STUCK_THRESHOLD_DAYS} days.",
        ),
        font=FONT_HINT,
        fill_hex=LIGHT_NAVY,
        border=None,
    )
    for col in range(2, 13):
        ws.cell(2, col).fill = fill(LIGHT_NAVY)

    t = quote_sheet(SHEET_TRACKER)
    first = DATA_START
    last = DATA_START + MAX_DATA_ROWS - 1
    name_col = layout.letter("scheme_name")
    status_col = layout.letter("current_status")
    region_col = layout.letter("region")
    days_col = layout.letter("days_in_current")
    prog_col = layout.letter("physical_progress_pct")
    total_col = layout.letter("total_pipeline_days")
    interv_col = layout.letter("intervention_type")

    name_rng = f"{t}!${name_col}${first}:${name_col}${last}"
    status_rng = f"{t}!${status_col}${first}:${status_col}${last}"
    region_rng = f"{t}!${region_col}${first}:${region_col}${last}"
    days_rng = f"{t}!${days_col}${first}:${days_col}${last}"
    prog_rng = f"{t}!${prog_col}${first}:${prog_col}${last}"
    total_rng = f"{t}!${total_col}${first}:${total_col}${last}"
    interv_rng = f"{t}!${interv_col}${first}:${interv_col}${last}"

    # KPI row
    health_col = layout.letter("schedule_health")
    health_rng = f"{t}!${health_col}${first}:${health_col}${last}"
    kpis = [
        ("A", "C", "Schemes registered", f'COUNTA({name_rng})'),
        ("D", "F", "On track / completed", f'COUNTIF({health_rng},"On track")+COUNTIF({health_rng},"Completed — on track")'),
        ("G", "I", "At risk — close to off track", f'COUNTIF({health_rng},"At risk — close to off track")'),
        ("J", "L", "Behind planned date", f'COUNTIF({health_rng},"Behind*")'),
    ]
    ws.row_dimensions[4].height = 16
    ws.row_dimensions[5].height = 28
    for start, end, label, formula in kpis:
        ws.merge_cells(f"{start}4:{end}4")
        ws.merge_cells(f"{start}5:{end}5")
        apply_cell(ws[f"{start}4"], font=FONT_GROUP, fill_hex=STEEL, align=ALIGN_C)
        ws[f"{start}4"] = label
        for cell in ws[f"{start}4":f"{end}4"][0]:
            cell.fill = fill(STEEL)
            cell.font = FONT_GROUP
            cell.alignment = ALIGN_C
        apply_cell(ws[f"{start}5"], font=Font(name="Calibri", size=18, bold=True, color=NAVY), fill_hex=LIGHT_SLATE, align=ALIGN_C)
        ws[f"{start}5"] = f"={formula}"
        for cell in ws[f"{start}5":f"{end}5"][0]:
            cell.fill = fill(LIGHT_SLATE)
            cell.alignment = ALIGN_C
            cell.border = THIN
        if "progress" in label.lower():
            ws[f"{start}5"].number_format = '0.0'

    # Status breakdown
    apply_cell(ws.cell(7, 1, "Schemes by current status"), font=FONT_SECTION, fill_hex=LIGHT_NAVY, border=None)
    ws.merge_cells("A7:C7")
    apply_cell(ws.cell(8, 1, "Status"), font=FONT_HEAD, fill_hex=NAVY, align=ALIGN_C)
    apply_cell(ws.cell(8, 2, "Count"), font=FONT_HEAD, fill_hex=NAVY, align=ALIGN_C)
    apply_cell(ws.cell(8, 3, "Share"), font=FONT_HEAD, fill_hex=NAVY, align=ALIGN_C)

    statuses = [s["name"] for s in STATUS_PIPELINE] + ["Not started"]
    for i, name in enumerate(statuses):
        row = 9 + i
        apply_cell(ws.cell(row, 1, name), font=FONT_BODY, fill_hex=STATUS_COLORS.get(name, WHITE))
        apply_cell(ws.cell(row, 2, f'=COUNTIF({status_rng},A{row})'), font=FONT_FORMULA, fill_hex=FORMULA_BG, align=ALIGN_C, fmt="0")
        apply_cell(
            ws.cell(row, 3, f'=IF($B$5=0,"",B{row}/$B$5)'),
            font=FONT_FORMULA,
            fill_hex=FORMULA_BG,
            align=ALIGN_C,
            fmt="0%",
        )
    # B5 is first KPI which is COUNTA — wait, B5 is merged from A5:C5 which is schemes registered.
    # Use COUNTA formula cell A5.
    # Share should divide by A5 not B5. A5 holds the formula for schemes registered (merged A5:C5).
    for i, name in enumerate(statuses):
        row = 9 + i
        ws.cell(row, 3).value = f'=IF($A$5=0,"",B{row}/$A$5)'

    last_status_row = 8 + len(statuses)

    # Region breakdown
    apply_cell(ws.cell(7, 5, "Schemes by region"), font=FONT_SECTION, fill_hex=LIGHT_GREEN, border=None)
    ws.merge_cells("E7:G7")
    apply_cell(ws.cell(8, 5, "Region"), font=FONT_HEAD, fill_hex=FOREST, align=ALIGN_C)
    apply_cell(ws.cell(8, 6, "Count"), font=FONT_HEAD, fill_hex=FOREST, align=ALIGN_C)
    apply_cell(ws.cell(8, 7, "Share"), font=FONT_HEAD, fill_hex=FOREST, align=ALIGN_C)
    for i, region in enumerate(GEOGRAPHY.keys()):
        row = 9 + i
        apply_cell(ws.cell(row, 5, region), font=FONT_BODY)
        apply_cell(ws.cell(row, 6, f'=COUNTIF({region_rng},E{row})'), font=FONT_FORMULA, fill_hex=FORMULA_BG, align=ALIGN_C, fmt="0")
        apply_cell(ws.cell(row, 7, f'=IF($A$5=0,"",F{row}/$A$5)'), font=FONT_FORMULA, fill_hex=FORMULA_BG, align=ALIGN_C, fmt="0%")

    # Average days per transition
    apply_cell(ws.cell(7, 9, "Average days between steps"), font=FONT_SECTION, fill_hex=LIGHT_GOLD, border=None)
    ws.merge_cells("I7:L7")
    apply_cell(ws.cell(8, 9, "Step"), font=FONT_HEAD, fill_hex=GOLD, align=ALIGN_C)
    apply_cell(ws.cell(8, 10, "Average days"), font=FONT_HEAD, fill_hex=GOLD, align=ALIGN_C)
    apply_cell(ws.cell(8, 11, "Schemes with this step dated"), font=FONT_HEAD, fill_hex=GOLD, align=ALIGN_C)
    apply_cell(ws.cell(8, 12, "Target days"), font=FONT_HEAD, fill_hex=GOLD, align=ALIGN_C)

    pipe = quote_sheet(SHEET_PIPELINE)
    for i, col in enumerate(layout.duration_cols):
        row = 9 + i
        letter = colletter(col)
        dur_rng = f"{t}!${letter}${first}:${letter}${last}"
        date_col = colletter(layout.status_date_cols[i + 1])
        date_rng = f"{t}!${date_col}${first}:${date_col}${last}"
        # Header pulled from tracker so spare slots stay in sync
        apply_cell(
            ws.cell(row, 9, f"={t}!{letter}{HEADER_ROW}"),
            font=FONT_BODY,
            align=ALIGN_L,
        )
        apply_cell(
            ws.cell(row, 10, f'=IFERROR(AVERAGE({dur_rng}),"")'),
            font=FONT_FORMULA,
            fill_hex=FORMULA_BG,
            align=ALIGN_C,
            fmt="0.0",
        )
        apply_cell(
            ws.cell(row, 11, f"=COUNT({date_rng})"),
            font=FONT_FORMULA,
            fill_hex=FORMULA_BG,
            align=ALIGN_C,
            fmt="0",
        )
        apply_cell(
            ws.cell(row, 12, f"=IFERROR({pipe}!E{4 + i},\"\")"),
            font=FONT_FORMULA,
            fill_hex=FORMULA_BG,
            align=ALIGN_C,
            fmt="0",
        )

    # Intervention type counts
    start_iv = last_status_row + 2
    apply_cell(ws.cell(start_iv, 1, "Schemes by intervention type"), font=FONT_SECTION, fill_hex=LIGHT_NAVY, border=None)
    ws.merge_cells(start_row=start_iv, start_column=1, end_row=start_iv, end_column=3)
    apply_cell(ws.cell(start_iv + 1, 1, "Intervention type"), font=FONT_HEAD, fill_hex=NAVY, align=ALIGN_C)
    apply_cell(ws.cell(start_iv + 1, 2, "Count"), font=FONT_HEAD, fill_hex=NAVY, align=ALIGN_C)
    for i, name in enumerate(INTERVENTION_TYPES):
        row = start_iv + 2 + i
        apply_cell(ws.cell(row, 1, name), font=FONT_BODY)
        apply_cell(ws.cell(row, 2, f"=COUNTIF({interv_rng},A{row})"), font=FONT_FORMULA, fill_hex=FORMULA_BG, align=ALIGN_C, fmt="0")

    # Average total pipeline days KPI extra
    extra_row = start_iv
    apply_cell(ws.cell(extra_row, 5, "Average total pipeline days (first → last dated step)"), font=FONT_H2, fill_hex=LIGHT_SLATE, border=None)
    ws.merge_cells(start_row=extra_row, start_column=5, end_row=extra_row, end_column=7)
    apply_cell(
        ws.cell(extra_row + 1, 5, f"=IFERROR(AVERAGE({total_rng}),\"\")"),
        font=Font(name="Calibri", size=18, bold=True, color=NAVY),
        fill_hex=LIGHT_SLATE,
        align=ALIGN_C,
        fmt="0.0",
    )
    ws.merge_cells(start_row=extra_row + 1, start_column=5, end_row=extra_row + 1, end_column=7)

    apply_cell(ws.cell(extra_row + 3, 5, "How to read this dashboard"), font=FONT_H2, border=None)
    ws.merge_cells(start_row=extra_row + 4, start_column=5, end_row=extra_row + 7, end_column=12)
    apply_cell(
        ws.cell(
            extra_row + 4,
            5,
            "Current Status follows the latest date typed on 01_Scheme_Tracker. "
            "Until dates are entered, schemes sit under whatever you chose as Reported Status "
            "(or Not started). Average days between steps populate only after both ends of a step "
            "have dates — see 03_Example_Filled for a complete worked pipeline. "
            "Add or rename a status on 04_Status_Pipeline; this average-days table uses the tracker headers, so it follows.",
        ),
        font=FONT_BODY,
        align=ALIGN_L,
        border=None,
    )

    for col, w in {"A": 28, "B": 12, "C": 12, "D": 3, "E": 28, "F": 12, "G": 12, "H": 3, "I": 42, "J": 14, "K": 16, "L": 12}.items():
        ws.column_dimensions[col].width = w

    # Chart — status counts
    chart = BarChart()
    chart.type = "bar"
    chart.title = "Schemes by current status"
    chart.y_axis.title = None
    chart.x_axis.title = "Schemes"
    data = Reference(ws, min_col=2, min_row=8, max_row=last_status_row)
    cats = Reference(ws, min_col=1, min_row=9, max_row=last_status_row)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.shape = 4
    chart.legend = None
    chart.style = 10
    chart.y_axis.majorGridlines = None
    chart.dataLabels = DataLabelList()
    chart.dataLabels.showVal = True
    chart.width = 18
    chart.height = 8
    ws.add_chart(chart, "A" + str(start_iv + len(INTERVENTION_TYPES) + 4))


def add_workbook_props(wb: Workbook) -> None:
    wb.properties.title = WORKBOOK_TITLE
    wb.properties.subject = WORKBOOK_SUBTITLE
    wb.properties.creator = "Construction Works Tracker"
    wb.properties.description = (
        "Scheme-level construction tracker with status dates, duration between steps, "
        "and editable domains."
    )


def build_workbook() -> Workbook:
    layout = Layout()
    wb = Workbook()
    # remove default
    default = wb.active
    wb.remove(default)

    write_howto(wb, layout)
    write_pipeline(wb)
    domain_meta = write_domains(wb)
    geo = write_geography(wb)
    write_lookups(wb, geo)
    register_named_ranges(wb, domain_meta, geo)

    write_tracker_sheet(
        wb,
        layout,
        SHEET_TRACKER,
        SCHEMES,
        fill_example_dates=False,
        tab_color=FOREST,
        banner=f"{WORKBOOK_TITLE}  ·  live register — type dates in section 4",
    )
    write_tracker_sheet(
        wb,
        layout,
        SHEET_EXAMPLE,
        EXAMPLE_SCHEMES,
        fill_example_dates=True,
        tab_color=GOLD,
        banner="EXAMPLE ONLY — two worked schemes so you can see day counts. Do not use for reporting.",
    )
    write_dashboard(wb, layout)

    # Reorder sheets
    order = [
        SHEET_HOWTO,
        SHEET_TRACKER,
        SHEET_DASH,
        SHEET_EXAMPLE,
        SHEET_PIPELINE,
        SHEET_DOMAINS,
        SHEET_GEO,
        SHEET_LOOKUPS,
    ]
    for i, name in enumerate(order):
        wb.move_sheet(name, offset=i - wb.sheetnames.index(name))

    add_workbook_props(wb)
    wb.active = wb[SHEET_TRACKER]
    return wb


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the construction works tracker workbook.")
    parser.add_argument(
        "-o",
        "--output",
        default=str(Path(__file__).resolve().parent / "WBK_AF2_Construction_Works_Tracker.xlsx"),
        help="Output .xlsx path",
    )
    args = parser.parse_args()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    wb = build_workbook()
    wb.save(out)
    print(f"Wrote {out} ({out.stat().st_size} bytes)")
    artifact_dir = Path("/opt/cursor/artifacts")
    if artifact_dir.is_dir():
        artifact = artifact_dir / out.name
        artifact.write_bytes(out.read_bytes())
        print(f"Copied {artifact}")


if __name__ == "__main__":
    main()
