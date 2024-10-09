import os
import pytest
import unittest.mock as mock
from unittest.mock import patch, Mock, call, MagicMock, mock_open
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLineEdit, QLabel
from PyQt5.QtGui import QPixmap
from UI import Ui_MainWindow
from ui_logic import (
    setup_ui_logic, start_data_processing, reset_all_fields, open_file_browser, 
    start_inversion_with_parameters, run_inversion_and_display_output,  
    save_output_file, start_water_computation_with_parameters
)
from DataInversion.ERT_Main import startInversion
from WaterContent.Water_Content_Main import water_computing
import data_processor
import numpy as np
import pygimli as pg

# Global variables reset
data_processor.global_tx0_input_folder = None
data_processor.global_selected_temperature_file = None

# 1. Create a single instance of QApplication as a fixture
@pytest.fixture(scope='module')
def app():
    app = QApplication([])  # Create once
    yield app
    app.exit()

# 2. Create a Ui_MainWindow instance as a fixture
@pytest.fixture
def ui(app):
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    setup_ui_logic(ui, MainWindow)
    yield ui  # Avoid rendering by not calling show()
    MainWindow.close()

# Test 1: Simulate file browser for selecting tx0 files
def test_open_file_browser_select_tx0_files(ui):
    # Simulate QFileDialog.getOpenFileNames return value
    with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames', return_value=(['test.tx0'], '')):
        open_file_browser(ui.textEditProcessedTxtPreview, tx0=True)
        assert 'test.tx0' in ui.textEditProcessedTxtPreview.toPlainText()

# Test 2: Simulate file browser with no file selected
def test_open_file_browser_no_selection(ui):
    # Simulate no file selected
    with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames', return_value=([], '')):
        open_file_browser(ui.textEditProcessedTxtPreview, tx0=True)
        assert ui.textEditProcessedTxtPreview.toPlainText() == ""

    with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName', return_value=('', '')):
        open_file_browser(ui.textEditProcessedTempPreview, tx0=False)
        assert ui.textEditProcessedTempPreview.toPlainText() == ""

# Test 3: Start data processing with no files selected and check error messages
def test_start_data_processing_without_files(ui):
    # Test when no files are selected
    tx0_input_folder = None
    selected_temperature_file = None

    with patch('builtins.print') as mock_print, \
         patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory', return_value=''), \
         patch('data_processor.convert_tx0_to_txt'), \
         patch('data_processor.filter_temperature_data_by_date'), \
         patch('data_processor.calibrate_resistivity'):

        # Call start_data_processing with no selected files
        start_data_processing(ui, tx0_input_folder, selected_temperature_file)

        # Check expected print output
        expected_calls = [
            call("Please use the 'Browser' button to select tx0 files first.")
        ]
        assert mock_print.mock_calls == expected_calls

    # Test when tx0 file is selected but temperature file is not
    tx0_input_folder = "dummy_path"
    selected_temperature_file = None

    with patch('builtins.print') as mock_print, \
         patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory', return_value=''), \
         patch('data_processor.convert_tx0_to_txt'), \
         patch('data_processor.filter_temperature_data_by_date'), \
         patch('data_processor.calibrate_resistivity'):

        # Call start_data_processing again
        start_data_processing(ui, tx0_input_folder, selected_temperature_file)

        # Check expected print output
        expected_calls = [
            call("Please use the 'Browser' button to select the temperature file first.")
        ]
        assert mock_print.mock_calls == expected_calls

# Test 4: Start data processing with valid files and ensure conversion is called
def test_start_data_processing_with_files(ui):
    # Set valid folder and file paths
    tx0_input_folder = "dummy_folder_path"
    selected_temperature_file = "dummy_temp_file.txt"

    # Mock the UI file selections
    ui.textEditProcessedTxtPreview.setText("test.tx0")
    ui.textEditProcessedTempPreview.setText("temperature.txt")

    # Simulate output directory selection
    with patch('ui_logic.convert_tx0_to_txt') as mock_convert, \
         patch('ui_logic.filter_temperature_data_by_date'), \
         patch('ui_logic.calibrate_resistivity'), \
         patch('os.listdir', return_value=['file1.tx0', 'file2.tx0']), \
         patch('builtins.open', mock_open(read_data='dummy data')), \
         patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory', return_value="output_dir"):

        # Call start_data_processing
        start_data_processing(ui, tx0_input_folder, selected_temperature_file)

        # Ensure the conversion was called
        mock_convert.assert_called_once()

# Test 5: Test inversion with mock file and check if the output image is generated
def test_inversion_with_mock_file():
    mock_ui = MagicMock()

    # Simulate UI input values
    mock_ui.startXLineEdit.text.return_value = "0"
    mock_ui.startZLineEdit.text.return_value = "0"
    mock_ui.endXLineEdit.text.return_value = "47"
    mock_ui.endZLineEdit.text.return_value = "-8"
    mock_ui.qualityLineEdit.text.return_value = "33.5"
    mock_ui.areaLineEdit.text.return_value = "0.5"
    mock_ui.LambdaLineEdit.text.return_value = "7"
    mock_ui.IterationLineEdit.text.return_value = "6"
    mock_ui.dPhiLineEdit.text.return_value = "2"
    mock_ui.checkBox.isChecked.return_value = False

    # Simulate file and output generation
    test_file_path = "uilogic_test/test_data.txt"
    
    with patch('ui_logic.select_processed_file', return_value=test_file_path), \
         patch('DataInversion.ERT_Main.startInversion', return_value='uilogic_test/output_folder/inversion_result_test_data.png'), \
         patch('DataInversion.ERT_Main.ensure_output_folder', return_value="uilogic_test/output_folder"), \
         patch('DataInversion.ERT_Main.cleanup_temp_files'):

        # Call the function being tested
        start_inversion_with_parameters(mock_ui)

        # Check if the image file exists
        assert os.path.exists('uilogic_test/output_folder/inversion_result_test_data.png')

        # Check if the image is displayed in the UI
        mock_ui.labelDepthImage.setPixmap.assert_called_once()

# Test 6: Test resetting all fields in the UI
def test_reset_all_fields(ui):
    """Test resetting all UI fields."""
    # Set some test values in the UI fields
    ui.startXLineEdit.setText("10")
    ui.startZLineEdit.setText("20")
    ui.endXLineEdit.setText("30")
    ui.endZLineEdit.setText("40")
    ui.qualityLineEdit.setText("50")
    ui.areaLineEdit.setText("60")
    ui.LambdaLineEdit.setText("70")
    ui.IterationLineEdit.setText("80")
    ui.dPhiLineEdit.setText("90")
    ui.checkBox.setChecked(True)

    # Call reset function
    reset_all_fields(ui)

    # Assert that all fields have been reset to 0 or cleared
    assert ui.startXLineEdit.text() == "0"
    assert ui.startZLineEdit.text() == "0"
    assert ui.endXLineEdit.text() == "0"
    assert ui.endZLineEdit.text() == "0"
    assert ui.qualityLineEdit.text() == "0"
    assert ui.areaLineEdit.text() == "0"
    assert ui.LambdaLineEdit.text() == "0"
    assert ui.IterationLineEdit.text() == "0"
    assert ui.dPhiLineEdit.text() == "0"
    assert not ui.checkBox.isChecked()

    # Check if text boxes are cleared
    assert ui.textEditProcessedTxtPreview.toPlainText() == ""
    assert ui.textEditProcessedTempPreview.toPlainText() == ""

# Test 7: Test saving the output file
def test_save_output_file(ui):
    # Simulate QFileDialog.getSaveFileName return value
    with patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName', return_value=('output.txt', '')), \
         patch('builtins.open', mock.mock_open()) as mock_file:
        
        save_output_file(ui, None)
        
        # Check if the file was opened for writing
        mock_file.assert_called_once_with('output.txt', 'w')

# Test 8: Test application exit functionality
def test_exit_application(app, ui):
    """Test the application exit functionality."""
    with patch.object(QApplication, 'quit') as mock_quit:
        ui.actionExit.trigger()
        mock_quit.assert_called_once()

# Test 9: Test water computation functionality
def test_start_water_computation_with_parameters(ui):
    # Get the path of the test data file
    test_file_path = os.path.join(os.path.dirname(__file__), 'uilogic_test', 'test_data.txt')

    # Simulate QFileDialog.getOpenFileName to select the test file
    with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName', return_value=(test_file_path, '')), \
         patch('os.path.exists', return_value=True), \
         patch.object(ui.labelSWC, 'setPixmap') as mock_setPixmap:

        # Call the function being tested with real test data
        start_water_computation_with_parameters(ui)

        # Verify setPixmap was called once with a valid image path
        mock_setPixmap.assert_called_once()
        pixmap_argument = mock_setPixmap.call_args[0][0]
        assert pixmap_argument is not None, "Pixmap argument is None"

# Run the tests
if __name__ == '__main__':
    pytest.main()
