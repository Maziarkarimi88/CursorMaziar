# Add KPI icons to ArcGIS Dashboards indicators

Icons live in `design/icons/`. They are 24×24 line SVGs that use `currentColor`, so Dashboards can tint them.

| Indicator | File | Icon color in the indicator |
| --- | --- | --- |
| Schemes | `icon-schemes.svg` | `#E8EEF7` |
| Awarded | `icon-awarded.svg` | `#3DDC97` |
| Awarded cost | `icon-cost.svg` | `#F5C15A` |
| Area | `icon-area.svg` | `#2EE6D6` |
| Households | `icon-households.svg` | `#5B8CFF` |
| Canal km | `icon-canal.svg` | `#2EE6D6` |
| Physical works (optional) | `icon-progress.svg` | `#3DDC97` |

## Add one icon

1. Download the matching `.svg` to your computer.
2. Edit the dashboard → hover the indicator → **Configure**.
3. Open the **Indicator** tab.
4. Turn **Icon** on.
5. **Add** / **Upload** / **Custom icon** → choose the `.svg`.
6. If SVG upload is rejected, open the file in a browser → screenshot or export a **128×128 PNG**, then upload the PNG.
7. **Icon color:** paste the hex from the table (the SVG is single-color).
8. **Alignment:** **Left** of the value (Pulse style) or Top if that option exists.
9. Done → save.

Repeat for each of the six tiles. Use the same alignment on all six so the row stays even.

## If the icon is huge or tiny

Resize the indicator (Shift + click, drag the tile). Icon and value scale together. Do not use a different SVG size per tile.

## If the icon stays black on the dark tile

The upload flattened `currentColor` to black. Set **Icon color** in the Indicator tab to the hex above, or open the SVG in a text editor and replace `currentColor` with that hex, then upload again.
