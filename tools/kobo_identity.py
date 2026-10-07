"""Well identity: 12 m GPS clusters, confirmed by owner/phone.

Do not cluster GPS alone. Home-dug wells in one village often sit <12 m
apart; union-find then chains a whole hamlet into one 'well' (Kunduz
Yaamchi: 40 owners). Merge two visits only when they are within CLUSTER_M
and the owner group matches (same phone, or same/fuzzy name).
"""
from __future__ import annotations

import hashlib
import re
from collections import defaultdict

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
    """Union-find clusters; use only inside one owner group (no village chaining)."""
    n = len(lat)
    if n == 0:
        return np.array([], dtype=int)
    if n == 1:
        return np.array([0], dtype=int)
    parent = np.arange(n)

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri

    cell = max(eps_m, 1.0)
    lat_cell = np.floor(lat * 111_320 / cell).astype(int)
    scale = 111_320 * np.cos(np.radians(np.clip(lat, -89.0, 89.0)))
    lon_cell = np.floor(lon * scale / cell).astype(int)
    buckets: dict[tuple[int, int], list[int]] = defaultdict(list)
    for i, key in enumerate(zip(lat_cell.tolist(), lon_cell.tolist())):
        buckets[key].append(i)
    for (a, b), idxs in buckets.items():
        neigh: list[int] = []
        for da in (-1, 0, 1):
            for db in (-1, 0, 1):
                neigh.extend(buckets.get((a + da, b + db), []))
        for i in idxs:
            for j in neigh:
                if j <= i:
                    continue
                if haversine_m(lat[i], lon[i], lat[j], lon[j]) <= eps_m:
                    union(i, j)
    roots = [find(i) for i in range(n)]
    remap = {r: k for k, r in enumerate(sorted(set(roots)))}
    return np.array([remap[r] for r in roots], dtype=int)


def _hash_id(*parts: str) -> str:
    key = "|".join(parts)
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]


def assign_owner_groups(df: pd.DataFrame) -> pd.Series:
    """Union visits in the same village if phone matches or names are fuzzy-equal.

    Different phones stay apart even when names look similar (father / son).
    """
    n = len(df)
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri

    by_village: dict[tuple[str, str], list[int]] = defaultdict(list)
    owners = df["owner"].map(norm_text).tolist()
    phones = df["phone"].map(phone_key).tolist()
    provinces = df["province"].map(norm_text).tolist()
    villages = df["village"].map(norm_text).tolist()
    for i, key in enumerate(zip(provinces, villages)):
        by_village[key].append(i)

    for idxs in by_village.values():
        phone_first: dict[str, int] = {}
        for i in idxs:
            ph = phones[i]
            if ph:
                if ph in phone_first:
                    union(i, phone_first[ph])
                else:
                    phone_first[ph] = i
        # name match only when phones do not contradict
        for a, i in enumerate(idxs):
            for j in idxs[a + 1 :]:
                if phones[i] and phones[j] and phones[i] != phones[j]:
                    continue
                if names_match(owners[i], owners[j]):
                    union(i, j)

    labels = []
    for i in range(n):
        r = find(i)
        labels.append(_hash_id(provinces[i], villages[i], str(r)))
    return pd.Series(labels, index=df.index, name="owner_group")


def attach_identity(df: pd.DataFrame, cluster_m: float = CLUSTER_M) -> pd.DataFrame:
    """Add owner_group, well_id, cluster_label. well_id = owner group + 12 m site."""
    out = df.copy()
    out["owner_n"] = out["owner"].map(norm_text)
    out["phone_k"] = out["phone"].map(phone_key)
    out["village_n"] = out["village"].map(norm_text)
    out["province_n"] = out["province"].map(norm_text)
    out["owner_group"] = assign_owner_groups(out)
    well_ids = pd.Series(index=out.index, dtype=object)
    cluster_labels = pd.Series(index=out.index, dtype=int)
    for (prov, vil, og), g in out.groupby(["province_n", "village_n", "owner_group"], dropna=False):
        labs = cluster_coords(g["lat"].to_numpy(), g["lon"].to_numpy(), cluster_m)
        for loc, lab in zip(g.index, labs):
            cluster_labels.at[loc] = int(lab)
            well_ids.at[loc] = _hash_id(str(prov), str(vil), str(og), str(int(lab)))
    out["cluster_label"] = cluster_labels.astype(int)
    out["well_id"] = well_ids
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
                            "same_owner_group": rec.at[i, "owner_group"] == rec.at[j, "owner_group"]
                            if "owner_group" in rec.columns
                            else False,
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
        "same_owner_group",
        "depth_a_m",
        "depth_b_m",
        "n_visits_a",
        "n_visits_b",
    ]
    return pd.DataFrame(rows, columns=cols)


def same_owner_splits(wells: pd.DataFrame) -> pd.DataFrame:
    """One owner group mapped to several 12 m wells — two wells, or bad GPS."""
    rows = []
    for og, g in wells.groupby("owner_group"):
        if len(g) < 2:
            continue
        rec = g.reset_index(drop=True)
        dmax = 0.0
        for i in range(len(rec)):
            for j in range(i + 1, len(rec)):
                dmax = max(
                    dmax,
                    haversine_m(rec.at[i, "lat"], rec.at[i, "lon"], rec.at[j, "lat"], rec.at[j, "lon"]),
                )
        rows.append(
            {
                "owner_group": og,
                "province": rec.at[0, "province"],
                "village": rec.at[0, "village"],
                "n_wells": int(len(rec)),
                "max_centroid_separation_m": round(dmax, 1),
                "band": (
                    "12-50m_review"
                    if dmax <= SOFT_MERGE_M
                    else ("50-200m_review" if dmax <= FAR_GPS_M else "far_likely_two_wells_or_office_gps")
                ),
                "well_ids": " ".join(rec["well_id"].astype(str)),
                "depths_m": " ".join(
                    rec["total_depth_m"].map(lambda x: "" if pd.isna(x) else f"{x:.1f}")
                )
                if "total_depth_m" in rec.columns
                else "",
            }
        )
    cols = [
        "owner_group",
        "province",
        "village",
        "n_wells",
        "max_centroid_separation_m",
        "band",
        "well_ids",
        "depths_m",
    ]
    return pd.DataFrame(rows, columns=cols)


def named_review_table(visits: pd.DataFrame, nearby: pd.DataFrame, splits: pd.DataFrame) -> pd.DataFrame:
    """Local-only table with owner names for enumerator follow-up. Do not commit."""
    names = (
        visits.groupby("well_id")
        .agg(
            owner=("owner", lambda s: " | ".join(sorted({norm_text(x) for x in s if norm_text(x)}))),
            phone=("phone_k", lambda s: " | ".join(sorted({x for x in s if x}))),
            village=("village", "first"),
            province=("province", "first"),
        )
        .reset_index()
    )
    return names
