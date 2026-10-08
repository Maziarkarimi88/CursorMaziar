"""Build well_id from an ArcGIS Generate Near Table (complete linkage).

Do **not** connect IN_FID–NEAR_FID as a network. That is DBSCAN / single-linkage
and chains a street. This script only groups visits when **every pair** in the
group has a Near Table row (NEAR_DIST ≤ 15 m). Owner name is a check after
the GPS group exists — it does not merge or split wells.

Export from ArcGIS Pro (see docs/ARCGIS_NEAR_TABLE_STEPS.md):

  1. Add a long field VID = ObjectID (copy, so ids stay stable).
  2. Generate Near Table, 15 m, geodesic, all neighbours.
  3. Export the point table (include OBJECTID/VID, X, Y, province, village,
     owner, dates, DTW) and the Near Table to CSV.

  python3 tools/near_table_wells.py \\
      --points visits_points.csv --near near_15m.csv --out-dir examples/kobo_gw

Joins back in Pro on OBJECTID / VID.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kobo_identity import (  # noqa: E402
    CLUSTER_M,
    attach_identity_from_near,
    attach_owner_clusters,
    same_owner_splits,
)


def _rename_point_cols(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    aliases = {
        "lat": ("lat", "Y", "POINT_Y", "point_y"),
        "lon": ("lon", "X", "POINT_X", "point_x"),
        "province": ("province", "1. Province", "Province"),
        "village": ("village", "3. Village Name", "Village"),
        "owner": ("owner", "8. Owner/caretaker name", "Owner"),
        "phone": ("phone", "9. Phone number", "Phone"),
        "meas_date": ("meas_date", "23. Date of water level measurement"),
        "wt_now": ("wt_now", "24. Current water table depth (m)"),
    }
    lower = {str(c).lower(): c for c in out.columns}
    for dest, names in aliases.items():
        if dest in out.columns:
            continue
        for name in names:
            if name.lower() in lower:
                out[dest] = out[lower[name.lower()]]
                break
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Complete-linkage wells from Generate Near Table")
    parser.add_argument("--points", type=Path, required=True, help="Exported visit points CSV (with ObjectID)")
    parser.add_argument("--near", type=Path, required=True, help="Generate Near Table CSV (IN_FID, NEAR_FID, NEAR_DIST)")
    parser.add_argument("--oid", default=None, help="ObjectID column on the points (default: OBJECTID/FID)")
    parser.add_argument("--eps", type=float, default=CLUSTER_M, help="Radius in metres (default 15)")
    parser.add_argument("--out-dir", type=Path, default=Path("examples/kobo_gw"))
    args = parser.parse_args(argv)

    points = _rename_point_cols(pd.read_csv(args.points))
    near = pd.read_csv(args.near)
    if "lat" not in points.columns or "lon" not in points.columns:
        raise SystemExit("Points CSV needs lat/Y and lon/X columns")
    if "province" not in points.columns:
        points["province"] = ""
    if "owner" not in points.columns:
        points["owner"] = ""
    if "village" not in points.columns:
        points["village"] = ""
    if "phone" not in points.columns:
        points["phone"] = ""

    oid_col = args.oid
    labeled = attach_identity_from_near(points, near, oid_col=oid_col, cluster_m=args.eps)
    labeled = attach_owner_clusters(labeled, cluster_m=args.eps)
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    pii = {"owner", "phone", "owner_n", "phone_k", "owner_rep"}
    keep = [c for c in labeled.columns if str(c).lower() not in pii]
    visits_path = out_dir / "visits_from_near.csv"
    labeled.loc[:, keep].to_csv(visits_path, index=False)

    wells = (
        labeled.groupby("well_id", sort=False)
        .agg(
            n_visits=("well_id", "size"),
            province=("province", "first"),
            village=("village", "first"),
            lat=("lat", "median"),
            lon=("lon", "median"),
            owner_check=("owner_check", "first"),
        )
        .reset_index()
    )
    wells_path = out_dir / "wells_from_near.csv"
    wells.to_csv(wells_path, index=False)

    splits = same_owner_splits(wells, labeled)
    if "owner_n" in splits.columns:
        splits = splits.drop(columns=["owner_n"])
    splits_path = out_dir / "same_owner_splits_from_near.csv"
    splits.to_csv(splits_path, index=False)

    summary = {
        "n_visits": int(len(labeled)),
        "n_wells": int(labeled["well_id"].nunique()),
        "owner_check": labeled.groupby("well_id")["owner_check"].first().value_counts().to_dict(),
        "n_single": int((wells["n_visits"] == 1).sum()),
        "n_multi": int((wells["n_visits"] >= 2).sum()),
        "eps_m": args.eps,
        "n_owner_splits": int(len(splits)),
        "n_cluster_ids": int(labeled["cluster_id"].nunique()) if "cluster_id" in labeled.columns else int(len(wells)),
        "n_sites_split_by_owner": (
            int(labeled.loc[labeled["split_by_owner"] == 1, "well_id"].nunique())
            if "split_by_owner" in labeled.columns
            else 0
        ),
        "paths": {"visits": str(visits_path), "wells": str(wells_path), "splits": str(splits_path)},
    }
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
