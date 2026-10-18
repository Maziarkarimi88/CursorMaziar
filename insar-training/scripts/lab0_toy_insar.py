"""
LAB 0 — "InSAR in a shoebox": simulate the whole InSAR idea with NumPy only.

No satellite data, no accounts, no big downloads. You build a fake sinking
town, turn the sinking into radar phase, wrap it into fringes, add noise,
measure coherence, unwrap, and finally recover the motion with a mini-SBAS
least-squares inversion — the same maths the real libraries use.

Run:   python scripts/lab0_toy_insar.py
Needs: numpy, matplotlib
Makes: figures/05_toy_interferogram.png
       figures/06_coherence_noise.png
       figures/08_baseline_network.png
       figures/09_time_series_sbas.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent.parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)

WAVELENGTH_CM = 5.5466  # Sentinel-1 C-band wavelength in centimetres
rng = np.random.default_rng(42)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def displacement_to_phase(d_cm):
    """Radar phase for a line-of-sight change d (cm). The wave travels down AND back,
    so the path changes by 2*d, and 2π of phase corresponds to one wavelength."""
    return 4 * np.pi * d_cm / WAVELENGTH_CM


def phase_to_displacement(phase):
    return phase * WAVELENGTH_CM / (4 * np.pi)


def wrap(phase):
    """Fold any phase into the interval (-π, π]. This is what the satellite actually gives you."""
    return np.angle(np.exp(1j * phase))


def gaussian_blur(z, sigma):
    """Separable Gaussian filter written with plain numpy so you can read every line.
    Works for complex arrays too (blurs real and imaginary parts) — that is exactly how
    interferograms are filtered: never blur the wrapped phase directly, blur the complex number."""
    r = int(3 * sigma)
    x = np.arange(-r, r + 1)
    k = np.exp(-0.5 * (x / sigma) ** 2)
    k /= k.sum()
    out = np.apply_along_axis(lambda row: np.convolve(row, k, mode="same"), 1, z)
    out = np.apply_along_axis(lambda col: np.convolve(col, k, mode="same"), 0, out)
    return out


def coherence(ifg, win=7):
    """Local coherence: |mean of the complex interferogram| / mean of amplitudes in a window.
    1.0 = perfectly stable phase, 0.0 = pure noise."""
    num = np.abs(gaussian_blur(ifg, win / 3))
    den = gaussian_blur(np.abs(ifg), win / 3)
    return np.clip(num / (den + 1e-12), 0, 1)


def unwrap_2d_simple(wrapped):
    """Very simple 2-D unwrapping: unwrap the middle column, then every row from it.
    Fine for clean data, breaks on noise — that is the lesson. Real software (SNAPHU,
    InSAR.dev's DCT+IRLS solver, branch-cut/max-flow) is smarter about noisy pixels."""
    out = np.empty_like(wrapped)
    mid = wrapped.shape[1] // 2
    out[:, mid] = np.unwrap(wrapped[:, mid])
    for i in range(wrapped.shape[0]):
        row = np.unwrap(wrapped[i, :])
        out[i, :] = row - row[mid] + out[i, mid]
    return out


# ---------------------------------------------------------------------------
# PART A — one interferogram of a sinking town
# ---------------------------------------------------------------------------
def part_a():
    n = 300
    y, x = np.mgrid[0:n, 0:n]
    # a subsidence "bowl": 12 cm deep, ~ 60 px wide, off-centre
    bowl = -12.0 * np.exp(-(((x - 180) ** 2 + (y - 140) ** 2) / (2 * 45 ** 2)))
    # plus a gentle regional tilt (like an orbit error or long-wavelength atmosphere)
    ramp = 0.004 * x
    true_disp = bowl + ramp  # centimetres along the line of sight

    phase = displacement_to_phase(true_disp)
    wrapped = wrap(phase)
    unwrapped = unwrap_2d_simple(wrapped)
    unwrapped -= unwrapped[0, 0]  # reference point: top-left corner is "not moving"
    recovered = phase_to_displacement(unwrapped)
    recovered -= recovered[0, 0]
    ref_true = true_disp - true_disp[0, 0]

    fig, axes = plt.subplots(1, 4, figsize=(17, 4.4))
    im0 = axes[0].imshow(ref_true, cmap="RdBu_r", vmin=-13, vmax=3)
    axes[0].set_title("A. TRUE motion (cm)\n(we made it up)")
    plt.colorbar(im0, ax=axes[0], fraction=0.046)
    im1 = axes[1].imshow(wrapped, cmap="hsv", vmin=-np.pi, vmax=np.pi)
    axes[1].set_title("B. WRAPPED phase = interferogram\neach colour cycle = 2.77 cm")
    plt.colorbar(im1, ax=axes[1], fraction=0.046)
    im2 = axes[2].imshow(unwrapped, cmap="turbo")
    axes[2].set_title("C. UNWRAPPED phase (rad)\nfringes counted and added up")
    plt.colorbar(im2, ax=axes[2], fraction=0.046)
    im3 = axes[3].imshow(recovered, cmap="RdBu_r", vmin=-13, vmax=3)
    axes[3].set_title(f"D. RECOVERED motion (cm)\nmax error {np.abs(recovered-ref_true).max():.3f} cm")
    plt.colorbar(im3, ax=axes[3], fraction=0.046)
    for ax in axes:
        ax.axis("off")
    fig.suptitle("5. From ground motion to fringes and back — a perfect (noise-free) interferogram", fontweight="bold")
    fig.savefig(OUT / "05_toy_interferogram.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Part A: fringes in the bowl =", round((phase.min() - phase.max()) / (-2 * np.pi), 1))
    return true_disp, phase


# ---------------------------------------------------------------------------
# PART B — noise, coherence and why we filter BEFORE unwrapping
# ---------------------------------------------------------------------------
def part_b(true_disp, phase):
    n = phase.shape[0]
    y, x = np.mgrid[0:n, 0:n]
    # coherence pattern: town (stable) on the left, forest (noisy) on the right, lake (no signal) top-right
    gamma = np.where(x < 150, 0.9, 0.35).astype(float)
    gamma[(x > 210) & (y < 80)] = 0.02
    # complex interferogram with noise whose strength depends on coherence
    noise_sigma = np.sqrt((1 - gamma ** 2) / (2 * np.maximum(gamma, 1e-3) ** 2))
    noisy_phase = phase + rng.normal(0, 1, phase.shape) * noise_sigma
    ifg = np.exp(1j * noisy_phase)

    coh = coherence(ifg)
    filtered = gaussian_blur(ifg, sigma=3)  # "multilooking / Gaussian filter"
    unwrapped_raw = unwrap_2d_simple(np.angle(ifg))
    unwrapped_filt = unwrap_2d_simple(np.angle(filtered))
    unwrapped_filt -= unwrapped_filt[5, 5]
    rec = phase_to_displacement(unwrapped_filt)
    ref_true = true_disp - true_disp[5, 5]
    err = np.abs(rec - ref_true)

    fig, axes = plt.subplots(2, 3, figsize=(14, 8.5))
    axes[0, 0].imshow(np.angle(ifg), cmap="hsv", vmin=-np.pi, vmax=np.pi)
    axes[0, 0].set_title("A. noisy wrapped phase\n(left: town, right: forest, corner: lake)")
    im = axes[0, 1].imshow(coh, cmap="gray", vmin=0, vmax=1)
    axes[0, 1].set_title("B. COHERENCE map (0 = garbage, 1 = perfect)")
    plt.colorbar(im, ax=axes[0, 1], fraction=0.046)
    axes[0, 2].imshow(np.angle(filtered), cmap="hsv", vmin=-np.pi, vmax=np.pi)
    axes[0, 2].set_title("C. after Gaussian filtering of the\nCOMPLEX interferogram (fringes come back)")
    axes[1, 0].imshow(unwrapped_raw, cmap="turbo")
    axes[1, 0].set_title("D. unwrapping the raw noisy phase\n→ streaks = unwrapping errors")
    im = axes[1, 1].imshow(np.where(coh > 0.3, rec, np.nan), cmap="RdBu_r", vmin=-13, vmax=3)
    axes[1, 1].set_title("E. filtered → unwrapped → motion (cm)\nonly where coherence > 0.3 (white = masked)")
    plt.colorbar(im, ax=axes[1, 1], fraction=0.046)
    im = axes[1, 2].imshow(np.where(coh > 0.3, err, np.nan), cmap="magma", vmin=0, vmax=2)
    axes[1, 2].set_title("F. error (cm) where coherence > 0.3\n(lake masked: no coherence, no answer)")
    plt.colorbar(im, ax=axes[1, 2], fraction=0.046)
    for ax in axes.ravel():
        ax.axis("off")
    fig.suptitle("6. Noise, coherence and filtering — why real InSAR needs masks and smart unwrappers", fontweight="bold")
    fig.savefig(OUT / "06_coherence_noise.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Part B: median error where coherent = %.2f cm" % np.nanmedian(np.where(coh > 0.3, err, np.nan)))


# ---------------------------------------------------------------------------
# PART C — baseline network (which pairs of dates to use?)
# ---------------------------------------------------------------------------
def make_dates(n_dates=36, repeat_days=12):
    days = np.arange(n_dates) * repeat_days
    bperp = rng.normal(0, 60, n_dates)  # perpendicular baseline in metres (orbit tube ~ ±100 m)
    return days, bperp


def sbas_pairs(days, bperp, max_days=100, max_meters=150):
    """Mimics stack.baseline(days=100, meters=150): connect every two dates that are
    close in TIME and close in SPACE (orbit position)."""
    pairs = []
    for i in range(len(days)):
        for j in range(i + 1, len(days)):
            if days[j] - days[i] <= max_days and abs(bperp[j] - bperp[i]) <= max_meters:
                pairs.append((i, j))
    return pairs


def part_c():
    days, bperp = make_dates()
    pairs = sbas_pairs(days, bperp)
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for i, j in pairs:
        ax.plot([days[i], days[j]], [bperp[i], bperp[j]], color="#33415c", lw=0.8, alpha=0.6)
    ax.scatter(days, bperp, s=60, color="#e63946", zorder=3)
    for k, (d, b) in enumerate(zip(days, bperp)):
        ax.annotate(str(k), (d, b), textcoords="offset points", xytext=(4, 4), fontsize=8)
    ax.set_xlabel("days since first image (Sentinel-1 repeats every 6–12 days)")
    ax.set_ylabel("perpendicular baseline, m\n(how far apart the two orbits were)")
    ax.set_title(f"8. SBAS baseline network: {len(days)} dates → {len(pairs)} interferograms "
                 f"(max 100 days, max 150 m)")
    ax.grid(alpha=0.3)
    fig.savefig(OUT / "08_baseline_network.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Part C: pairs =", len(pairs))
    return days, bperp, pairs


# ---------------------------------------------------------------------------
# PART D — mini-SBAS: many noisy pair measurements → one clean time series
# ---------------------------------------------------------------------------
def part_d(days, bperp, pairs):
    t_years = days / 365.25
    velocity_true = -3.0            # cm/year (sinking)
    seasonal_amp = 0.6              # cm, e.g. groundwater swelling in the wet season
    true_cum = velocity_true * t_years + seasonal_amp * np.sin(2 * np.pi * t_years)
    true_cum -= true_cum[0]

    # each interferogram measures displacement(j) - displacement(i) + noise (atmosphere etc.)
    pair_meas = np.array([true_cum[j] - true_cum[i] + rng.normal(0, 0.35) for i, j in pairs])

    # design matrix: unknowns are the displacement at each date except the first (fixed to 0)
    A = np.zeros((len(pairs), len(days) - 1))
    for r, (i, j) in enumerate(pairs):
        if j > 0:
            A[r, j - 1] += 1
        if i > 0:
            A[r, i - 1] -= 1
    # weights: pretend coherence is higher for short pairs (this is stack.lstsq(disp, corr))
    w = np.array([1.0 / (1 + (days[j] - days[i]) / 60.0) for i, j in pairs])
    sol, *_ = np.linalg.lstsq(A * w[:, None], pair_meas * w, rcond=None)
    est_cum = np.concatenate([[0.0], sol])

    # split into trend + seasonal (a tiny cousin of STL decomposition)
    B = np.column_stack([t_years, np.sin(2 * np.pi * t_years), np.cos(2 * np.pi * t_years), np.ones_like(t_years)])
    coef, *_ = np.linalg.lstsq(B, est_cum, rcond=None)
    trend = coef[0] * t_years + coef[3]
    seasonal = coef[1] * np.sin(2 * np.pi * t_years) + coef[2] * np.cos(2 * np.pi * t_years)

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    ax = axes[0]
    for (i, j), m in zip(pairs, pair_meas):
        # hang every interferogram measurement from the solved value at its first date
        ax.plot([days[i], days[j]], [est_cum[i], est_cum[i] + m], color="gray", lw=0.6, alpha=0.45)
    ax.plot(days, est_cum, "o-", color="#1f4e79", ms=4, label="least-squares solution")
    ax.set_title(f"A. {len(pairs)} interferograms (grey), each a noisy\n'change between two dates' — one curve must fit them all")
    ax.set_xlabel("days since first image")
    ax.set_ylabel("cumulative LOS displacement, cm")
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(alpha=0.3)

    ax = axes[1]
    ax.plot(days, true_cum, "k--", lw=1.5, label="truth (hidden)")
    ax.plot(days, est_cum, "o-", color="#1f4e79", label="SBAS least-squares solution")
    ax.plot(days, trend, color="#e63946", ls="--", label=f"trend: {coef[0]:.2f} cm/yr (truth {velocity_true} cm/yr)")
    ax.plot(days, seasonal + trend, color="#f4a261", lw=1, label="trend + seasonal")
    ax.set_title("B. cumulative displacement time series at one pixel")
    ax.set_xlabel("days since first image")
    ax.set_ylabel("cumulative LOS displacement, cm")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.suptitle("9. Mini-SBAS: many short, noisy pairs → one clean story of how the ground moved", fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(OUT / "09_time_series_sbas.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Part D: estimated velocity = %.2f cm/yr, RMS error = %.2f cm" % (coef[0], np.sqrt(np.mean((est_cum - true_cum) ** 2))))


if __name__ == "__main__":
    true_disp, phase = part_a()
    part_b(true_disp, phase)
    days, bperp, pairs = part_c()
    part_d(days, bperp, pairs)
    print("Lab 0 complete. Figures are in", OUT)
