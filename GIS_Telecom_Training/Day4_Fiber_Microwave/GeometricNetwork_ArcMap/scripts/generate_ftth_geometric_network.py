# -*- coding: utf-8 -*-
"""
Regenerate MetroTel FTTH geometric-network training data (>20,000 Home ONTs).
Produces shapefiles (EPSG:32642), GeoPackage, and CSV catalogs.

Usage:
  python3 generate_ftth_geometric_network.py
"""
from __future__ import print_function
import json
import math
import random
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point

random.seed(44)
ROOT = Path(__file__).resolve().parents[1]
SHP = ROOT / "shapefiles"
TAB = ROOT / "tables"
for p in (SHP, TAB, ROOT / "docs", ROOT / "scripts"):
    p.mkdir(parents=True, exist_ok=True)


def main():
    for f in SHP.glob("*"):
        f.unlink()

    junctions = []
    edges = []
    jxy = {}

    def add_j(jid, jtype, name, lon, lat, level, parent="", status="Active", capacity=0, notes=""):
        junctions.append(
            {
                "JunctionID": jid,
                "JuncType": jtype,
                "Name": name,
                "Lon": round(lon, 8),
                "Lat": round(lat, 8),
                "Level": int(level),
                "ParentID": parent,
                "Status": status,
                "Capacity": int(capacity),
                "Notes": notes,
                "Enabled": 1,
                "AncillaryR": 0,  # shapefile-safe (<=10 chars): 1=Source, 2=Sink
            }
        )
        jxy[jid] = (lon, lat)

    def add_e(eid, etype, from_id, to_id, cable="", fibers=0, length_m=0, status="Active", notes=""):
        x1, y1 = jxy[from_id]
        x2, y2 = jxy[to_id]
        if length_m <= 0:
            length_m = math.hypot(
                (x2 - x1) * 111320 * math.cos(math.radians((y1 + y2) / 2.0)),
                (y2 - y1) * 110540,
            )
        edges.append(
            {
                "EdgeID": eid,
                "EdgeType": etype,
                "FromID": from_id,
                "ToID": to_id,
                "CableID": cable or eid,
                "FiberCount": int(fibers),
                "Length_m": round(length_m, 2),
                "Status": status,
                "Notes": notes,
                "Enabled": 1,
                "FlowDirect": 1,
            }
        )

    # Level 0 — multi-source internet
    add_j("SRC-IXP-01", "Internet_Source", "IXP_Primary_A", 69.155, 34.545, 0, "", "Active", 100000, "Primary IXP")
    add_j("SRC-IXP-02", "Internet_Source", "IXP_Secondary_B", 69.182, 34.552, 0, "", "Active", 80000, "Secondary IXP")
    add_j("SRC-SAT-01", "Internet_Source", "Satellite_Backup_Gateway", 69.140, 34.560, 0, "", "Standby", 20000, "Backup")

    # Level 1 — core
    add_j("CORE-01", "Core_POP", "National_Core_East", 69.168, 34.538, 1, "SRC-IXP-01", "Active", 200000, "Core East")
    add_j("CORE-02", "Core_POP", "National_Core_West", 69.148, 34.530, 1, "SRC-IXP-02", "Active", 180000, "Core West")
    add_e("E-SRC-01", "Backbone_Fiber", "SRC-IXP-01", "CORE-01", "BB-SRC-A", 288)
    add_e("E-SRC-02", "Backbone_Fiber", "SRC-IXP-02", "CORE-02", "BB-SRC-B", 288)
    add_e("E-SRC-03", "Backbone_Fiber", "SRC-SAT-01", "CORE-01", "BB-SAT", 48, 0, "Standby", "Satellite backup")
    add_e("E-CORE-RING", "Core_Ring", "CORE-01", "CORE-02", "CORE-RING-1", 288)

    hubs = [
        ("HUB-01", "Hub_Central", 69.165, 34.525, "CORE-01"),
        ("HUB-02", "Hub_North", 69.172, 34.555, "CORE-01"),
        ("HUB-03", "Hub_East", 69.205, 34.530, "CORE-01"),
        ("HUB-04", "Hub_South", 69.160, 34.495, "CORE-02"),
        ("HUB-05", "Hub_West", 69.125, 34.520, "CORE-02"),
        ("HUB-06", "Hub_NW", 69.135, 34.545, "CORE-02"),
    ]
    for hid, name, lon, lat, parent in hubs:
        add_j(hid, "Regional_Hub", name, lon, lat, 2, parent, "Active", 50000, name)
        add_e("E-{}-{}".format(parent, hid), "Backbone_Fiber", parent, hid, "BB-{}".format(hid), 144)

    for a, b in [("HUB-01", "HUB-02"), ("HUB-02", "HUB-03"), ("HUB-01", "HUB-04"), ("HUB-05", "HUB-06"), ("HUB-04", "HUB-05")]:
        add_e("E-RING-{}{}".format(a[-2:], b[-2:]), "Hub_Ring", a, b, "RING-{}-{}".format(a, b), 96)

    olts = []
    for hi, (hid, hname, hlon, hlat, _) in enumerate(hubs):
        for k in range(3):
            oid = "OLT-{:02d}".format(hi * 3 + k + 1)
            lon = hlon + (k - 1) * 0.012 + random.uniform(-0.002, 0.002)
            lat = hlat + random.uniform(-0.008, 0.008)
            add_j(oid, "OLT", "OLT_{}_{}".format(hname, k + 1), lon, lat, 3, hid, "Active", 8192, hid)
            add_e("E-{}-{}".format(hid, oid), "Feeder_Fiber", hid, oid, "FD-{}".format(oid), 72)
            olts.append((oid, lon, lat, hid))

    fdhs = []
    f_idx = 1
    for oid, olon, olat, hid in olts:
        for k in range(5):
            fid = "FDH-{:03d}".format(f_idx)
            f_idx += 1
            ang = (k / 5.0) * 2 * math.pi
            r = 0.008 + 0.002 * (k % 2)
            lon = olon + r * math.cos(ang)
            lat = olat + r * math.sin(ang) * 0.85
            add_j(fid, "FDH", "FDH_{}_{}".format(oid, k + 1), lon, lat, 4, oid, "Active", 512, oid)
            jid = "JC-{}".format(fid)
            jlon = (olon + lon) / 2 + random.uniform(-0.0008, 0.0008)
            jlat = (olat + lat) / 2 + random.uniform(-0.0008, 0.0008)
            add_j(jid, "Joint_Closure", "Joint_{}".format(fid), jlon, jlat, 4, oid, "Active", 72, "Feeder joint")
            add_e("E-{}-{}".format(oid, jid), "Feeder_Fiber", oid, jid, "FD-{}-{}".format(oid, fid), 48)
            add_e("E-{}-{}".format(jid, fid), "Feeder_Fiber", jid, fid, "FD-{}".format(fid), 48)
            fdhs.append((fid, lon, lat, oid))

    splitters = []
    s_idx = 1
    for fid, flon, flat, oid in fdhs:
        for k in range(14):
            sid = "SP-{:04d}".format(s_idx)
            s_idx += 1
            ang = (k / 14.0) * 2 * math.pi
            r = 0.0022 + 0.0004 * (k % 3)
            lon = flon + r * math.cos(ang)
            lat = flat + r * math.sin(ang) * 0.9
            add_j(sid, "Optical_Splitter", "Splitter_{}_{}".format(fid, k + 1), lon, lat, 5, fid, "Active", 16, "1:16")
            add_e("E-{}-{}".format(fid, sid), "Distribution_Fiber", fid, sid, "DIST-{}".format(sid), 12)
            splitters.append((sid, lon, lat, fid))

    h_idx = 1
    for sid, slon, slat, fid in splitters:
        for k in range(17):  # 1260 * 17 = 21420 homes
            hid_home = "ONT-{:05d}".format(h_idx)
            h_idx += 1
            ang = (k / 17.0) * 2 * math.pi + random.uniform(-0.05, 0.05)
            r = 0.00055 + 0.00025 * random.random()
            lon = slon + r * math.cos(ang)
            lat = slat + r * math.sin(ang) * 0.9
            st = "Active" if random.random() > 0.03 else "Planned"
            add_j(hid_home, "Home_ONT", "Home_{}".format(hid_home), lon, lat, 6, sid, st, 1, "Customer ONT")
            add_e("E-{}-{}".format(sid, hid_home), "Drop_Fiber", sid, hid_home, "DROP-{}".format(hid_home), 1, 0, st, "Drop")

    for j in junctions:
        if j["JuncType"] == "Internet_Source":
            j["AncillaryR"] = 1
        elif j["JuncType"] == "Home_ONT":
            j["AncillaryR"] = 2

    home_n = sum(1 for j in junctions if j["JuncType"] == "Home_ONT")
    assert home_n >= 20000, home_n

    gdf_j = gpd.GeoDataFrame(
        junctions, geometry=[Point(j["Lon"], j["Lat"]) for j in junctions], crs="EPSG:4326"
    ).to_crs("EPSG:32642")
    gdf_j["X_m"] = gdf_j.geometry.x.round(3)
    gdf_j["Y_m"] = gdf_j.geometry.y.round(3)

    id_to_xy = {row.JunctionID: (row.geometry.x, row.geometry.y) for row in gdf_j.itertuples()}
    edge_geoms = []
    for e in edges:
        x1, y1 = id_to_xy[e["FromID"]]
        x2, y2 = id_to_xy[e["ToID"]]
        edge_geoms.append(LineString([(x1, y1), (x2, y2)]))
        e["Length_m"] = round(math.hypot(x2 - x1, y2 - y1), 2)
    gdf_e = gpd.GeoDataFrame(edges, geometry=edge_geoms, crs="EPSG:32642")

    # keep shapefile fields <= 10 chars
    gdf_j.to_file(SHP / "GN_Junctions.shp")
    gdf_e.to_file(SHP / "GN_Edges.shp")
    for jt in sorted(gdf_j["JuncType"].unique()):
        gdf_j[gdf_j.JuncType == jt].to_file(SHP / "Junc_{}.shp".format(jt))
    for et in sorted(gdf_e["EdgeType"].unique()):
        gdf_e[gdf_e.EdgeType == et].to_file(SHP / "Edge_{}.shp".format(et))

    gpkg = ROOT / "MetroTel_FTTH_GeometricNetwork_Data.gpkg"
    if gpkg.exists():
        gpkg.unlink()
    gdf_j.to_file(gpkg, layer="GN_Junctions", driver="GPKG")
    gdf_e.to_file(gpkg, layer="GN_Edges", driver="GPKG")

    pd.DataFrame(junctions).to_csv(TAB / "GN_Junctions_Catalog.csv", index=False)
    pd.DataFrame(edges).to_csv(TAB / "GN_Edges_Catalog.csv", index=False)
    pd.DataFrame(junctions)["JuncType"].value_counts().rename_axis("JuncType").reset_index(name="Count").to_csv(
        TAB / "Summary_Junction_Counts.csv", index=False
    )
    pd.DataFrame(edges)["EdgeType"].value_counts().rename_axis("EdgeType").reset_index(name="Count").to_csv(
        TAB / "Summary_Edge_Counts.csv", index=False
    )
    pd.DataFrame(
        [
            ("Internet_Source", "Backbone_Fiber", "Core_POP", "1:M", "Source feeds core"),
            ("Core_POP", "Core_Ring", "Core_POP", "1:1", "Core ring"),
            ("Core_POP", "Backbone_Fiber", "Regional_Hub", "1:M", "Core to hubs"),
            ("Regional_Hub", "Hub_Ring", "Regional_Hub", "M:M", "Hub ring"),
            ("Regional_Hub", "Feeder_Fiber", "OLT", "1:M", "Hub to OLT"),
            ("OLT", "Feeder_Fiber", "Joint_Closure", "1:M", "OLT feeder"),
            ("Joint_Closure", "Feeder_Fiber", "FDH", "1:1", "Joint to FDH"),
            ("FDH", "Distribution_Fiber", "Optical_Splitter", "1:M", "FDH distribution"),
            ("Optical_Splitter", "Drop_Fiber", "Home_ONT", "1:M", "Last mile drops"),
        ],
        columns=["FromType", "EdgeType", "ToType", "Cardinality", "Description"],
    ).to_csv(TAB / "Connectivity_Rules.csv", index=False)
    pd.DataFrame(
        [
            {"Level": 0, "Device": "Internet_Source", "Role": "Multi-source upstream", "ExampleIDs": "SRC-*"},
            {"Level": 1, "Device": "Core_POP", "Role": "National core", "ExampleIDs": "CORE-*"},
            {"Level": 2, "Device": "Regional_Hub", "Role": "Regional aggregation", "ExampleIDs": "HUB-*"},
            {"Level": 3, "Device": "OLT", "Role": "PON headend", "ExampleIDs": "OLT-*"},
            {"Level": 4, "Device": "Joint_Closure / FDH", "Role": "Feeder & distribution hub", "ExampleIDs": "JC-*, FDH-*"},
            {"Level": 5, "Device": "Optical_Splitter", "Role": "1:16 split", "ExampleIDs": "SP-*"},
            {"Level": 6, "Device": "Home_ONT", "Role": "End-user ONT", "ExampleIDs": "ONT-* (>20,000)"},
        ]
    ).to_csv(TAB / "Network_Hierarchy.csv", index=False)

    meta = {
        "project": "MetroTel Capital Region - FTTH Geometric Network",
        "software_target": "ArcGIS Desktop (ArcMap) Geometric Network",
        "crs_shapefiles": "EPSG:32642",
        "junction_count": len(junctions),
        "edge_count": len(edges),
        "home_ont_count": home_n,
        "internet_sources": 3,
        "topology": "Source -> Core -> Hub -> OLT -> Joint -> FDH -> Splitter -> Home_ONT",
    }
    (TAB / "Dataset_Metadata.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
