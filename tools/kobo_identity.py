"""Well identity: 15 m GPS first, then split on owner/caretaker.

Same personal names appear in many provinces. Do not key wells on owner
nationwide. A visit belongs to a GPS **site** (`well_id` / `site_id`) when
it sits within CLUSTER_M of every other point (complete linkage — no
street-long chains).

`cluster_id` is the monitoring well: 15 m complete linkage **inside** one
owner/caretaker (spelling drift allowed). Two names within 15 m become two
cluster_ids. Owner check on the GPS site stays:
  agree  = one caretaker (allowing spelling drift)
  mixed  = several distinct names at the same spot (split into cluster_ids)
  missing = no name
"""
from __future__ import annotations

import hashlib
import re
from collections import Counter

import numpy as np
import pandas as pd

CLUSTER_M = 15.0
SOFT_MERGE_M = 50.0
FAR_GPS_M = 200.0
R_EARTH_M = 6_371_000.0
MISSING_OWNER_REP = "__missing__"


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
    if min(len(a), len(b)) >= 6 and levenshtein(a, b) <= 2:
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


def cluster_from_near_pairs(
    lat: np.ndarray,
    lon: np.ndarray,
    pairs: list[tuple[int, int]],
    eps_m: float = CLUSTER_M,
) -> np.ndarray:
    """Complete linkage using Generate Near Table pairs (IN_FID–NEAR_FID).

    An edge means NEAR_DIST ≤ eps_m. A visit joins a cluster only if it has
    an edge to **every** member (no A–B–C street chain). Isolates stay as
    their own well. Connecting the Near Table as a network (union-find)
    would recreate DBSCAN — do not do that.
    """
    n = len(lat)
    if n == 0:
        return np.array([], dtype=int)
    adj: list[set[int]] = [set() for _ in range(n)]
    for i, j in pairs:
        if i == j or i < 0 or j < 0 or i >= n or j >= n:
            continue
        adj[i].add(j)
        adj[j].add(i)
    clusters: list[list[int]] = []
    for i in range(n):
        best: int | None = None
        best_d = 1e18
        for c_idx, members in enumerate(clusters):
            if any(j not in adj[i] for j in members):
                continue
            clat = float(np.mean(lat[members]))
            clon = float(np.mean(lon[members]))
            d_cent = haversine_m(lat[i], lon[i], clat, clon)
            if d_cent > eps_m:
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


def _pick_col(df: pd.DataFrame, *names: str) -> str:
    lower = {str(c).lower(): c for c in df.columns}
    for name in names:
        if name.lower() in lower:
            return lower[name.lower()]
    raise KeyError(f"Need one of {names}; got {list(df.columns)}")


def near_table_pairs(near: pd.DataFrame, oid_to_index: dict[int, int], eps_m: float = CLUSTER_M) -> list[tuple[int, int]]:
    """Turn ArcGIS Generate Near Table rows into index pairs ≤ eps_m."""
    in_c = _pick_col(near, "IN_FID", "IN_OBJECTID", "INID")
    near_c = _pick_col(near, "NEAR_FID", "NEAR_OBJECTID", "NEARID")
    dist_c = _pick_col(near, "NEAR_DIST", "NEAR_DISTANCE", "DISTANCE")
    pairs: list[tuple[int, int]] = []
    for in_fid, near_fid, dist in zip(near[in_c].tolist(), near[near_c].tolist(), near[dist_c].tolist()):
        try:
            a, b, d = int(in_fid), int(near_fid), float(dist)
        except (TypeError, ValueError):
            continue
        if d < 0 or d > eps_m or a == b:
            continue
        if a not in oid_to_index or b not in oid_to_index:
            continue
        pairs.append((oid_to_index[a], oid_to_index[b]))
    return pairs


def attach_identity_from_near(
    df: pd.DataFrame,
    near: pd.DataFrame,
    oid_col: str | None = None,
    cluster_m: float = CLUSTER_M,
) -> pd.DataFrame:
    """Same well_id rule as attach_identity, but edges come from a Near Table."""
    out = df.copy()
    out["owner_n"] = out["owner"].map(norm_text) if "owner" in out.columns else ""
    out["phone_k"] = out["phone"].map(phone_key) if "phone" in out.columns else ""
    out["village_n"] = out["village"].map(norm_text) if "village" in out.columns else ""
    out["province_n"] = out["province"].map(norm_text) if "province" in out.columns else ""
    if oid_col is None:
        oid_col = _pick_col(out, "OBJECTID", "ObjectID", "OID", "FID", "oid")
    well_ids = pd.Series(index=out.index, dtype=object)
    cluster_labels = pd.Series(index=out.index, dtype=int)
    for prov, g in out.groupby("province_n", dropna=False):
        local_oids = g[oid_col].astype(int).tolist()
        oid_to_index = {int(oid): k for k, oid in enumerate(local_oids)}
        pairs = near_table_pairs(near, oid_to_index, cluster_m)
        labs = cluster_from_near_pairs(
            g["lat"].to_numpy(), g["lon"].to_numpy(), pairs, cluster_m
        )
        for loc, lab in zip(g.index, labs):
            cluster_labels.at[loc] = int(lab)
            well_ids.at[loc] = _hash_id(str(prov), str(int(lab)))
    out["cluster_label"] = cluster_labels.astype(int)
    out["well_id"] = well_ids
    if "owner" in out.columns:
        check = out.groupby("well_id")["owner"].transform(lambda s: owner_check_status(s.tolist()))
        out["owner_check"] = check
    else:
        out["owner_check"] = "missing"
    out["owner_group"] = out["well_id"]
    return out


def single_linkage_labels(lat: np.ndarray, lon: np.ndarray, eps_m: float = CLUSTER_M) -> np.ndarray:
    """DBSCAN-style clusters with min_samples=2: join every pair ≤ eps_m (chaining allowed)."""
    n = len(lat)
    if n == 0:
        return np.array([], dtype=int)
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

    # Cells smaller than eps, and a 5×5 neighbourhood, so a pair at distance
    # eps is not missed when the metre-per-degree conversion is a little off.
    cell = max(eps_m * 0.6, 1.0)
    lat_c = np.floor(lat * 111_320 / cell).astype(int)
    lon_c = np.floor(lon * 111_320 * np.cos(np.radians(np.clip(lat, -89.0, 89.0))) / cell).astype(int)
    buckets: dict[tuple[int, int], list[int]] = {}
    for i, key in enumerate(zip(lat_c.tolist(), lon_c.tolist())):
        buckets.setdefault(key, []).append(i)
    for (a, b), idxs in buckets.items():
        neigh: list[int] = []
        for da in (-2, -1, 0, 1, 2):
            for db in (-2, -1, 0, 1, 2):
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


def noise_vs_clustered(labels: np.ndarray) -> tuple[int, int, int]:
    """Return (clustered_points, singleton_points, n_clusters_of_2plus)."""
    if len(labels) == 0:
        return 0, 0, 0
    sizes = pd.Series(labels).value_counts()
    return int(sizes[sizes >= 2].sum()), int((sizes == 1).sum()), int((sizes >= 2).sum())


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


def owner_reps_for_names(names: list[str]) -> list[str]:
    """Stable caretaker key: spelling-drift names share one rep; blanks are missing."""
    norms = [norm_text(n) for n in names]
    unique: list[str] = []
    seen: set[str] = set()
    for n in norms:
        if n and n not in seen:
            unique.append(n)
            seen.add(n)
    if not unique:
        return [MISSING_OWNER_REP] * len(names)
    parent = {u: u for u in unique}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i, a in enumerate(unique):
        for b in unique[i + 1 :]:
            if names_match(a, b):
                union(a, b)
    counts = Counter(n for n in norms if n)
    groups: dict[str, list[str]] = {}
    for u in unique:
        groups.setdefault(find(u), []).append(u)
    canon: dict[str, str] = {}
    for members in groups.values():
        rep = sorted(members, key=lambda m: (-counts[m], m))[0]
        for m in members:
            canon[m] = rep
    return [canon[n] if n else MISSING_OWNER_REP for n in norms]


def attach_owner_clusters(df: pd.DataFrame, cluster_m: float = CLUSTER_M) -> pd.DataFrame:
    """cluster_id = 15 m complete linkage within one owner/caretaker.

    `well_id` / `site_id` stay the GPS-only courtyard. Different owners inside
    that radius get different `cluster_id`s. Missing names cluster together
    by GPS only. Spelling drift (`names_match`) stays one cluster.
    """
    if "well_id" not in df.columns:
        out = attach_identity(df, cluster_m=cluster_m)
    else:
        out = df.copy()
        if "owner" in out.columns and "owner_n" not in out.columns:
            out["owner_n"] = out["owner"].map(norm_text)
        if "province_n" not in out.columns:
            out["province_n"] = out["province"].map(norm_text) if "province" in out.columns else ""
    if "owner" not in out.columns:
        out["owner"] = ""
    out["site_id"] = out["well_id"]
    owner_rep = pd.Series(index=out.index, dtype=object)
    for _prov, g in out.groupby("province_n", dropna=False):
        reps = owner_reps_for_names(g["owner"].tolist())
        for loc, rep in zip(g.index, reps):
            owner_rep.at[loc] = rep
    out["owner_rep"] = owner_rep
    cluster_ids = pd.Series(index=out.index, dtype=object)
    cluster_labels = pd.Series(index=out.index, dtype=int)
    for (prov, orep), g in out.groupby(["province_n", "owner_rep"], dropna=False):
        labs = cluster_coords(g["lat"].to_numpy(), g["lon"].to_numpy(), cluster_m)
        for loc, lab in zip(g.index, labs):
            cluster_labels.at[loc] = int(lab)
            cluster_ids.at[loc] = _hash_id(str(prov), str(orep), str(int(lab)))
    out["owner_cluster_label"] = cluster_labels.astype(int)
    out["cluster_id"] = cluster_ids
    n_cid = out.groupby("site_id")["cluster_id"].transform("nunique")
    out["split_by_owner"] = (n_cid > 1).astype(int)
    return number_cluster_ids(out)


def number_cluster_ids(df: pd.DataFrame, id_col: str = "cluster_id") -> pd.DataFrame:
    """Replace hashed cluster keys with 01, 02, … N (zero-padded).

    Order is stable: province, then median lat, lon, then first date.
    `n_monitorings` is the visit count in that cluster.
    """
    out = df.copy()
    if id_col not in out.columns or out[id_col].isna().all():
        return out
    out["cluster_key"] = out[id_col].astype(str)
    rows = []
    for key, g in out.groupby("cluster_key", sort=False):
        first_date = pd.NaT
        if "meas_date" in g.columns:
            first_date = pd.to_datetime(g["meas_date"], errors="coerce").min()
        rows.append(
            {
                "cluster_key": key,
                "province": str(g["province"].iloc[0]) if "province" in g.columns else "",
                "lat": float(pd.to_numeric(g["lat"], errors="coerce").median()) if "lat" in g.columns else 0.0,
                "lon": float(pd.to_numeric(g["lon"], errors="coerce").median()) if "lon" in g.columns else 0.0,
                "first_date": first_date,
            }
        )
    order = pd.DataFrame(rows)
    order = order.sort_values(
        ["province", "lat", "lon", "first_date", "cluster_key"],
        kind="mergesort",
        na_position="last",
    )
    mapping = {k: f"{i:02d}" for i, k in enumerate(order["cluster_key"].tolist(), start=1)}
    out[id_col] = out["cluster_key"].map(mapping)
    out["n_monitorings"] = out.groupby(id_col, sort=False)[id_col].transform("size").astype(int)
    return out


def owner_split_sites(visits: pd.DataFrame) -> pd.DataFrame:
    """GPS sites that hold more than one owner-split cluster_id. No names."""
    need = {"site_id", "cluster_id", "split_by_owner", "lat", "lon"}
    if not need.issubset(visits.columns):
        return pd.DataFrame(
            columns=[
                "site_id",
                "n_clusters",
                "n_visits",
                "province",
                "village",
                "lat",
                "lon",
                "cluster_ids",
            ]
        )
    rows = []
    hit = visits.loc[visits["split_by_owner"] == 1]
    for site, g in hit.groupby("site_id"):
        cids = sorted(g["cluster_id"].astype(str).unique())
        villages = sorted({str(v).strip() for v in g["village"].dropna().astype(str) if str(v).strip()}) if "village" in g.columns else []
        provinces = sorted({str(v).strip() for v in g["province"].dropna().astype(str) if str(v).strip()}) if "province" in g.columns else []
        rows.append(
            {
                "site_id": site,
                "n_clusters": int(len(cids)),
                "n_visits": int(len(g)),
                "province": "; ".join(provinces)[:80],
                "village": villages[0] if len(villages) == 1 else (f"several ({len(villages)})" if villages else ""),
                "lat": round(float(g["lat"].median()), 6),
                "lon": round(float(g["lon"].median()), 6),
                "cluster_ids": " ".join(cids),
            }
        )
    cols = [
        "site_id",
        "n_clusters",
        "n_visits",
        "province",
        "village",
        "lat",
        "lon",
        "cluster_ids",
    ]
    out = pd.DataFrame(rows, columns=cols)
    if len(out):
        out = out.sort_values(["n_clusters", "n_visits"], ascending=False)
    return out


def attach_identity(df: pd.DataFrame, cluster_m: float = CLUSTER_M) -> pd.DataFrame:
    """well_id = 15 m complete-linkage site. Owner is a check, not the key."""
    out = df.copy()
    out["owner_n"] = out["owner"].map(norm_text)
    out["phone_k"] = out["phone"].map(phone_key)
    out["village_n"] = out["village"].map(norm_text)
    out["province_n"] = out["province"].map(norm_text)
    well_ids = pd.Series(index=out.index, dtype=object)
    cluster_labels = pd.Series(index=out.index, dtype=int)
    # Cluster inside each province only — names like "Gul Ahmad" stay local.
    # GPS is the key. Owner is applied after this loop as owner_check.
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
    """Same owner name in the same village on more than one 15 m well.

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
