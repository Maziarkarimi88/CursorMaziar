"""Distance-first 12 m clusters; owner name is a check, not the key."""
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
    phone_key,
)


def test_haversine_8m_and_40m():
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


def test_same_owner_within_12m_is_one_well():
    a = _visits()
    b = _visits(lat=35.0 + 8 / 111_320)
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


def test_different_owners_within_12m_are_one_site_mixed_check():
    """Distance is the key. Owner disagreement is a flag, not a split."""
    a = _visits()
    b = _visits(owner="Other Owner", phone="0709999999", lat=35.0 + 8 / 111_320)
    df = attach_identity(pd.concat([a, b], ignore_index=True))
    assert df["well_id"].nunique() == 1
    assert set(df["owner_check"]) == {"mixed"}


def test_village_trailing_space_does_not_collide_far_gps():
    a = _visits(village="Lala Kai", lat=37.2, lon=68.92)
    b = _visits(village="Lala Kai ", lat=36.53, lon=69.15)
    df = attach_identity(pd.concat([a, b], ignore_index=True))
    assert df["well_id"].nunique() == 2


if __name__ == "__main__":
    test_haversine_8m_and_40m()
    print("ok test_haversine_8m_and_40m")
    test_cluster_merges_within_12m_only()
    print("ok test_cluster_merges_within_12m_only")
    test_complete_linkage_does_not_chain_a_street()
    print("ok test_complete_linkage_does_not_chain_a_street")
    test_names_and_phone()
    print("ok test_names_and_phone")
    test_same_owner_within_12m_is_one_well()
    print("ok test_same_owner_within_12m_is_one_well")
    test_same_owner_40m_is_two_wells()
    print("ok test_same_owner_40m_is_two_wells")
    test_same_name_in_two_provinces_stays_two_wells()
    print("ok test_same_name_in_two_provinces_stays_two_wells")
    test_different_owners_within_12m_are_one_site_mixed_check()
    print("ok test_different_owners_within_12m_are_one_site_mixed_check")
    test_village_trailing_space_does_not_collide_far_gps()
    print("ok test_village_trailing_space_does_not_collide_far_gps")
