"""
Concept diagrams for the InSAR self-learning course.

Run:  python scripts/make_figures.py
Output: figures/*.png  (only numpy + matplotlib are needed)
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

OUT = Path(__file__).resolve().parent.parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "figure.facecolor": "white",
})

C_SAT = "#1f4e79"
C_BEAM = "#f4a261"
C_GROUND = "#8ab17d"
C_ACCENT = "#e63946"
C_BOX = "#e9f2fb"
C_BOX2 = "#fff3e0"
C_BOX3 = "#e8f5e9"


def save(fig, name):
    path = OUT / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved", path)


# ---------------------------------------------------------------------------
# 01  SAR side-looking geometry
# ---------------------------------------------------------------------------
def fig_sar_geometry():
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    # ground
    ax.add_patch(Rectangle((0, 0), 10, 0.6, color=C_GROUND, alpha=0.7))
    ax.text(0.2, 0.2, "Earth surface", fontsize=10)

    # satellite
    sat_x, sat_y = 2.0, 5.2
    ax.add_patch(Rectangle((sat_x - 0.35, sat_y - 0.2), 0.7, 0.4, color=C_SAT))
    ax.add_patch(Rectangle((sat_x - 1.1, sat_y - 0.08), 0.7, 0.16, color="#a0c4ff"))
    ax.add_patch(Rectangle((sat_x + 0.4, sat_y - 0.08), 0.7, 0.16, color="#a0c4ff"))
    ax.text(sat_x - 1.1, sat_y + 0.45, "SAR satellite\n(~700 km up, ~7 km/s)", ha="left", fontsize=10)

    # flight direction (azimuth) - into the page, draw as arrow along x
    ax.add_patch(FancyArrowPatch((sat_x + 1.2, sat_y), (sat_x + 2.4, sat_y),
                                 arrowstyle="-|>", mutation_scale=18, color=C_SAT, lw=2))
    ax.text(sat_x + 2.55, sat_y, "flight direction = AZIMUTH", ha="left", va="center", fontsize=9, color=C_SAT)

    # radar beam (side-looking)
    near = (5.0, 0.6)
    far = (9.2, 0.6)
    beam = Polygon([(sat_x, sat_y - 0.2), near, far], closed=True, color=C_BEAM, alpha=0.45)
    ax.add_patch(beam)
    ax.plot([sat_x, near[0]], [sat_y - 0.2, near[1]], color=C_BEAM, lw=1.5)
    ax.plot([sat_x, far[0]], [sat_y - 0.2, far[1]], color=C_BEAM, lw=1.5)

    # nadir line
    ax.plot([sat_x, sat_x], [sat_y - 0.2, 0.6], ls="--", color="gray", lw=1)
    ax.text(sat_x + 0.05, 2.6, "nadir\n(straight down)", fontsize=9, color="gray")

    # incidence angle
    mid = ((near[0] + far[0]) / 2, 0.6)
    ax.plot([sat_x, mid[0]], [sat_y - 0.2, mid[1]], color=C_ACCENT, lw=2)
    ax.text((sat_x + mid[0]) / 2 + 0.2, (sat_y + mid[1]) / 2 + 0.2, "line of sight (LOS)\n= slant RANGE", color=C_ACCENT, fontsize=9)
    ax.plot([mid[0], mid[0]], [0.6, 2.0], ls=":", color="gray")
    ax.annotate("", xy=(mid[0] - 0.45, 1.75), xytext=(mid[0], 1.95),
                arrowprops=dict(arrowstyle="->", color="k", connectionstyle="arc3,rad=0.3"))
    ax.text(mid[0] + 0.15, 1.75, "incidence angle θ\n(~30–45°)", fontsize=9)

    # swath
    ax.add_patch(FancyArrowPatch((near[0], 0.3), (far[0], 0.3), arrowstyle="<->", mutation_scale=15, color="k"))
    ax.text((near[0] + far[0]) / 2, 0.05, "swath (~80–250 km) — the ground strip being imaged", ha="center", fontsize=9)
    ax.text(near[0], 0.75, "near range", fontsize=9)
    ax.text(far[0] - 0.9, 0.75, "far range", fontsize=9)

    ax.set_title("1. A SAR satellite looks SIDEWAYS, not straight down")
    save(fig, "01_sar_geometry.png")


# ---------------------------------------------------------------------------
# 02  Wavelength bands ruler
# ---------------------------------------------------------------------------
def fig_wavelength_bands():
    bands = [
        ("X-band", 3.1, "TerraSAR-X, COSMO-SkyMed, ICEYE, Capella"),
        ("C-band", 5.6, "Sentinel-1, ERS, Envisat, RADARSAT"),
        ("S-band", 9.4, "NISAR (S), NovaSAR"),
        ("L-band", 23.8, "ALOS-2, NISAR (L), SAOCOM"),
    ]
    fig, ax = plt.subplots(figsize=(10, 4.2))
    y = np.arange(len(bands))[::-1]
    for yi, (name, lam, sats) in zip(y, bands):
        ax.barh(yi, lam, color=C_SAT, alpha=0.75, height=0.55)
        ax.barh(yi, lam / 2, color=C_ACCENT, alpha=0.9, height=0.25)
        ax.text(lam + 0.4, yi, f"λ = {lam:.1f} cm   →  one fringe (colour cycle) = λ/2 = {lam/2:.1f} cm of motion",
                va="center", fontsize=10)
        ax.text(-0.4, yi, f"{name}\n{sats}", va="center", ha="right", fontsize=9)
    ax.set_xlim(0, 45)
    ax.set_yticks([])
    ax.set_xlabel("wavelength, centimetres")
    ax.set_title("2. Radar wavelength = the size of the tick-marks on your measuring tape")
    ax.text(0.02, -0.28, "Blue = full wavelength λ. Red = λ/2, the ground motion that produces ONE complete phase cycle (2π).\n"
            "Short wavelength (X) = very sensitive, loses coherence fast over vegetation. Long wavelength (L) = less sensitive, sees through leaves.",
            transform=ax.transAxes, fontsize=9)
    fig.subplots_adjust(left=0.3, bottom=0.3)
    save(fig, "02_wavelength_bands.png")


# ---------------------------------------------------------------------------
# 03  Complex pixel: amplitude + phase
# ---------------------------------------------------------------------------
def fig_complex_pixel():
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    # phasor
    ax = axes[0]
    A, ph = 1.0, np.deg2rad(50)
    ax.add_patch(plt.Circle((0, 0), 1, fill=False, ls="--", color="gray"))
    ax.annotate("", xy=(A * np.cos(ph), A * np.sin(ph)), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", lw=2.5, color=C_SAT))
    th = np.linspace(0, ph, 30)
    ax.plot(0.35 * np.cos(th), 0.35 * np.sin(th), color=C_ACCENT)
    ax.text(0.42, 0.12, "phase φ", color=C_ACCENT)
    ax.text(0.35, 0.75, "amplitude A\n(how bright)", color=C_SAT)
    ax.axhline(0, color="k", lw=0.8)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect("equal")
    ax.set_title("One SLC pixel = a complex number")
    ax.set_xlabel("real part")
    ax.set_ylabel("imaginary part")

    # amplitude image (speckle-like)
    rng = np.random.default_rng(0)
    amp = np.abs(rng.normal(size=(80, 80)) + 1j * rng.normal(size=(80, 80)))
    yy, xx = np.mgrid[0:80, 0:80]
    amp *= 1 + 2 * ((xx > 30) & (xx < 50) & (yy > 20) & (yy < 60))
    axes[1].imshow(amp, cmap="gray")
    axes[1].set_title("Amplitude image (what you 'see')")
    axes[1].axis("off")

    # phase image
    phase = np.angle(rng.normal(size=(80, 80)) + 1j * rng.normal(size=(80, 80)))
    axes[2].imshow(phase, cmap="hsv", vmin=-np.pi, vmax=np.pi)
    axes[2].set_title("Phase image (looks random alone!)")
    axes[2].axis("off")
    fig.suptitle("3. A SAR image stores TWO things per pixel: brightness AND phase", fontweight="bold")
    save(fig, "03_complex_pixel.png")


# ---------------------------------------------------------------------------
# 04  Synthetic aperture idea
# ---------------------------------------------------------------------------
def fig_synthetic_aperture():
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 10, 0.5, color=C_GROUND, alpha=0.7))
    target = (5, 0.5)
    ax.plot(*target, marker="*", color=C_ACCENT, markersize=18)
    ax.text(5, 0.05, "one house on the ground", ha="center", fontsize=9)
    xs = np.linspace(1.0, 9.0, 9)
    for i, x in enumerate(xs):
        alpha = 0.25 if i not in (0, 4, 8) else 1
        ax.add_patch(Rectangle((x - 0.25, 4.0), 0.5, 0.3, color=C_SAT, alpha=alpha))
        ax.plot([x, target[0]], [4.0, target[1]], color=C_BEAM, lw=1, alpha=0.6)
    ax.add_patch(FancyArrowPatch((1.0, 4.65), (9.0, 4.65), arrowstyle="<->", mutation_scale=15, color=C_SAT, lw=2))
    ax.text(5, 4.8, "the satellite keeps 'seeing' the house for a few seconds while flying ~ 10–20 km\n"
                    "→ the computer combines all echoes as if the antenna were 10–20 km long = the SYNTHETIC APERTURE",
            ha="center", fontsize=10)
    ax.text(0.2, 3.3, "Real antenna: ~12 m long\n→ blurry (km-scale) image", fontsize=10, color="gray")
    ax.text(6.4, 3.3, "Synthetic antenna: ~15 km long\n→ sharp (metre-scale) image", fontsize=10, color=C_SAT)
    ax.set_title("4. 'Synthetic aperture' = using motion to fake a gigantic antenna")
    save(fig, "04_synthetic_aperture.png")


# ---------------------------------------------------------------------------
# 07  LOS geometry
# ---------------------------------------------------------------------------
def fig_los_geometry():
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 5)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 8, 0.5, color=C_GROUND, alpha=0.7))
    g = (4.0, 0.5)
    sat = (1.2, 4.5)
    ax.add_patch(Rectangle((sat[0] - 0.3, sat[1] - 0.15), 0.6, 0.3, color=C_SAT))
    ax.plot([sat[0], g[0]], [sat[1], g[1]], color=C_ACCENT, lw=2)
    ax.text(2.0, 2.9, "line of sight (LOS)", color=C_ACCENT, rotation=-55)
    # vertical motion arrow
    ax.annotate("", xy=(g[0], g[1] - 0.0), xytext=(g[0], g[1] + 1.4),
                arrowprops=dict(arrowstyle="-|>", lw=2.5, color="k"))
    ax.text(g[0] + 0.1, g[1] + 1.2, "true motion: subsidence d (down)", fontsize=10)
    # LOS component
    theta = np.deg2rad(38)
    L = 1.4 * np.cos(theta)
    ux, uy = -np.sin(theta), np.cos(theta)
    ax.annotate("", xy=(g[0] - ux * L * 0.0, g[1]), xytext=(g[0] + ux * L, g[1] + uy * L),
                arrowprops=dict(arrowstyle="-|>", lw=2.5, color=C_ACCENT))
    ax.text(g[0] - 2.3, g[1] + 1.1, "what the radar measures:\nLOS change = d · cos(θ)", color=C_ACCENT, fontsize=10)
    ax.text(0.3, 1.6, "θ ≈ 30–45° → cos θ ≈ 0.7–0.87\n\n"
                      "Example: 10 mm real subsidence\nlooks like ~8 mm along the LOS.\n\n"
                      "Combine ASCENDING + DESCENDING\npasses to split vertical and east–west.\n"
                      "North–south motion is nearly invisible.", fontsize=9)
    ax.set_title("7. InSAR measures motion ALONG the line of sight, not straight down")
    save(fig, "07_los_geometry.png")


# ---------------------------------------------------------------------------
# 10  Processing pipeline flowchart
# ---------------------------------------------------------------------------
def box(ax, xy, w, h, text, color=C_BOX, fontsize=9):
    ax.add_patch(FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=color, ec="#33415c", lw=1.2))
    ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center", fontsize=fontsize)


def arrow(ax, p, q):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=14, color="#33415c", lw=1.5))


def elbow(ax, x_from, y_from, x_to, y_to):
    """Connector from the bottom of the last box in a row to the top of the first box in the next row."""
    y_mid = y_from - 0.42
    ax.plot([x_from, x_from, x_to], [y_from, y_mid, y_mid], color="#33415c", lw=1.5)
    arrow(ax, (x_to, y_mid), (x_to, y_to))


def fig_pipeline_flowchart():
    fig, ax = plt.subplots(figsize=(13, 7.5))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    # Stage 1: data
    steps1 = [
        "1. Pick area + dates\n(ASF Vertex search)",
        "2. Download SLC bursts\nASF().download()",
        "3. Download orbits\nEOF().download()",
        "4. Download DEM\nTiles().download_dem()",
    ]
    for i, t in enumerate(steps1):
        box(ax, (0.3 + i * 3.15, 6.2), 2.8, 1.0, t, C_BOX)
        if i < 3:
            arrow(ax, (0.3 + i * 3.15 + 2.8, 6.7), (0.3 + (i + 1) * 3.15, 6.7))
    ax.text(0.3, 7.32, "STAGE 1 — GET THE DATA  (insardev_toolkit / pygmtsar)", fontsize=10, fontweight="bold", color=C_SAT)

    # Stage 2: preprocessing
    steps2 = [
        "5. Read bursts + DEM\nS1(DATADIR, DEM=DEM)",
        "6. Coregister (align) all dates\nto one reference image",
        "7. Geocode to a map grid\n(remove topography + flat earth)",
        "8. Save cloud-ready stack\ns1.transform(ZARRDIR)  → Zarr",
    ]
    for i, t in enumerate(steps2):
        box(ax, (0.3 + i * 3.15, 4.4), 2.8, 1.0, t, C_BOX2)
        if i < 3:
            arrow(ax, (0.3 + i * 3.15 + 2.8, 4.9), (0.3 + (i + 1) * 3.15, 4.9))
    elbow(ax, 0.3 + 3 * 3.15 + 1.4, 6.2, 0.3 + 1.4, 5.4)
    ax.text(0.3, 5.47, "STAGE 2 — PREPROCESS SLCs  (insardev_pygmtsar)", fontsize=10, fontweight="bold", color="#b26a00")

    # Stage 3: interferometry
    steps3 = [
        "9. Choose pairs\nstack.baseline(days, meters)",
        "10. Interferograms + coherence\nstack.phasediff(...)\nGaussian + Goldstein + multilook",
        "11. Unwrap phase\nstack.unwrap2d_dataset()\n(or SNAPHU / 1D unwrap)",
        "12. Detrend\nphase - phase.gaussian(40 km)",
    ]
    for i, t in enumerate(steps3):
        box(ax, (0.3 + i * 3.15, 2.6), 2.8, 1.0, t, C_BOX3)
        if i < 3:
            arrow(ax, (0.3 + i * 3.15 + 2.8, 3.1), (0.3 + (i + 1) * 3.15, 3.1))
    elbow(ax, 0.3 + 3 * 3.15 + 1.4, 4.4, 0.3 + 1.4, 3.6)
    ax.text(0.3, 3.67, "STAGE 3 — INTERFEROMETRY  (insardev)", fontsize=10, fontweight="bold", color="#2e7d32")

    # Stage 4: time series + outputs
    steps4 = [
        "13. Phase → LOS displacement\nstack.displacement_los()",
        "14. Time series (SBAS/PSI)\nstack.lstsq(disp, corr)",
        "15. Velocity + STL seasonal\n.velocity()   .stl()",
        "16. Export & share\nGeoTIFF · VTK 3D · GeoJSON\nHTML web map",
    ]
    for i, t in enumerate(steps4):
        box(ax, (0.3 + i * 3.15, 0.8), 2.8, 1.0, t, "#f3e5f5")
        if i < 3:
            arrow(ax, (0.3 + i * 3.15 + 2.8, 1.3), (0.3 + (i + 1) * 3.15, 1.3))
    elbow(ax, 0.3 + 3 * 3.15 + 1.4, 2.6, 0.3 + 1.4, 1.8)
    ax.text(0.3, 1.87, "STAGE 4 — TIME SERIES & RESULTS  (insardev + xarray/rioxarray/pyvista/ipyleaflet)", fontsize=10, fontweight="bold", color="#6a1b9a")
    ax.text(0.3, 0.25, "Same recipe, different words, in PyGMTSAR: Stack.set_scenes → load_dem → compute_align → compute_geocode → phasediff → multilooking → goldstein → unwrap_snaphu → detrend → lstsq → velocity",
            fontsize=8.5, color="gray")
    ax.set_title("10. The InSAR recipe: 16 steps from satellite files to a subsidence map", pad=14)
    save(fig, "10_pipeline_flowchart.png")


# ---------------------------------------------------------------------------
# 11  Ecosystem map
# ---------------------------------------------------------------------------
def fig_ecosystem_map():
    fig, ax = plt.subplots(figsize=(15, 7))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 7)
    ax.axis("off")
    fs = 8.5

    # data sources
    box(ax, (0.3, 5.2), 3.0, 1.0, "NASA ASF / Copernicus\nSentinel-1 SLC bursts", C_BOX, fs)
    box(ax, (0.3, 3.9), 3.0, 1.0, "NASA NISAR\nRSLC HDF5 (L- and S-band)", C_BOX, fs)
    box(ax, (0.3, 2.6), 3.0, 1.0, "Orbits (EOF) · DEM (Copernicus\nGLO-30, SRTM) · land mask · map tiles", C_BOX, fs)
    ax.text(0.3, 6.35, "DATA SOURCES", fontweight="bold", color=C_SAT)

    # toolkit
    box(ax, (4.0, 3.8), 3.0, 1.9, "insardev_toolkit  (BSD)\n\nASF · EOF · Tiles\nXYZTiles · HTTP\n\n'the downloader & helpers'", C_BOX2, fs)
    for y in (5.7, 4.4, 3.1):
        arrow(ax, (3.3, y), (4.0, 4.75))

    # preprocessor
    box(ax, (7.7, 3.8), 3.0, 1.9, "insardev_pygmtsar  (BSD)\n\nS1 · Nisar · PRM\ncoregister · geocode\nsolid-Earth tides\n→ geocoded Zarr v3 stack", C_BOX2, fs)
    arrow(ax, (7.0, 4.75), (7.7, 4.75))

    # core
    box(ax, (11.4, 3.8), 3.3, 1.9, "insardev  (source-available;\nfree for students & hobby use)\n\nStack · Baseline · unwrap2d\nlstsq · SBAS · PSI · STL\nGPU via torch (CUDA / Apple MPS)", C_BOX3, fs)
    arrow(ax, (10.7, 4.75), (11.4, 4.75))

    # outputs
    box(ax, (11.4, 1.3), 3.3, 1.7, "OUTPUTS\n\nGeoTIFF (QGIS) · NetCDF\nVTK 3D (ParaView / PyVista)\nGeoJSON + HTML map (ipyleaflet)", "#f3e5f5", fs)
    arrow(ax, (13.05, 3.8), (13.05, 3.0))

    # foundations
    box(ax, (4.0, 1.3), 6.7, 1.7,
        "SCIENTIFIC PYTHON FOUNDATION (used by everything above)\n\n"
        "numpy · scipy · xarray · dask · zarr · pandas · geopandas · shapely\n"
        "rasterio / rioxarray · pyproj · opencv (cv2) · tifffile · h5py\n"
        "numba · torch · statsmodels · matplotlib", "#f5f5f5", fs)

    # legacy
    box(ax, (4.0, 0.15), 10.7, 0.8,
        "PREVIOUS GENERATION: pygmtsar (BSD) — same ideas, Sentinel-1 only, NetCDF files,\n"
        "needs GMTSAR C binaries + SNAPHU unwrapper (Docker image: pechnikov/pygmtsar)",
        "#eeeeee", fs)

    ax.set_title("11. The InSAR.dev ecosystem (Alexey Pechnikov) — who does what", pad=10)
    save(fig, "11_ecosystem_map.png")


# ---------------------------------------------------------------------------
# 12  PS vs DS
# ---------------------------------------------------------------------------
def fig_ps_vs_ds():
    rng = np.random.default_rng(3)
    t = np.arange(20)
    true_phase = np.deg2rad(6) * t  # slow steady motion
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    ps = np.angle(np.exp(1j * (true_phase + rng.normal(0, 0.15, t.size))))
    ds = np.angle(np.exp(1j * (true_phase + rng.normal(0, 1.1, t.size))))
    for ax, ph, name, col in [(axes[0], ps, "Persistent Scatterer (PS)\nbuilding corner, rock, pylon", C_SAT),
                              (axes[1], ds, "Distributed Scatterer (DS)\nfield, gravel, grass", "#b26a00")]:
        ax.plot(t, np.angle(np.exp(1j * true_phase)), "k--", lw=1, label="true phase")
        ax.plot(t, ph, "o-", color=col, label="measured phase")
        ax.set_ylim(-np.pi, np.pi)
        ax.set_xlabel("acquisition number (every 12 days)")
        ax.set_ylabel("wrapped phase, rad")
        ax.set_title(name)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(alpha=0.3)
    axes[0].text(0.5, -2.7, "stable, low noise → one pixel is enough (PSI)", fontsize=9, color=C_SAT)
    axes[1].text(0.5, -2.7, "noisy → average many pixels/pairs (SBAS, multilooking)", fontsize=9, color="#b26a00")
    fig.suptitle("12. Two kinds of pixels: PS (stable) vs DS (noisy) — Alexey's 'the physics is always the same'", fontweight="bold")
    save(fig, "12_ps_vs_ds.png")


if __name__ == "__main__":
    fig_sar_geometry()
    fig_wavelength_bands()
    fig_complex_pixel()
    fig_synthetic_aperture()
    fig_los_geometry()
    fig_pipeline_flowchart()
    fig_ecosystem_map()
    fig_ps_vs_ds()
    print("done")
