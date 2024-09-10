import os
import pytest
from ERT_Main import  startInversion, cleanup_temp_files



def test_start_inversion():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, "Output")
    # This test runs the full inversion process using the actual test file.
    try:
        startInversion()
        cleanup_temp_files()
        output_files = os.listdir(output_dir)
        
        # Check if the expected output file is generated
        assert any(f.endswith('.png') for f in output_files)
    except Exception as e:
        pytest.fail(f"startInversion failed with exception: {e}")
