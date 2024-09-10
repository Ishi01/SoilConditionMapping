import os
import unittest
import shutil
from your_module_name import ensure_output_folder, cleanup_temp_files, startInversion

class TestSoilConditionMapping(unittest.TestCase):

    def setUp(self):
        # Set up any necessary environment before each test
        self.output_dir = ensure_output_folder()
        self.raw_file = "test_data.dat"  # replace with the actual test file name
        self.raw_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Raw")
        
        # Ensure Raw directory and test file exist
        if not os.path.exists(self.raw_dir):
            os.makedirs(self.raw_dir)
        
        with open(os.path.join(self.raw_dir, self.raw_file), 'w') as f:
            f.write("Some test content")  # Put valid content for testing

    def test_ensure_output_folder(self):
        # Test if the output directory is created correctly
        self.assertTrue(os.path.exists(self.output_dir))

    def test_cleanup_temp_files(self):
        # Create temporary files to be cleaned up
        patterns = [
            "*.vector", "*.matrix", "*.bmat", 
            "fop-model1.vtk", "invalid.data", "mesh.bms"
        ]
        
        for pattern in patterns:
            with open(pattern, 'w') as f:
                f.write("temp data")
        
        # Run the cleanup function
        cleanup_temp_files()
        
        # Verify the files were removed
        for pattern in patterns:
            self.assertFalse(os.path.exists(pattern))

    def test_start_inversion(self):
        # This test runs the full inversion process using the actual test file.
        try:
            startInversion()
            output_files = os.listdir(self.output_dir)
            
            # Check if the expected output file is generated
            self.assertTrue(any(f.endswith('.png') for f in output_files))
        except Exception as e:
            self.fail(f"startInversion failed with exception: {e}")

    def tearDown(self):
        # Clean up after each test
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        
        if os.path.exists(self.raw_dir):
            shutil.rmtree(self.raw_dir)

if __name__ == '__main__':
    unittest.main()
