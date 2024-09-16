import os
import pytest
from ERT_Main import startInversion, cleanup_temp_files, create_mesh


def test_start_inversion():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, "Output")

    try:
        startInversion()
        cleanup_temp_files()
        output_files = os.listdir(output_dir)

        assert any(f.endswith('.png') for f in output_files)
    except Exception as e:
        pytest.fail(f"startInversion failed with exception: {e}")


def test_create_mesh():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        create_mesh()
        assert "mesh.bms" in os.listdir(current_dir)
    except Exception as e:
        pytest.fail(f"create_mesh failed with exception: {e}")
