"""12 m clustering must follow owner, not chain a village."""
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
    cluster_coords,
    haversine_m,
    names_match,
    nearby_other_wells,
    phone_key,
)


def test_haversine_8m_and_40m():
    # 1 deg lat ~ 111_320 m
    lat0, lon0 = 35.0, 69.5
    lat8 = lat0 + 8.0 / 111_320
    lat40 = lat0 + 40.0 / 111_320
    assert 7 < haversine_m(lat0, lon0, lat8, lon0) < 9
    assert 38 < haversine_m(lat0, lon0, lat40, lon0) < 42


def test_cluster_merges_within_12m_only():
    lat0, lon0 = 35.0, 69.5
    lat = np.array([lat0, lat0 + 8 / 111_320, lat0 + 40 / 111_320])
    lon = np.array([lon0, lon0, lon0])
    labs = cluster_coords(lat, lon, CLUSTER_M)
    assert labs[0] == labs[1]
    assert labs[0] != labs[2]


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


def test_same_owner_within_12m_is_one_well():
    a = _visits()
    b = _visits(lat=35.0 + 8 / 111_320)
    df = attach_identity(pd.concat([a, b], ignore_index=True))
    assert df["well_id"].nunique() == 1


def test_same_owner_40m_is_two_wells():
    a = _visits()
    b = _visits(lat=35.0 + 40 / 111_320)
    df = attach_identity(pd.concat([a, b], ignore_index=True))
    assert df["well_id"].nunique() == 2


def test_village_trailing_space_does_not_collide_far_gps():
    a = _visits(village="Lala Kai", lat=37.2, lon=68.92)
    b = _visits(village="Lala Kai ", lat=36.53, lon=69.15)
    df = attach_identity(pd.concat([a, b], ignore_index=True))
    assert df["well_id"].nunique() == 2


def test_different_owners_within_12m_stay_apart():
    a = _visits()
    b = _visits(owner="Other Owner", phone="0709999999", lat=35.0 + 8 / 111_320)
    df = attach_identity(pd.concat([a, b], ignore_index=True))
    assert df["well_id"].nunique() == 2
    wells = (
        df.groupby("well_id")
        .agg(lat=("lat", "median"), lon=("lon", "median"), province=("province", "first"), village=("village", "first"))
        .reset_index()
    )
    wells["owner_group"] = df.groupby("well_id")["owner_group"].first().to_numpy()
    wells["total_depth_m"] = 10
    wells["n_visits"] = 1
    near = nearby_other_wells(wells, radius_m=12)
    assert len(near) == 1


if __name__ == "__main__":
    test_haversine_8m_and_40m()
    print("ok test_haversine_8m_and_40m")
    test_cluster_merges_within_12m_only()
    print("ok test_cluster_merges_within_12m_only")
    test_names_and_phone()
    print("ok test_names_and_phone")
    test_same_owner_within_12m_is_one_well()
    print("ok test_same_owner_within_12m_is_one_well")
    test_same_owner_40m_is_two_wells()
    print("ok test_same_owner_40m_is_two_wells")
    test_village_trailing_space_does_not_collide_far_gps()
    print("ok test_village_trailing_space_does_not_collide_far_gps")
    test_different_owners_within_12m_stay_apart()
    print("ok test_different_owners_within_12m_stay_apart")
