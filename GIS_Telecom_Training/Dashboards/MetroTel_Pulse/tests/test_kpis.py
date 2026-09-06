#!/usr/bin/env python3
"""Guard the sample KPI totals that the dashboard header must show."""

from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pulse_kpis import summarize_zones  # noqa: E402


class PulseKpiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / "data" / "ExecZone_KPI_Dashboard.csv"
        with path.open(encoding="utf-8") as handle:
            cls.rows = list(csv.DictReader(handle))

    def test_twelve_zones(self):
        self.assertEqual(len(self.rows), 12)

    def test_network_totals(self):
        summary = summarize_zones(self.rows)
        self.assertEqual(summary["subscribers"], 526)
        self.assertEqual(summary["p1_expand"], 3)
        self.assertEqual(summary["population"], 1232000)
        self.assertAlmostEqual(summary["arpu_weighted"], 31.97, places=1)
        self.assertAlmostEqual(summary["churn_weighted"], 0.292, places=2)
        self.assertGreater(summary["coverage_pop_weighted"], 80)
        self.assertLess(summary["coverage_pop_weighted"], 95)

    def test_filter_peri_urban(self):
        row = next(r for r in self.rows if r["DIST_ID"] == "DZ-12")
        summary = summarize_zones([row])
        self.assertEqual(summary["subscribers"], 16)
        self.assertEqual(summary["p1_expand"], 0)
        self.assertTrue(str(row["PRIORITY"]).startswith("P3"))


if __name__ == "__main__":
    unittest.main()
