"""
Build a single-file HTML version of the course (images embedded as base64)
so it can be read offline, e-mailed, or printed to PDF.

Run:   python scripts/build_html.py
Needs: markdown, pygments   (pip install markdown pygments)
Makes: build/InSAR_Python_Training.html
"""
import base64
import mimetypes
import re
from pathlib import Path

import markdown
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "README.md"
BUILD = ROOT / "build"
BUILD.mkdir(exist_ok=True)
OUT = BUILD / "InSAR_Python_Training.html"


def github_slugify(value, separator="-"):
    """Reproduce GitHub's heading anchors so the hand-written table of contents keeps working."""
    value = value.strip().lower()
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    return value.replace(" ", separator)


def embed_images(html):
    def repl(m):
        src = m.group(1)
        path = ROOT / src
        if not path.exists():
            return m.group(0)
        mime = mimetypes.guess_type(path.name)[0] or "image/png"
        data = base64.b64encode(path.read_bytes()).decode()
        return f'src="data:{mime};base64,{data}"'
    return re.sub(r'src="(figures/[^"]+)"', repl, html)


CSS = """
:root { --ink:#1d2433; --muted:#5b6478; --accent:#1f4e79; --accent2:#e63946; --bg:#ffffff; --code:#f5f7fa; --line:#dfe4ec; }
* { box-sizing: border-box; }
body { margin:0; padding:0 1.2rem 4rem; font-family: -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
       color:var(--ink); background:var(--bg); line-height:1.6; font-size:16px; }
main { max-width: 980px; margin: 0 auto; }
h1 { font-size:2.1rem; color:var(--accent); margin-top:2rem; line-height:1.2; }
h2 { font-size:1.55rem; color:var(--accent); margin-top:3rem; padding-top:1rem; border-top:3px solid var(--accent); }
h3 { font-size:1.2rem; margin-top:2rem; color:var(--ink); }
h4 { color:var(--muted); font-weight:600; }
blockquote { border-left:5px solid var(--accent2); background:#fff5f5; margin:1.2rem 0; padding:0.6rem 1rem; color:#5a2a2e; font-style:italic; }
img { max-width:100%; height:auto; display:block; margin:1.2rem auto; border:1px solid var(--line); border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,0.06); }
table { border-collapse:collapse; width:100%; margin:1.2rem 0; font-size:0.92rem; }
th, td { border:1px solid var(--line); padding:0.45rem 0.6rem; vertical-align:top; text-align:left; }
th { background:#eef3f9; }
tr:nth-child(even) td { background:#fafbfd; }
code { font-family: "SFMono-Regular", Menlo, Consolas, "Liberation Mono", monospace; font-size:0.88em; background:var(--code); padding:0.1em 0.35em; border-radius:4px; }
pre { background:var(--code); border:1px solid var(--line); border-radius:8px; padding:0.9rem 1rem; overflow-x:auto; line-height:1.45; }
pre code { background:none; padding:0; font-size:0.85rem; }
.codehilite { background:var(--code); border-radius:8px; }
a { color:var(--accent); }
hr { border:none; border-top:1px solid var(--line); margin:2.5rem 0; }
.toc-note { color:var(--muted); font-size:0.9rem; }
@media print {
  body { font-size:11pt; }
  h2 { page-break-before: always; }
  h2:first-of-type { page-break-before: avoid; }
  pre, img, table { page-break-inside: avoid; }
  a { color:inherit; text-decoration:none; }
}
"""


def main():
    text = SRC.read_text(encoding="utf-8")
    md = markdown.Markdown(
        extensions=["extra", "toc", "sane_lists", "codehilite", "admonition"],
        extension_configs={
            "toc": {"slugify": github_slugify, "permalink": False},
            "codehilite": {"guess_lang": False, "noclasses": False},
        },
    )
    body = md.convert(text)
    body = embed_images(body)
    pyg_css = HtmlFormatter(style="friendly").get_style_defs(".codehilite")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>InSAR with Python — a self-learning course</title>
<style>{CSS}\n{pyg_css}</style>
</head>
<body>
<main>
{body}
</main>
</body>
</html>
"""
    OUT.write_text(html, encoding="utf-8")
    print("wrote", OUT, f"({OUT.stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
