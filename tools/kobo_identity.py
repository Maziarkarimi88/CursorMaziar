"""Well identity: cluster by distance first, then cross-check owner names.

Same personal names appear in many provinces. Do not key wells on owner.
A visit belongs to a well when it sits within CLUSTER_M of every other
point in that well (complete linkage — no street-long chains).

Owner name is only a check after the GPS cluster exists:
  agree  = one caretaker (allowing spelling drift)
  mixed  = several distinct names at the same spot (review)
  missing = no name
"""
from __future__ import annotations

import hashlib
import re
import numpy as np
import pandas as pd

CLUSTER_M = 12.0
SOFT_MERGE_M = 50.0
FAR_GPS_M = 200.0
R_EARTH_M = 6_371_000.0


def norm_text(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).replace("\n", " ").strip().lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def phone_key(value) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    elif isinstance(value, str) and re.fullmatch(r"\d+\.0", value.strip()):
        value = value.strip()[:-2]
    digits = re.sub(r"\D", "", str(value))
    return digits.lstrip("0")


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            ins, delete, sub = cur[j - 1] + 1, prev[j] + 1, prev[j - 1] + (ca != cb)
            cur.append(min(ins, delete, sub))
        prev = cur
    return prev[-1]


def names_match(a: str, b: str) -> bool:
    """Same caretaker, allowing spelling drift — not two different people."""
    a, b = norm_text(a), norm_text(b)
    if not a or not b:
        return False
    if a == b or a.replace(" ", "") == b.replace(" ", ""):
        return True
    if min(len(a), len(b)) >= 6 and (a in b or b in a):
        return True
    if min(len(a), len(b)) >= 5 and levenshtein(a, b) <= 2:
        return True
    ta, tb = set(a.split()), set(b.split())
    if len(ta) >= 2 and len(tb) >= 2 and ta == tb:
        return True
    return False


def haversine_m(lat1, lon1, lat2, lon2) -> float:
    p1, l1, p2, l2 = map(np.radians, (float(lat1), float(lon1), float(lat2), float(lon2)))
    dlat = p2 - p1
    dlon = l2 - l1
    a = np.sin(dlat / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlon / 2) ** 2
    return float(2 * R_EARTH_M * np.arcsin(np.sqrt(min(1.0, a))))


def cluster_coords(lat: np.ndarray, lon: np.ndarray, eps_m: float = CLUSTER_M) -> np.ndarray:
    """Complete-linkage GPS clusters: every pair in a cluster is ≤ eps_m.

    Single-linkage (union-find) is not used: A–B 11 m and B–C 11 m would
    then swallow a whole street. Here A and C at 20 m stay two wells.
    """
    n = len(lat)
    if n == 0:
        return np.array([], dtype=int)
    if n == 1:
        return np.array([0], dtype=int)
    clusters: list[list[int]] = []
    for i in range(n):
        best: int | None = None
        best_d = 1e18
        for c_idx, members in enumerate(clusters):
            clat = float(np.mean(lat[members]))
            clon = float(np.mean(lon[members]))
            d_cent = haversine_m(lat[i], lon[i], clat, clon)
            if d_cent > eps_m:
                continue
            if any(haversine_m(lat[i], lon[i], lat[j], lon[j]) > eps_m for j in members):
                continue
            if d_cent < best_d:
                best, best_d = c_idx, d_cent
        if best is None:
            clusters.append([i])
        else:
            clusters[best].append(i)
    labels = np.empty(n, dtype=int)
    for k, members in enumerate(clusters):
        for i in members:
            labels[i] = k
    return labels


def _hash_id(*parts: str) -> str:
    key = "|".join(parts)
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]


def distinct_owner_count(names: list[str]) -> int:
    reps: list[str] = []
    for name in names:
        n = norm_text(name)
        if not n:
            continue
        if not any(names_match(n, r) for r in reps):
            reps.append(n)
    return len(reps)


def owner_check_status(names) -> str:
    reps = []
    for name in names:
        n = norm_text(name)
        if not n:
            continue
        if not any(names_match(n, r) for r in reps):
            reps.append(n)
    if not reps:
        return "missing"
    return "agree" if len(reps) == 1 else "mixed"


def attach_identity(df: pd.DataFrame, cluster_m: float = CLUSTER_M) -> pd.DataFrame:
    """well_id = 12 m complete-linkage site. Owner is a check, not the key."""
    out = df.copy()
    out["owner_n"] = out["owner"].map(norm_text)
    out["phone_k"] = out["phone"].map(phone_key)
    out["village_n"] = out["village"].map(norm_text)
    out["province_n"] = out["province"].map(norm_text)
    well_ids = pd.Series(index=out.index, dtype=object)
    cluster_labels = pd.Series(index=out.index, dtype=int)
    # Cluster inside each province only — names like "Gul Ahmad" stay local.
    for prov, g in out.groupby("province_n", dropna=False):
        labs = cluster_coords(g["lat"].to_numpy(), g["lon"].to_numpy(), cluster_m)
        for loc, lab in zip(g.index, labs):
            cluster_labels.at[loc] = int(lab)
            well_ids.at[loc] = _hash_id(str(prov), str(int(lab)))
    out["cluster_label"] = cluster_labels.astype(int)
    out["well_id"] = well_ids
    # Owner check per spatial well (not used to merge or split).
    check = out.groupby("well_id")["owner"].transform(lambda s: owner_check_status(s.tolist()))
    out["owner_check"] = check
    out["owner_group"] = out["well_id"]
    return out


def gps_spread_m(g: pd.DataFrame) -> float:
    if len(g) < 2:
        return 0.0
    lat, lon = g["lat"].to_numpy(), g["lon"].to_numpy()
    dmax = 0.0
    for i in range(len(lat)):
        for j in range(i + 1, len(lat)):
            dmax = max(dmax, haversine_m(lat[i], lon[i], lat[j], lon[j]))
    return dmax


def nearby_other_wells(wells: pd.DataFrame, radius_m: float = CLUSTER_M) -> pd.DataFrame:
    """Pairs of different wells whose centroids are within radius_m."""
    rows = []
    for (prov, vil), g in wells.groupby(["province", "village"], dropna=False):
        rec = g.reset_index(drop=True)
        for i in range(len(rec)):
            for j in range(i + 1, len(rec)):
                d = haversine_m(rec.at[i, "lat"], rec.at[i, "lon"], rec.at[j, "lat"], rec.at[j, "lon"])
                if d <= radius_m:
                    rows.append(
                        {
                            "province": prov,
                            "village": vil,
                            "well_id_a": rec.at[i, "well_id"],
                            "well_id_b": rec.at[j, "well_id"],
                            "distance_m": round(d, 1),
                            "owner_check_a": rec.at[i, "owner_check"] if "owner_check" in rec.columns else "",
                            "owner_check_b": rec.at[j, "owner_check"] if "owner_check" in rec.columns else "",
                            "depth_a_m": rec.at[i, "total_depth_m"] if "total_depth_m" in rec.columns else np.nan,
                            "depth_b_m": rec.at[j, "total_depth_m"] if "total_depth_m" in rec.columns else np.nan,
                            "n_visits_a": rec.at[i, "n_visits"] if "n_visits" in rec.columns else np.nan,
                            "n_visits_b": rec.at[j, "n_visits"] if "n_visits" in rec.columns else np.nan,
                        }
                    )
    cols = [
        "province",
        "village",
        "well_id_a",
        "well_id_b",
        "distance_m",
        "owner_check_a",
        "owner_check_b",
        "depth_a_m",
        "depth_b_m",
        "n_visits_a",
        "n_visits_b",
    ]
    return pd.DataFrame(rows, columns=cols)


def same_owner_splits(wells: pd.DataFrame, visits: pd.DataFrame | None = None) -> pd.DataFrame:
    """Same owner name in the same village on more than one 12 m well.

    Country-wide repeats of 'Mohammad' are ignored — we group by village.
    """
    src = visits if visits is not None else wells
    if "owner_n" not in src.columns or "village_n" not in src.columns:
        if visits is None:
            return pd.DataFrame(
                columns=[
                    "province",
                    "village",
                    "owner_n",
                    "n_wells",
                    "max_centroid_separation_m",
                    "band",
                    "well_ids",
                ]
            )
    if visits is not None:
        keys = visits.groupby(["province_n", "village_n", "owner_n"], dropna=False)["well_id"].nunique()
        multi = keys[keys >= 2]
        rows = []
        well_xy = wells.set_index("well_id")
        for (prov, vil, owner), n_w in multi.items():
            if not owner:
                continue
            wids = visits.loc[
                (visits["province_n"] == prov)
                & (visits["village_n"] == vil)
                & (visits["owner_n"] == owner),
                "well_id",
            ].unique()
            dmax = 0.0
            for i, a in enumerate(wids):
                if a not in well_xy.index:
                    continue
                for b in wids[i + 1 :]:
                    if b not in well_xy.index:
                        continue
                    dmax = max(
                        dmax,
                        haversine_m(
                            well_xy.at[a, "lat"],
                            well_xy.at[a, "lon"],
                            well_xy.at[b, "lat"],
                            well_xy.at[b, "lon"],
                        ),
                    )
            rows.append(
                {
                    "province": prov,
                    "village": vil,
                    "owner_n": owner,
                    "n_wells": int(n_w),
                    "max_centroid_separation_m": round(dmax, 1),
                    "band": (
                        "12-50m_review"
                        if dmax <= SOFT_MERGE_M
                        else ("50-200m_review" if dmax <= FAR_GPS_M else "far_likely_two_wells_or_office_gps")
                    ),
                    "well_ids": " ".join(map(str, wids)),
                }
            )
        cols = [
            "province",
            "village",
            "owner_n",
            "n_wells",
            "max_centroid_separation_m",
            "band",
            "well_ids",
        ]
        return pd.DataFrame(rows, columns=cols)
    return pd.DataFrame()


def named_review_table(visits: pd.DataFrame, nearby: pd.DataFrame, splits: pd.DataFrame) -> pd.DataFrame:
    """Local-only table with owner names for enumerator follow-up. Do not commit."""
    agg = {
        "owner": lambda s: " | ".join(sorted({norm_text(x) for x in s if norm_text(x)})),
        "phone_k": lambda s: " | ".join(sorted({x for x in s if x})),
        "village": "first",
        "province": "first",
    }
    if "owner_check" in visits.columns:
        agg["owner_check"] = "first"
    names = visits.groupby("well_id").agg(agg).reset_index().rename(columns={"phone_k": "phone"})
    return names
