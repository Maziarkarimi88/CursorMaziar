# What radius means “the same well”

**Use 15 m, complete linkage.** Not 5 m. Not GIS DBSCAN at 15 m.

GPS precision in this export is median **4.62 m**, maximum **5.0 m**. Two weekly fixes of the same standing point are often 3–8 m apart. **15 m** is about three times that precision — enough for a small cloud of repeat GPS pings, still one courtyard. Complete linkage (every pair ≤ 15 m) stops a street of houses 11 m apart from becoming one well.

## Same-owner revisit (different date, ≥5 days, same village)

2968 visits have another visit with the same caretaker name on another date.

- Median nearest neighbour: **3.2 m**
- 75th percentile: **7.3 m**
- 90th percentile: **23.0 m**

| Radius | Same-owner revisits captured | What that radius is |
|---:|---:|---|
| 5 m | 64.9% | GPS precision itself — splits true weekly revisits |
| 8 m | 76.5% | covers the 75th percentile of revisits |
| 10 m | 81.5% | about 2× GPS precision — conservative floor |
| 12 m | 83.9% | close to 15 m; previous setting |
| 15 m | 86.1% | about 3× GPS precision — **use this** |
| 20 m | 89.0% | starts reaching neighbouring compounds |

The remaining ~14% at 15 m are mostly **>20 m** (office vs field GPS, or a second well that happens to share a name). No courtyard radius joins those. Keep them as two wells and review `same_owner_splits.csv`.

## Complete-linkage well counts on this file

| Radius | Wells | 1-visit | 2+ visits | Series with ≥8 dates | Mixed-owner wells | Wells with a DTW jump | Median GPS spread |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 m | 1954 | 1259 | 695 | 9 | 116 | 60 | 3.7 m |
| 8 m | 1539 | 858 | 681 | 48 | 139 | 87 | 5.8 m |
| 10 m | 1356 | 705 | 651 | 67 | 148 | 95 | 7.2 m |
| 12 m | 1224 | 618 | 606 | 78 | 143 | 99 | 8.8 m |
| 15 m | 1081 | 533 | 548 | 99 | 140 | 100 | 10.7 m |
| 20 m | 923 | 433 | 490 | 128 | 144 | 103 | 13.3 m |

## Verdict on 5 / 10 / 12 / 15 / 20

- **5 m — too small.** Equal to the GPS precision. Your GIS 1,041 “noise” / 2,339 clustered split is this window (~5.22 m), not 15 m. It cuts weekly revisits in half (only 9 wells with ≥8 dates vs 99 at 15 m).
- **10 m — conservative floor.** About 2× precision. Captures ~82% of same-owner revisits. Use only if you want fewer mixed courtyards and can accept fewer hydrographs.
- **12 m — acceptable.** Almost the same mixed-well count as 15 m, but 21 fewer long series (78 vs 99).
- **15 m — ideal default.** 3× precision, complete linkage, DTW-jump well count unchanged from 12 m (100 vs 99). Mixed *well* count stays ~140. This is `CLUSTER_M`.
- **20 m — too large.** Mixed visits and DTW jumps rise. Typical different-owner neighbour in the same village is ~40 m; 20 m starts eating the next compound.

If the GIS tool is DBSCAN / single-linkage, **do not use 15 m**. That chains A–B–C down a street. Either run this script (complete linkage) or, in GIS, use ~8–10 m and inspect any cluster that spans more than one courtyard.

Owner name is still only a **check** after the GPS cluster exists.

Regenerate the inventory table with `python3 tools/kobo_gw.py --csv data/kobo/groundwater_monitoring.csv --scan-radii --no-plots`.
