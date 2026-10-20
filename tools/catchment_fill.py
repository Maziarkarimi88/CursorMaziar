"""Rainfall-to-fill and storage-hold time for small check dams.

NRCS curve-number runoff (NEH-630) and a constant-area emptying estimate.
Units: rainfall and runoff in millimetres; areas in m²; volumes in m³.
"""

from __future__ import annotations

import math


def scs_S_mm(cn: float) -> float:
    """Potential maximum retention S (mm) from curve number."""
    if cn <= 0 or cn >= 100:
        raise ValueError("CN must be between 0 and 100 exclusive of 100")
    return 25400.0 / cn - 254.0


def scs_runoff_mm(p_mm: float, cn: float, ia_ratio: float = 0.2) -> float:
    """Direct runoff depth Q (mm) for storm rainfall P (mm)."""
    s = scs_S_mm(cn)
    ia = ia_ratio * s
    if p_mm <= ia:
        return 0.0
    return (p_mm - ia) ** 2 / (p_mm - ia + s)


def scs_p_for_q_mm(q_mm: float, cn: float, ia_ratio: float = 0.2) -> float:
    """Invert SCS-CN: rainfall P (mm) that produces runoff depth Q (mm).

    From Q = (P-Ia)^2 / (P-Ia+S) with Ia = ia_ratio * S:
    x = P-Ia satisfies x^2 - Q x - Q S = 0.
    """
    if q_mm < 0:
        raise ValueError("Q cannot be negative")
    if q_mm == 0:
        return ia_ratio * scs_S_mm(cn)
    s = scs_S_mm(cn)
    ia = ia_ratio * s
    disc = q_mm ** 2 + 4.0 * q_mm * s
    x = (q_mm + math.sqrt(disc)) / 2.0
    return x + ia


def runoff_volume_m3(q_mm: float, catchment_m2: float) -> float:
    return q_mm / 1000.0 * catchment_m2


def simple_p_to_fill_mm(
    volume_m3: float, catchment_m2: float, runoff_coeff: float
) -> float:
    """P = V / (C A). Constant C; use only as a first look."""
    if runoff_coeff <= 0 or catchment_m2 <= 0:
        raise ValueError("C and catchment must be positive")
    q_mm = volume_m3 / catchment_m2 * 1000.0
    return q_mm / runoff_coeff


def q_depth_to_fill_mm(volume_m3: float, catchment_m2: float) -> float:
    if catchment_m2 <= 0:
        raise ValueError("catchment must be positive")
    return volume_m3 / catchment_m2 * 1000.0


def hold_days_constant_area(
    volume_m3: float,
    area_m2: float,
    e_mm_d: float,
    infiltration_mm_d: float,
    seepage_m3_d: float = 0.0,
) -> float:
    """Days to empty from volume V if area stays A (upper-bound loss rate).

    Real emptying is slower because A shrinks as stage falls.
    """
    if area_m2 <= 0:
        raise ValueError("area must be positive")
    loss_m3_d = (e_mm_d + infiltration_mm_d) / 1000.0 * area_m2 + seepage_m3_d
    if loss_m3_d <= 0:
        return math.inf
    return volume_m3 / loss_m3_d


def hold_days_mean_area(
    volume_m3: float,
    area_full_m2: float,
    e_mm_d: float,
    infiltration_mm_d: float,
    seepage_m3_d: float = 0.0,
) -> float:
    """Same as constant-area but with A = A_full / 2 (rough mid-stage)."""
    return hold_days_constant_area(
        volume_m3, area_full_m2 / 2.0, e_mm_d, infiltration_mm_d, seepage_m3_d
    )
