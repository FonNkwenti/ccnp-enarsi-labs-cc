import unittest
import os

class TestLab06Initialization(unittest.TestCase):
    LAB_PATH = "labs/eigrp/lab-06-filtering-control"

    def test_directory_exists(self):
        """Check if the lab directory exists."""
        self.assertTrue(os.path.exists(self.LAB_PATH), f"Directory {self.LAB_PATH} does not exist")

    def test_subdirectories_exist(self):
        """Check if required subdirectories exist."""
        subdirs = ["initial-configs", "solutions"]
        for subdir in subdirs:
            path = os.path.join(self.LAB_PATH, subdir)
            self.assertTrue(os.path.exists(path), f"Subdirectory {path} does not exist")

if __name__ == "__main__":
    unittest.main()
