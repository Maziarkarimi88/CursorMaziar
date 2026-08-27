"""Pack protocol files into /tmp and zip for download. Optional Chrome PDF with timeout."""
from __future__ import annotations

import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGING = Path("/tmp/check-dam-groundwater-protocol")
ZIP_PATH = Path("/tmp/check-dam-groundwater-protocol.zip")
ART = Path("/opt/cursor/artifacts")


def copy_pack():
    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True)
    pairs = [
        (ROOT / "README.md", "00_README.md"),
        (ROOT / "docs" / "FIELD_PROTOCOL_Kandahar_Zabul.md", "01_FIELD_PROTOCOL_Kandahar_Zabul.md"),
        (ROOT / "docs" / "ANNEX_A_Flood_Detention_Check_Dams.md", "02_ANNEX_A_Flood_Detention_Check_Dams.md"),
        (ROOT / "docs" / "COUNTRY_STORIES_AND_METHODS.md", "03_COUNTRY_STORIES_AND_METHODS.md"),
        (ROOT / "docs" / "forms" / "print_forms.html", "forms/print_forms.html"),
        (ROOT / "docs" / "forms" / "Form_A_Site_Setup.md", "forms/Form_A_Site_Setup.md"),
        (ROOT / "docs" / "forms" / "Form_B_Daily_Pond.md", "forms/Form_B_Daily_Pond.md"),
        (ROOT / "docs" / "forms" / "Form_C_Weekly_Wells_Karez.md", "forms/Form_C_Weekly_Wells_Karez.md"),
        (ROOT / "docs" / "forms" / "Form_D_Annual_Sediment_Scorecard.md", "forms/Form_D_Annual_Sediment_Scorecard.md"),
        (ROOT / "docs" / "forms" / "Form_E_Flood_Event.md", "forms/Form_E_Flood_Event.md"),
        (ROOT / "docs" / "forms" / "Observer_Field_Card.md", "forms/Observer_Field_Card.md"),
        (ROOT / "docs" / "forms" / "PRINT.md", "forms/PRINT.md"),
        (ROOT / "templates" / "CheckDam_Recharge_Calculator.xlsx", "calculator/CheckDam_Recharge_Calculator.xlsx"),
        (ROOT / "templates" / "README.md", "calculator/README.md"),
        (ROOT / "figures" / "sampling_layout.png", "figures/sampling_layout.png"),
        (ROOT / "figures" / "sampling_layout.svg", "figures/sampling_layout.svg"),
        (ROOT / "figures" / "calculation_flow.png", "figures/calculation_flow.png"),
        (ROOT / "figures" / "example_results.png", "figures/example_results.png"),
        (ROOT / "requirements.txt", "rebuild/requirements.txt"),
        (ROOT / "tools" / "build_protocol_assets.py", "rebuild/build_protocol_assets.py"),
    ]
    for src, rel in pairs:
        dest = STAGING / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    (STAGING / "START_HERE.txt").write_text(
        """Kandahar–Zabul check-dam groundwater assessment pack
=====================================================

START HERE

1. 01_FIELD_PROTOCOL_Kandahar_Zabul.md (or .pdf if present)
   Core SOP for wells, karez, control fan.

2. 02_ANNEX_A_Flood_Detention_Check_Dams.md (or .pdf if present)
   TWO-PAGE ANNEX for dams that only hold water for HOURS
   (flood and erosion control, not a standing pond).

3. 03_COUNTRY_STORIES_AND_METHODS.md
   How similar projects were done and what happened: Balochistan
   karez and leaky dams, Tunisia jessour, Tigray gullies, Arizona
   leaky weirs, Oman dry dams, Spain ramblas, Cyprus, Morocco,
   Yemen, Rajasthan, Loess Plateau, Kenya sand dams.

4. forms/Form_E_Flood_Event.md  and  forms/print_forms.html
   One Form E sheet per flood. Open HTML in a browser and print A4.

5. figures/sampling_layout.png
6. calculator/CheckDam_Recharge_Calculator.xlsx
   Still useful for well/karez I4–I5. Do not use daily empty-pond
   MDWIR as the main number for flood-control dams.

Flood-control KPIs: hours wet per flood, peak cut, silt, I4 vs control, I5 karez.
""",
        encoding="utf-8",
    )


def zip_pack():
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(STAGING.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(STAGING.parent))
    ART.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ZIP_PATH, ART / "check-dam-groundwater-protocol.zip")
    return ZIP_PATH.stat().st_size


def try_pdf(html: Path, pdf: Path) -> bool:
    pdf.parent.mkdir(parents=True, exist_ok=True)
    profile = Path("/tmp/chrome-pdf-profile-annex")
    profile.mkdir(exist_ok=True)
    cmd = [
        "google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        f"--user-data-dir={profile}",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf}",
        html.resolve().as_uri(),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=40)
        return pdf.exists() and pdf.stat().st_size > 1000
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    copy_pack()
    # copy existing protocol pdf if still in old staging location... skip
    n = zip_pack()
    print("staging", STAGING)
    print("zip", ZIP_PATH, n)
    print("files", sum(1 for p in STAGING.rglob("*") if p.is_file()))


if __name__ == "__main__":
    main()
