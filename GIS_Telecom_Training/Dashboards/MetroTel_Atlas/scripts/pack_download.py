#!/usr/bin/env python3
"""Build a download site + zip of MetroTel Atlas (no pycache)."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = Path("/tmp/metrotel-atlas-site")
ARTIFACTS = Path("/opt/cursor/artifacts")
ZIP_NAME = "MetroTel_Atlas_Dashboard_Template.zip"
SKIP_PARTS = {"__pycache__", ".gitignore"}
SKIP_SUFFIXES = {".pyc"}


def should_copy(path: Path) -> bool:
    if any(part in SKIP_PARTS for part in path.parts):
        return False
    return path.suffix not in SKIP_SUFFIXES


def collect_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if path.is_file() and should_copy(path.relative_to(ROOT)):
            files.append(path)
    return sorted(files)


def write_portal(site: Path, files: list[Path], zip_size: int) -> None:
    rows = []
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        size = path.stat().st_size
        rows.append(
            f'<tr><td><a download href="files/{rel}">{rel}</a></td>'
            f"<td>{size:,}</td></tr>"
        )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Download MetroTel Atlas</title>
  <style>
    :root {{
      --bg:#070b14; --panel:#121b2c; --text:#e8eef7; --muted:#8b9bb4;
      --cyan:#2ee6d6; --stroke:rgba(148,163,184,.16);
    }}
    * {{ box-sizing:border-box; }}
    body {{
      margin:0; font-family:"Segoe UI",sans-serif; color:var(--text);
      background:radial-gradient(900px 400px at 0 -10%, rgba(46,230,214,.12), transparent 50%), var(--bg);
    }}
    main {{ max-width:920px; margin:0 auto; padding:36px 20px 64px; }}
    h1 {{ margin:0 0 8px; font-size:28px; }}
    p, li {{ color:var(--muted); line-height:1.5; }}
    .hero {{
      padding:22px; border:1px solid var(--stroke); border-radius:16px;
      background:var(--panel); margin:20px 0 28px;
    }}
    a.btn {{
      display:inline-block; margin:8px 10px 0 0; padding:12px 18px;
      background:var(--cyan); color:#070b14; font-weight:700; text-decoration:none;
      border-radius:10px;
    }}
    a.ghost {{ background:transparent; color:var(--cyan); border:1px solid var(--cyan); }}
    table {{ width:100%; border-collapse:collapse; }}
    td, th {{ text-align:left; padding:8px 6px; border-bottom:1px solid var(--stroke); font-size:14px; }}
    a {{ color:var(--cyan); }}
    code {{ color:var(--cyan); }}
  </style>
</head>
<body>
<main>
  <h1>MetroTel Atlas — light briefing pack</h1>
  <p>Light-theme dashboard, scripts, sample data, and directions in one zip.</p>
  <div class="hero">
    <p><strong>Best download:</strong> the zip ({zip_size:,} bytes). Unzip, then open <code>START_HERE.md</code>.</p>
    <a class="btn" href="{ZIP_NAME}" download>Download zip</a>
    <a class="btn ghost" href="files/index.html">Open dashboard here</a>
    <a class="btn ghost" href="files/START_HERE.md">Read directions</a>
  </div>
  <h2>After unzip</h2>
  <ol>
    <li>Open <code>START_HERE.md</code></li>
    <li>Double-click <code>index.html</code> or run <code>python -m http.server 8765</code></li>
    <li>Optional: <code>python scripts/publish_to_agol.py --user YOUR_USER</code></li>
  </ol>
  <h2>Individual files</h2>
  <table>
    <thead><tr><th>File</th><th>Bytes</th></tr></thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</main>
</body>
</html>
"""
    (site / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    files = collect_files()
    if SITE.exists():
        shutil.rmtree(SITE)
    files_dir = SITE / "files"
    files_dir.mkdir(parents=True)

    for path in files:
        dest = files_dir / path.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)

    zip_path = SITE / ZIP_NAME
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, arcname=f"MetroTel_Atlas/{path.relative_to(ROOT).as_posix()}")

    write_portal(SITE, files, zip_path.stat().st_size)

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    artifact_zip = ARTIFACTS / ZIP_NAME
    shutil.copy2(zip_path, artifact_zip)
    shutil.copy2(SITE / "index.html", ARTIFACTS / "metrotel_atlas_download.html")
    shutil.copy2(ROOT / "START_HERE.md", ARTIFACTS / "START_HERE_Atlas.md")
    shutil.copy2(ROOT / "START_HERE.txt", ARTIFACTS / "START_HERE_Atlas.txt")

    repo_zip = ROOT.parent / ZIP_NAME
    shutil.copy2(zip_path, repo_zip)

    print(f"Site: {SITE}")
    print(f"Files: {len(files)}")
    print(f"Zip: {zip_path} ({zip_path.stat().st_size:,} bytes)")
    print(f"Artifact zip: {artifact_zip}")
    print(f"Repo zip: {repo_zip}")


if __name__ == "__main__":
    main()
