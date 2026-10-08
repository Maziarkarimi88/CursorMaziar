"""15 m GPS sites; cluster_id splits different owners inside that radius."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from kobo_identity import (  # noqa: E402
    CLUSTER_M,
    attach_identity,
    attach_identity_from_near,
    attach_owner_clusters,
    cluster_coords,
    cluster_from_near_pairs,
    haversine_m,
    names_match,
    noise_vs_clustered,
    phone_key,
    single_linkage_labels,
)


def test_haversine_8m_and_40m():
    lat0, lon0 = 35.0, 69.5
    lat8 = lat0 + 8.0 / 111_320
    lat40 = lat0 + 40.0 / 111_320
    assert 7 < haversine_m(lat0, lon0, lat8, lon0) < 9
    assert 38 < haversine_m(lat0, lon0, lat40, lon0) < 42


def test_cluster_merges_within_15m_only():
    lat0, lon0 = 35.0, 69.5
    lat = np.array([lat0, lat0 + 8 / 111_320, lat0 + 14 / 111_320, lat0 + 40 / 111_320])
    lon = np.array([lon0, lon0, lon0, lon0])
    labs = cluster_coords(lat, lon, CLUSTER_M)
    assert labs[0] == labs[1] == labs[2]
    assert labs[0] != labs[3]


def test_single_linkage_chains_and_counts_noise():
    lat0, lon0 = 35.0, 69.5
    lat = np.array([lat0, lat0 + 11 / 111_320, lat0 + 22 / 111_320, lat0 + 200 / 111_320])
    lon = np.array([lon0, lon0, lon0, lon0])
    sl = single_linkage_labels(lat, lon, 15.0)
    assert sl[0] == sl[1] == sl[2]
    assert sl[0] != sl[3]
    clustered, noise, ncl = noise_vs_clustered(sl)
    assert clustered == 3 and noise == 1 and ncl == 1


def test_single_linkage_does_not_miss_pairs_just_inside_eps():
    """A pair 5.1 m apart must join at 5.2 m, including near a cell edge."""
    lat0, lon0 = 35.0, 69.5
    dlat = 5.1 / 111_320
    rng = np.random.default_rng(0)
    lats = [lat0]
    lons = [lon0]
    for _ in range(20):
        lats.append(lat0 + float(rng.uniform(-0.002, 0.002)))
        lons.append(lon0 + float(rng.uniform(-0.002, 0.002)))
    lats.append(lats[-1] + dlat)
    lons.append(lons[-1])
    sl = single_linkage_labels(np.array(lats), np.array(lons), 5.2)
    assert sl[-1] == sl[-2]


def test_near_table_complete_linkage_does_not_chain():
    """Near Table has A–B and B–C at 11 m, not A–C at 22 m → two wells."""
    lat0, lon0 = 35.0, 69.5
    lat = np.array([lat0, lat0 + 11 / 111_320, lat0 + 22 / 111_320])
    lon = np.array([lon0, lon0, lon0])
    pts = pd.DataFrame(
        {
            "OBJECTID": [1, 2, 3],
            "lat": lat,
            "lon": lon,
            "province": ["Kapisa"] * 3,
            "village": ["V"] * 3,
            "owner": ["Same Person"] * 3,
            "phone": [""] * 3,
        }
    )
    near = pd.DataFrame(
        {
            "IN_FID": [1, 2, 2, 3],
            "NEAR_FID": [2, 1, 3, 2],
            "NEAR_DIST": [11.0, 11.0, 11.0, 11.0],
        }
    )
    sl = single_linkage_labels(lat, lon, 15.0)
    assert sl[0] == sl[1] == sl[2]
    cl = cluster_from_near_pairs(lat, lon, [(0, 1), (1, 2)], 15.0)
    assert cl[0] != cl[2]
    labeled = attach_identity_from_near(pts, near)
    assert labeled["well_id"].nunique() == 2
    assert set(labeled["owner_check"]) == {"agree"}
    from near_table_wells import main as near_main
    import tempfile

    tmp = Path(tempfile.mkdtemp())
    pts.to_csv(tmp / "pts.csv", index=False)
    near.to_csv(tmp / "near.csv", index=False)
    assert near_main(["--points", str(tmp / "pts.csv"), "--near", str(tmp / "near.csv"), "--out-dir", str(tmp)]) == 0
    wells = pd.read_csv(tmp / "wells_from_near.csv")
    assert len(wells) == 2
    assert "Same Person" not in (tmp / "visits_from_near.csv").read_text(encoding="utf-8")


def test_complete_linkage_does_not_chain_a_street():
    """A–B 11 m and B–C 11 m, A–C 22 m → two wells, not one chain."""
    lat0, lon0 = 35.0, 69.5
    lat = np.array([lat0, lat0 + 11 / 111_320, lat0 + 22 / 111_320])
    lon = np.array([lon0, lon0, lon0])
    labs = cluster_coords(lat, lon, CLUSTER_M)
    assert labs[0] != labs[2]
    assert len(set(labs)) == 2


def test_names_and_phone():
    assert names_match("Malik Mohammad Rasikh", "malik mohammad rasikh")
    assert names_match("Abdul Ghafoor Rahmani", "Abdul Ghafoor Rahamni")
    assert not names_match("Saadullah", "Mostafa")
    assert phone_key("0701111111") == phone_key(701111111.0)


def _visits(**kwargs) -> pd.DataFrame:
    base = dict(
        province="Kapisa",
        village="Test Village",
        owner="Good Owner",
        phone="0701111111",
        lat=35.0,
        lon=69.5,
    )
    base.update(kwargs)
    return pd.DataFrame([base])


def test_same_owner_within_15m_is_one_well():
    a = _visits()
    b = _visits(lat=35.0 + 14 / 111_320)
    df = attach_identity(pd.concat([a, b], ignore_index=True))
    assert df["well_id"].nunique() == 1
    assert set(df["owner_check"]) == {"agree"}


def test_same_owner_40m_is_two_wells():
    a = _visits()
    b = _visits(lat=35.0 + 40 / 111_320)
    df = attach_identity(pd.concat([a, b], ignore_index=True))
    assert df["well_id"].nunique() == 2


def test_same_name_in_two_provinces_stays_two_wells():
    a = _visits(province="Kapisa", owner="Gul Ahmad", lat=35.0, lon=69.5)
    b = _visits(province="Kunduz", owner="Gul Ahmad", lat=37.1, lon=68.9)
    df = attach_identity(pd.concat([a, b], ignore_index=True))
    assert df["well_id"].nunique() == 2


def test_different_owners_within_15m_are_one_site_mixed_check():
    """GPS site stays one well_id. Owner disagreement is a flag on that site."""
    a = _visits()
    b = _visits(owner="Other Owner", phone="0709999999", lat=35.0 + 14 / 111_320)
    df = attach_identity(pd.concat([a, b], ignore_index=True))
    assert df["well_id"].nunique() == 1
    assert set(df["owner_check"]) == {"mixed"}


def test_same_owner_within_15m_is_one_cluster():
    a = _visits()
    b = _visits(lat=35.0 + 14 / 111_320)
    df = attach_owner_clusters(pd.concat([a, b], ignore_index=True))
    assert df["cluster_id"].nunique() == 1
    assert df["well_id"].nunique() == 1
    assert int(df["split_by_owner"].max()) == 0


def test_different_owners_within_15m_get_two_cluster_ids():
    a = _visits()
    b = _visits(owner="Other Owner", phone="0709999999", lat=35.0 + 14 / 111_320)
    df = attach_owner_clusters(pd.concat([a, b], ignore_index=True))
    assert df["well_id"].nunique() == 1
    assert df["cluster_id"].nunique() == 2
    assert set(df["split_by_owner"]) == {1}


def test_same_owner_40m_is_two_clusters():
    a = _visits()
    b = _visits(lat=35.0 + 40 / 111_320)
    df = attach_owner_clusters(pd.concat([a, b], ignore_index=True))
    assert df["cluster_id"].nunique() == 2
    assert df["well_id"].nunique() == 2


def test_same_name_in_two_provinces_stays_two_clusters():
    a = _visits(province="Kapisa", owner="Gul Ahmad", lat=35.0, lon=69.5)
    b = _visits(province="Kunduz", owner="Gul Ahmad", lat=37.1, lon=68.9)
    df = attach_owner_clusters(pd.concat([a, b], ignore_index=True))
    assert df["cluster_id"].nunique() == 2


def test_spelling_drift_within_15m_is_one_cluster():
    a = _visits(owner="Abdul Ghafoor Rahmani")
    b = _visits(owner="Abdul Ghafoor Rahamni", lat=35.0 + 8 / 111_320)
    df = attach_owner_clusters(pd.concat([a, b], ignore_index=True))
    assert df["cluster_id"].nunique() == 1
    assert int(df["split_by_owner"].max()) == 0


def test_missing_owner_does_not_merge_with_named_owner():
    a = _visits(owner="Good Owner")
    b = _visits(owner="", lat=35.0 + 8 / 111_320)
    df = attach_owner_clusters(pd.concat([a, b], ignore_index=True))
    assert df["cluster_id"].nunique() == 2
    assert df["well_id"].nunique() == 1


def test_village_trailing_space_does_not_collide_far_gps():
    a = _visits(village="Lala Kai", lat=37.2, lon=68.92)
    b = _visits(village="Lala Kai ", lat=36.53, lon=69.15)
    df = attach_identity(pd.concat([a, b], ignore_index=True))
    assert df["well_id"].nunique() == 2


if __name__ == "__main__":
    test_haversine_8m_and_40m()
    print("ok test_haversine_8m_and_40m")
    test_cluster_merges_within_15m_only()
    print("ok test_cluster_merges_within_15m_only")
    test_single_linkage_chains_and_counts_noise()
    print("ok test_single_linkage_chains_and_counts_noise")
    test_single_linkage_does_not_miss_pairs_just_inside_eps()
    print("ok test_single_linkage_does_not_miss_pairs_just_inside_eps")
    test_complete_linkage_does_not_chain_a_street()
    print("ok test_complete_linkage_does_not_chain_a_street")
    test_near_table_complete_linkage_does_not_chain()
    print("ok test_near_table_complete_linkage_does_not_chain")
    test_names_and_phone()
    print("ok test_names_and_phone")
    test_same_owner_within_15m_is_one_well()
    print("ok test_same_owner_within_15m_is_one_well")
    test_same_owner_40m_is_two_wells()
    print("ok test_same_owner_40m_is_two_wells")
    test_same_name_in_two_provinces_stays_two_wells()
    print("ok test_same_name_in_two_provinces_stays_two_wells")
    test_different_owners_within_15m_are_one_site_mixed_check()
    print("ok test_different_owners_within_15m_are_one_site_mixed_check")
    test_same_owner_within_15m_is_one_cluster()
    print("ok test_same_owner_within_15m_is_one_cluster")
    test_different_owners_within_15m_get_two_cluster_ids()
    print("ok test_different_owners_within_15m_get_two_cluster_ids")
    test_same_owner_40m_is_two_clusters()
    print("ok test_same_owner_40m_is_two_clusters")
    test_same_name_in_two_provinces_stays_two_clusters()
    print("ok test_same_name_in_two_provinces_stays_two_clusters")
    test_spelling_drift_within_15m_is_one_cluster()
    print("ok test_spelling_drift_within_15m_is_one_cluster")
    test_missing_owner_does_not_merge_with_named_owner()
    print("ok test_missing_owner_does_not_merge_with_named_owner")
    test_village_trailing_space_does_not_collide_far_gps()
    print("ok test_village_trailing_space_does_not_collide_far_gps")
