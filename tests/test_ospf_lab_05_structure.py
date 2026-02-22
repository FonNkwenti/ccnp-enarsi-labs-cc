import unittest
import os

class TestOSPFLab05Structure(unittest.TestCase):
    LAB_PATH = "labs/ospf/lab-05-special-areas"

    def test_directory_exists(self):
        """Check if the lab directory exists."""
        self.assertTrue(os.path.exists(self.LAB_PATH), f"Directory {self.LAB_PATH} does not exist")

    def test_subdirectories_exist(self):
        """Check if required subdirectories exist."""
        subdirs = ["initial-configs", "solutions", "scripts/fault-injection"]
        for subdir in subdirs:
            path = os.path.join(self.LAB_PATH, subdir)
            self.assertTrue(os.path.exists(path), f"Subdirectory {path} does not exist")

    def test_files_exist(self):
        """Check if required files exist."""
        files = [
            "topology.drawio",
            "workbook.md",
            "challenges.md",
            "setup_lab.py",
            "scripts/refresh_lab.py",
            "scripts/fault-injection/inject_scenario_01.py",
            "scripts/fault-injection/apply_solution.py",
            "initial-configs/R1.cfg",
            "initial-configs/R7.cfg",
            "solutions/R1.cfg",
            "solutions/R7.cfg"
        ]
        for file in files:
            path = os.path.join(self.LAB_PATH, file)
            self.assertTrue(os.path.exists(path), f"File {path} does not exist")

    def test_workbook_content(self):
        """Check if workbook has required sections."""
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path, "r") as f:
            content = f.read()
            self.assertIn("## 1. Concepts & Skills Covered", content)
            self.assertIn("## 2. Topology & Scenario", content)
            self.assertIn("## 9. Solutions", content)

    def test_config_content(self):
        """Check if solution configs contain stub area commands."""
        path_r3 = os.path.join(self.LAB_PATH, "solutions/R3.cfg")
        with open(path_r3, "r") as f:
            content = f.read()
            self.assertIn("area 37 stub no-summary", content)
            
        path_r7 = os.path.join(self.LAB_PATH, "solutions/R7.cfg")
        with open(path_r7, "r") as f:
            content = f.read()
            self.assertIn("area 37 stub", content)

if __name__ == "__main__":
    unittest.main()
