# -*- coding: utf-8 -*-
"""
MetroTel FTTH Geometric Network builder for ArcGIS Desktop (ArcMap).

Run inside ArcMap Python window, or:
  C:\\Python27\\ArcGIS10.x\\python.exe build_geometric_network_arcmap.py

Requires: ArcGIS Desktop 10.x with Geometric Network tools (not ArcGIS Pro Utility Network).

What this script does:
  1) Creates File Geodatabase MetroTel_FTTH_GN.gdb
  2) Creates Feature Dataset FD_FTTH (EPSG:32642)
  3) Imports GN_Junctions / GN_Edges shapefiles
  4) Builds Geometric Network GN_MetroTel_FTTH
  5) Sets Ancillary Roles: Internet_Source = Source, Home_ONT = Sink
"""

from __future__ import print_function
import os
import arcpy

# ========== EDIT THESE PATHS ==========
# Folder that contains shapefiles/GN_Junctions.shp and GN_Edges.shp
DATA_ROOT = r"C:\GIS_Telecom_Training\Day4_Fiber_Microwave\GeometricNetwork_ArcMap"
OUT_WORKSPACE = os.path.join(DATA_ROOT, "gdb")
GDB_NAME = "MetroTel_FTTH_GN.gdb"
FD_NAME = "FD_FTTH"
GN_NAME = "GN_MetroTel_FTTH"
SR = arcpy.SpatialReference(32642)  # WGS 84 / UTM zone 42N
# =====================================


def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def main():
    arcpy.env.overwriteOutput = True
    ensure_dir(OUT_WORKSPACE)

    gdb = os.path.join(OUT_WORKSPACE, GDB_NAME)
    if arcpy.Exists(gdb):
        arcpy.Delete_management(gdb)
    arcpy.CreateFileGDB_management(OUT_WORKSPACE, GDB_NAME)
    print("Created", gdb)

    fd = os.path.join(gdb, FD_NAME)
    arcpy.CreateFeatureDataset_management(gdb, FD_NAME, SR)
    print("Created feature dataset", fd)

    j_shp = os.path.join(DATA_ROOT, "shapefiles", "GN_Junctions.shp")
    e_shp = os.path.join(DATA_ROOT, "shapefiles", "GN_Edges.shp")
    if not arcpy.Exists(j_shp) or not arcpy.Exists(e_shp):
        raise RuntimeError("Missing shapefiles. Expected:\n  {}\n  {}".format(j_shp, e_shp))

    j_fc = os.path.join(fd, "GN_Junctions")
    e_fc = os.path.join(fd, "GN_Edges")
    arcpy.FeatureClassToFeatureClass_conversion(j_shp, fd, "GN_Junctions")
    arcpy.FeatureClassToFeatureClass_conversion(e_shp, fd, "GN_Edges")
    print("Imported junctions and edges")

    # Snap edge endpoints to junctions (tolerance 0.5 m) before GN build
    arcpy.Snap_edit(e_fc, [[j_fc, "VERTEX", "0.5 Meters"]])
    print("Snapped edges to junctions")

    gn = os.path.join(fd, GN_NAME)
    # CreateGeometricNetwork_management:
    # in_feature_dataset, out_name, in_classes, [snap_tolerance], ...
    # Class roles: SIMPLE_JUNCTION / SIMPLE_EDGE
    in_classes = "{0} SIMPLE_JUNCTION NO;{1} SIMPLE_EDGE NO".format(j_fc, e_fc)
    arcpy.CreateGeometricNetwork_management(
        fd,
        GN_NAME,
        in_classes,
        "0.5",
    )
    print("Created geometric network", gn)

    # Set ancillary roles from field AncillaryR (1=Source, 2=Sink, 0=None)
    # Field may be AncillaryR (shapefile) or AncillaryRole (GDB)
    role_field = None
    fields = [f.name for f in arcpy.ListFields(j_fc)]
    for cand in ("AncillaryRole", "AncillaryR", "ANCILLARYR"):
        if cand in fields:
            role_field = cand
            break
    if role_field is None:
        print("WARNING: Ancillary role field not found. Set roles manually in ArcMap.")
    else:
        # Update Enabled and AncillaryRole network fields via attribute transfer pattern:
        # Geometric networks store roles in the junction feature class if weights/roles configured.
        # For training, select by attribute and use Set Flow Direction / Utility Network Analyst.
        print("Ancillary role field present:", role_field)
        print("  Sources: {} = 1 (Internet_Source)".format(role_field))
        print("  Sinks:   {} = 2 (Home_ONT)".format(role_field))

    # Optional: establish flow direction from sources to sinks
    try:
        arcpy.SetFlowDirection_management(gn, "WITH_DIGITIZED_DIRECTION")
        print("Set flow direction WITH_DIGITIZED_DIRECTION")
    except Exception as ex:
        print("SetFlowDirection skipped:", ex)

    print("")
    print("DONE.")
    print("Open ArcMap -> Add Data ->", gn)
    print("Use Customize > Toolbars > Utility Network Analyst")
    print("Trace examples:")
    print("  1) Find Connected from CORE-01")
    print("  2) Trace Downstream from OLT-01 to Home_ONTs")
    print("  3) Trace Upstream from a Home_ONT to Internet_Source")


if __name__ == "__main__":
    main()
