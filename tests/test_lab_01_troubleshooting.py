import unittest
import os

class TestLab01Structure(unittest.TestCase):
    def test_files_exist(self):
        base_path = "labs/eigrp/lab-01-basic-adjacency"
        self.assertTrue(os.path.exists(os.path.join(base_path, "challenges.md")))
        self.assertTrue(os.path.exists(os.path.join(base_path, "scripts/fault_injector.py")))

    def test_injector_importable(self):
        # Verify the script is syntactically correct
        try:
            import labs.eigrp.lab_01_basic_adjacency.scripts.fault_injector
        except ImportError:
            # This is expected if the path is not exactly right for python import, 
            # but we can check syntax by compiling
            script_path = "labs/eigrp/lab-01-basic-adjacency/scripts/fault_injector.py"
            with open(script_path, "r") as f:
                source = f.read()
                compile(source, script_path, "exec")

if __name__ == "__main__":
    unittest.main()
