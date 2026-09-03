"""Verify pond water-balance arithmetic used in the protocol workbook."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from catchment_fill import (  # noqa: E402
    hold_days_constant_area,
    scs_p_for_q_mm,
    scs_runoff_mm,
    simple_p_to_fill_mm,
)
from build_protocol_assets import (  # noqa: E402
    AREA,
    STAGE,
    VOL,
    area_of,
    compute_example,
    compute_i4,
    lerp,
    vol_of,
)


def test_trapezoid_volume_table():
    assert VOL[0] == 0
    # first slice 0–0.5 m: (0.5)/2 * (0+800) = 200
    assert abs(VOL[1] - 200) < 1e-9
    assert VOL[-1] > 6000


def test_lerp_endpoints_and_mid():
    assert area_of(0) == 0
    assert area_of(2.5) == 5500
    assert area_of(2.52) == 5500  # cap at crest
    assert abs(area_of(1.0) - 1800) < 1e-9
    mid = lerp(0.25, STAGE, AREA)
    assert abs(mid - 400) < 1e-9


def test_example_mdwir_in_literature_band():
    rows, mean_mdwir, i1, vcrest, fillings = compute_example()
    dry = [r for r in rows if r.get("dry_day")]
    assert len(dry) >= 15
    # Gravel fan: faster than Rajasthan silty beds, but still a recharge pond not a leak.
    assert 25 <= mean_mdwir <= 90
    assert i1 > vcrest * 0.5
    assert 0.5 <= fillings <= 4.0
    # Evaporation must be a small share of dry-day losses
    e_share = sum(r["evap_m3"] for r in dry) / sum(r["dV"] for r in dry)
    assert e_share < 0.25


def test_scs_invert_roundtrip():
    cn = 70
    p = 63.0
    q = scs_runoff_mm(p, cn)
    p_back = scs_p_for_q_mm(q, cn)
    assert abs(p_back - p) < 0.05
    assert scs_runoff_mm(10.0, cn) == 0.0  # below Ia
    p_simple = simple_p_to_fill_mm(23000, 2.0e6, 0.12)
    assert abs(p_simple - 95.833) < 0.1
    t = hold_days_constant_area(20000, 8000, 6.0, 25.0)
    assert 70 < t < 90


def test_i4_treated_exceeds_control():
    i4, treated, control = compute_i4()
    assert control < 0.6
    assert treated > control + 0.3
    assert abs(i4 - (treated - control)) < 1e-9


def test_dry_day_definition_skips_rain_and_spill():
    rows, *_ = compute_example()
    for r in rows:
        if r["P"] > 0 or r["overflow"] == "Y":
            assert not r["dry_day"]


if __name__ == "__main__":
    tests = [
        test_trapezoid_volume_table,
        test_lerp_endpoints_and_mid,
        test_example_mdwir_in_literature_band,
        test_scs_invert_roundtrip,
        test_i4_treated_exceeds_control,
        test_dry_day_definition_skips_rain_and_spill,
    ]
    for fn in tests:
        fn()
        print("ok", fn.__name__)
    rows, mean_mdwir, i1, vcrest, fillings = compute_example()
    i4, treated, control = compute_i4()
    print(
        f"MDWIR={mean_mdwir:.2f} mm/d  I1={i1:.0f} m3  I2={fillings:.2f}  "
        f"Vcrest={vcrest:.0f}  I4={i4:.3f} m (T={treated:.3f} C={control:.3f})"
    )
