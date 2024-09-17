import os
import shutil
from PyQt5.QtWidgets import QFileDialog, QApplication, QDialogButtonBox
from pathlib import Path
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
from data_processor import convert_tx0_to_txt, filter_temperature_data_by_date, calibrate_resistivity
import tempfile
import subprocess
import platform
from data_inversion.ERT_Main import startInversion
from WaterContent.Water_Content_Main import water_computing

# global var
global_tx0_input_folder = None
global_selected_temperature_file = None
global_inversion_params = {}


def setup_ui_logic(ui, MainWindow):
    """
    Bind UI events and logic.
    """
    ui.pushButtonBrowserFiles.clicked.connect(lambda: open_file_browser(ui.textEditProcessedTxtPreview, tx0=True))
    ui.pushButtonBrowserTempFiles.clicked.connect(lambda: open_file_browser(ui.textEditProcessedTempPreview, tx0=False))
    ui.pushButtonStartDataProcessing.clicked.connect(lambda: start_data_processing(ui))
    ui.buttonBoxResetConfirmSave.accepted.connect(lambda: start_inversion_with_parameters(ui))
    ui.buttonBoxResetConfirmSave_2.accepted.connect(lambda: start_water_computation_with_parameters(ui))
    ui.actionExit.triggered.connect(lambda: exit_application(MainWindow))
    ui.pushButtonOpenTx0Dir.clicked.connect(lambda: open_directory(global_tx0_input_folder))
    ui.pushButtonTempDir.clicked.connect(lambda: open_directory(global_selected_temperature_file))
    ui.buttonBoxResetConfirmSave.button(QDialogButtonBox.Reset).clicked.connect(lambda: reset_all_fields(ui))
    ui.buttonBoxResetConfirmSave_2.button(QDialogButtonBox.Reset).clicked.connect(lambda: reset_all_fields(ui))
    ui.buttonBoxResetConfirmSave.button(QDialogButtonBox.Reset).clicked.connect(
        lambda: save_output_file(ui, MainWindow))
    ui.buttonBoxResetConfirmSave_2.button(QDialogButtonBox.Reset).clicked.connect(
        lambda: save_output_file(ui, MainWindow))


def open_file_browser(text_edit, tx0=True):
    """
    Open a file selection dialog and copy selected files to the specified directory.
    """
    global global_tx0_input_folder, global_selected_temperature_file

    options = QFileDialog.Options()

    if tx0:
        files, _ = QFileDialog.getOpenFileNames(None, "Select Tx0 Files", "", "Tx0 Files (*.tx0);;All Files (*)",
                                                options=options)
        if files:
            global_tx0_input_folder = tempfile.mkdtemp()  # Temporary directory to store Tx0 files
            for file_path in files:
                if os.path.isfile(file_path) and file_path.endswith('.tx0'):
                    shutil.copy(file_path, global_tx0_input_folder)

            # Display Tx0 file paths in the text edit
            text_edit.clear()
            for file in files:
                text_edit.append(file)
    else:
        file, _ = QFileDialog.getOpenFileName(None, "Select Temperature File", "", "Text Files (*.txt);;All Files (*)",
                                              options=options)
        if file:
            global_selected_temperature_file = file

            # Display temperature file path in the text edit
            text_edit.clear()
            text_edit.append(file)


def start_data_processing(ui):
    """
    Logic to execute when the "Start" button is clicked.
    """
    global global_tx0_input_folder
    global global_selected_temperature_file

    # Get the converter option
    converter_choice = "1" if ui.XZcheckBox.isChecked() else "2"

    if not global_tx0_input_folder:
        print("Please use the 'Browser' button to select tx0 files first.")
        return

    if not global_selected_temperature_file:
        print("Please use the 'Browser' button to select the temperature file first.")
        return

    # Select Output Directory
    output_directory = QFileDialog.getExistingDirectory(None, "Select Output Directory", "")
    if not output_directory:  # use default if cancelled
        output_directory = os.path.join(os.getcwd(), 'outputs')

    corrected_output_folder_detailed = Path(output_directory, 'corrected_resistivity_detailed')
    corrected_output_folder_simplified = Path(output_directory, 'corrected_resistivity_simplified')
    corrected_output_folder_detailed.mkdir(parents=True, exist_ok=True)
    corrected_output_folder_simplified.mkdir(parents=True, exist_ok=True)

    # Set output directories for temporary files
    txt_output_folder = Path(tempfile.mkdtemp())
    filtered_temp_output = Path(tempfile.mkdtemp(), 'Newtem.txt')

    # Step 1: Convert tx0 to txt
    convert_tx0_to_txt(global_tx0_input_folder, txt_output_folder, converter_choice)
    print("Conversion from tx0 to txt completed.")

    # Step 2: Filter temperature data by date
    filter_temperature_data_by_date(txt_output_folder, global_selected_temperature_file, filtered_temp_output)
    print("Temperature data filtering completed.")

    # Step 3: Calibrate resistivity
    calibrate_resistivity(txt_output_folder, corrected_output_folder_detailed, corrected_output_folder_simplified,
                          filtered_temp_output)
    print("Resistivity calibration completed.")

    print("Data processing completed.")


def exit_application(MainWindow):
    """
    Exit the application.
    """
    QApplication.quit()


def reset_all_fields(ui):
    """
    Reset all input fields in the UI to their default values.
    """
    # Reset geometry and inversion parameters
    ui.startXLineEdit.setText("0")
    ui.startZLineEdit.setText("0")
    ui.endXLineEdit.setText("47")
    ui.endZLineEdit.setText("-8")
    ui.qualityLineEdit.setText("33.5")
    ui.horizontalSlider.setValue(33)
    ui.areaLineEdit.setText("0.5")
    ui.LambdaLineEdit.setText("0.1")
    ui.IterationLineEdit.setText("10")
    ui.dPhiLineEdit.setText("0.01")
    ui.checkBox.setChecked(False)

    # Clear text edits for file paths
    ui.textEditProcessedTxtPreview.clear()
    ui.textEditProcessedTempPreview.clear()


def open_directory(directory):
    """
    Open the specified directory in the system's file explorer.
    """
    if directory:
        if platform.system() == "Windows":
            os.startfile(directory)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", directory])
        else:
            subprocess.Popen(["xdg-open", directory])
    else:
        print("Directory path is empty. Please select a valid directory.")


def select_processed_file():
    """
    Open File Dialog for processed file selection
    """
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(None, "Select Processed File", "", "Text Files (*.txt);;All Files (*)",
                                               options=options)
    if file_path:
        print(f"Selected processed file: {file_path}")
        return file_path
    else:
        print("No file selected.")
        return None


def start_inversion_with_parameters(ui):
    """
    Capture inversion parameters from the UI and initiate inversion processing.
    """
    # Capture inversion parameters from the UI
    try:
        start_x = float(ui.startXLineEdit.text()) if ui.startXLineEdit.text() else 0
        start_z = float(ui.startZLineEdit.text()) if ui.startZLineEdit.text() else 0
        end_x = float(ui.endXLineEdit.text()) if ui.endXLineEdit.text() else 47
        end_z = float(ui.endZLineEdit.text()) if ui.endZLineEdit.text() else -8
        quality = float(ui.qualityLineEdit.text()) if ui.qualityLineEdit.text() else 33.5
        area = float(ui.areaLineEdit.text()) if ui.areaLineEdit.text() else 0.5
        lambda_value = float(ui.LambdaLineEdit.text()) if ui.LambdaLineEdit.text() else 7
        max_iterations = int(ui.IterationLineEdit.text()) if ui.IterationLineEdit.text() else 6
        dphi = float(ui.dPhiLineEdit.text()) if ui.dPhiLineEdit.text() else 2
        robust_data = ui.checkBox.isChecked()
    except ValueError as e:
        print(f"Error in conversion: {e}")
        return

    inversion_params = {
        "lambda": lambda_value,
        "max_iterations": max_iterations,
        "dphi": dphi,
        "robust_data": robust_data
    }

    processed_file_path = select_processed_file()

    if processed_file_path:
        # Run inversion and display output
        output_image_path = startInversion(
            [start_x, start_z],
            [end_x, end_z],
            quality,
            area,
            inversion_params,
            processed_file_path
        )

        if output_image_path and os.path.exists(output_image_path):
            pixmap = QPixmap(output_image_path)
            ui.labelDepthImage.setPixmap(pixmap)
            ui.labelDepthImage.setScaledContents(True)
            ui.labelDepthImage.setAlignment(QtCore.Qt.AlignCenter)
            print(f"Depth image displayed: {output_image_path}")
            # 切换到显示结果的页面
            ui.stackedWidget.setCurrentWidget(ui.page_2)
        else:
            print("Output image file not found.")
    else:
        print("No processed file selected. Please select a file first.")


def start_water_computation_with_parameters(ui):
    """
    Capture water computation parameters from the UI and initiate the process.
    """
    processed_file_path = select_processed_file()

    if not processed_file_path:
        print("No processed file selected. Please select a file first.")
        return

    try:
        start_x = float(ui.startXLineEdit_WC.text()) if ui.startXLineEdit_WC.text() else 0
        start_z = float(ui.startZLineEdit_WC.text()) if ui.startZLineEdit_WC.text() else 0
        end_x = float(ui.endXLineEdit_WC.text()) if ui.endXLineEdit_WC.text() else 47
        end_z = float(ui.endZLineEdit_WC.text()) if ui.endZLineEdit_WC.text() else -8
        quality = float(ui.qualityLineEdit_WC.text()) if ui.qualityLineEdit_WC.text() else 33.5
        area = float(ui.areaLineEdit_WC.text()) if ui.areaLineEdit_WC.text() else 0.5
        lambda_value = float(ui.LambdaLineEdit_WC.text()) if ui.LambdaLineEdit_WC.text() else 10
        max_iterations = int(ui.IterationLineEdit_WC.text()) if ui.IterationLineEdit_WC.text() else 6
        dphi = float(ui.dPhiLineEdit_WC.text()) if ui.dPhiLineEdit_WC.text() else 2

        A = float(ui.ALineEdit.text()) if ui.ALineEdit.text() else 246.47
        B = float(ui.BLineEdit.text()) if ui.BLineEdit.text() else -0.627

    except ValueError as e:
        print(f"Error in conversion: {e}")
        return

    try:
        image_path = water_computing(
            [start_x, start_z], [end_x, end_z], quality, area, lambda_value,
            max_iterations, dphi, A, B, processed_file_path
        )

        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            ui.labelSWC.setPixmap(pixmap)
            ui.labelSWC.setScaledContents(True)
            ui.labelSWC.setAlignment(QtCore.Qt.AlignCenter)
            print(f"Image displayed on labelSWC: {image_path}")
            # 切换到显示结果的页面
            ui.stackedWidget_2.setCurrentWidget(ui.page_3)
        else:
            print("Image path is invalid or file does not exist.")
    except Exception as e:
        print(f"Error during water_computing: {e}")


def save_output_file(ui, MainWindow):
    options = QFileDialog.Options()
    file_name, _ = QFileDialog.getSaveFileName(MainWindow, "Save Output File", "", "Text Files (*.txt);;All Files (*)",
                                               options=options)
    if file_name:
        output_content = get_output_content(ui)
        with open(file_name, 'w') as file:
            file.write(output_content)
        print(f"Output saved to {file_name}")


def get_output_content(ui):
    output_file_path = ui.textEditProcessedTxtPreview.toPlainText()
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r') as file:
            content = file.read()
        return content
    return "No output file selected or file not found."
