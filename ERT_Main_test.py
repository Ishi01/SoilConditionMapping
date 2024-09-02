import pytest
import os
import numpy as np
import pygimli as pg
import pygimli.meshtools as mt

# Import the inversion function
from ERT_Main import inversion

@pytest.fixture
def setup_test_environment(tmp_path):
    # Create a temporary directory for the test
    test_dir = tmp_path / "test_inversion"
    test_dir.mkdir()

    # Create a dummy tx0 file
    dummy_file = test_dir / "dummy.tx0"
    dummy_file.write_text("Dummy content")

    # Change to the temporary directory
    os.chdir(test_dir)

    return test_dir

def test_inversion_function(setup_test_environment):
    # Set up test environment
    # test_dir = setup_test_environment

    # Run the inversion function
    # result = inversion(
    #     start=[0, 0],
    #     end=[47, -8],
    #     quality=33.5,
    #     area=0.5,
    #     work_dir=str(test_dir)
    # )
    result = inversion()

    # Assert that the result is not None
    assert result is not None

    # # Check if the mesh file was created
    # mesh_file = test_dir / "mesh.bms"
    # assert mesh_file.exists()

    # Additional checks can be added based on the expected behavior of the function

if __name__ == "__main__":
    pytest.main()
