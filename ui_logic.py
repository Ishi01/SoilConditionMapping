import os
import sys
import shutil
from PyQt5.QtWidgets import QFileDialog, QApplication, QDialogButtonBox, QStatusBar
from pathlib import Path
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
from data_processor import convert_tx0_to_txt, filter_temperature_data_by_date, calibrate_resistivity
import tempfile
import subprocess
import platform
import base64
from DataInversion.ERT_Main import startInversion
from WaterContent.Water_Content_Main import water_computing
from lib.temp_depth_graph import display_temp_vs_depth

# global var
global_tx0_input_folder = None
global_selected_temperature_file = None
global_inversion_params = {}


def setup_ui_logic(ui, MainWindow):
    """
    Bind UI events and logic.
    """
    redirect_print_to_status_bar(ui)

    ui.pushButtonBrowserFiles.clicked.connect(lambda: open_file_browser(ui.textEditProcessedTxtPreview, tx0=True))
    ui.pushButtonBrowserTempFiles.clicked.connect(lambda: open_file_browser(ui.textEditProcessedTempPreview, tx0=False))
    ui.pushButtonStartDataProcessing.clicked.connect(lambda: start_data_processing(ui))

    # Bind OK button to start the inversion with parameters
    ui.buttonBoxResetConfirmSave.accepted.connect(lambda: start_inversion_with_parameters(ui))

    # Bind exit action to close the application
    ui.actionExit.triggered.connect(lambda: exit_application(MainWindow))

    # Open directories when buttons are clicked
    ui.pushButtonOpenTx0Dir.clicked.connect(lambda: open_directory(global_tx0_input_folder))
    ui.pushButtonTempDir.clicked.connect(lambda: open_directory(global_selected_temperature_file))

    # Bind Reset buttons to reset all fields (corrected: only resets fields, does not trigger saving)
    ui.buttonBoxResetConfirmSave.button(QDialogButtonBox.Reset).clicked.connect(lambda: reset_all_fields(ui))

    # Bind Save buttons to save the output (corrected: Save buttons trigger saving)
    ui.buttonBoxResetConfirmSave.button(QDialogButtonBox.Save).clicked.connect(lambda: save_output_file(ui, MainWindow))

    # Batch Data processing (Note typo here)
    ui.pushButtonBashProcess.clicked.connect(lambda: start_batch_processing(ui))

    ui.toolButton.clicked.connect(lambda: open_directory(global_inversion_params.get('output_image_folder')))
    ui.toolButton.clicked.connect(lambda: switch_to_page(ui, ui.page_1))


def redirect_print_to_status_bar(ui):
    """
    Redirects all print outputs to the status bar of the UI.
    """

    class StreamToStatusBar:
        def __init__(self, status_bar):
            self.status_bar = status_bar

        def write(self, text):
            if text.strip():  # Ignore empty strings
                self.status_bar.showMessage(text, 5000)  # Show the message in the status bar for 5 seconds

        def flush(self):
            pass

    # Set the new stream for stdout
    sys.stdout = StreamToStatusBar(ui.statusbar)


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
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                text_edit.append(content)
    else:
        file, _ = QFileDialog.getOpenFileName(None, "Select Temperature File", "", "Text Files (*.txt);;All Files (*)",
                                              options=options)
        if file:
            global_selected_temperature_file = file

            # Display temperature file path in the text edit
            text_edit.clear()
            text_edit.append(f"File Path: {file}\n")
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            text_edit.append(content)


def start_data_processing(ui):
    """
    Logic to execute when the "Start" button is clicked.

    Parameters:
        ui: Instance of Ui_MainWindow.
        tx0_input_file: Path to the folder containing the tx0 files.
        selected_temperature_file: Path to the temperature file.
    """
    global global_tx0_input_folder
    global global_selected_temperature_file

    print(f"Debug: global_tx0_input_folder = {global_tx0_input_folder}")
    print("Selected output directory")

    tx0_input_file = global_tx0_input_folder
    selected_temperature_file = global_selected_temperature_file

    # Check tx0 file
    if not tx0_input_file:
        print("Please use the 'Browser' button to select tx0 files first.")
        return

    # Check temperature file
    if not selected_temperature_file:
        print("Please use the 'Browser' button to select the temperature file first.")
        return

    # set converter
    converter_choice = "1"

    # select output menu
    output_directory = QFileDialog.getExistingDirectory(None, "Select Output Directory", "")
    if not output_directory:  # no selection on output file, create default output directory
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
    filter_temperature_data_by_date(txt_output_folder, selected_temperature_file, filtered_temp_output)
    print("Temperature data filtering completed.")

    # Step 3: Calibrate resistivity with filtered temperature data
    calibrate_resistivity(txt_output_folder, corrected_output_folder_detailed, corrected_output_folder_simplified,
                          filtered_temp_output)
    print("Resistivity calibration completed.")

    # Display the content of the output file in the UI text edit
    output_files = list(corrected_output_folder_detailed.glob("*.txt"))
    if output_files:
        output_file_path = output_files[0]  # Assuming there is one file in the output folder
        with open(output_file_path, 'r', encoding='utf-8') as f:
            output_content = f.read()

        ui.textEditProcessedTxtPreview.clear()
        ui.textEditProcessedTxtPreview.append(f"Output File: {output_file_path}\n")
        ui.textEditProcessedTxtPreview.append(output_content)

    try:
        # Assume only one file is used
        tx0_file = os.listdir(global_tx0_input_folder)[0]

        # Generate temp vs depth plot with Base64 encoded image
        plot_image_base64 = display_temp_vs_depth(os.path.join(global_tx0_input_folder, tx0_file),
                                                  global_selected_temperature_file)

        if plot_image_base64:
            print("Successfully generate plot of temperature vs depth")
            with open(os.path.join(output_directory, "temp_vs_depth_plot.png"), "wb") as f:
                f.write(base64.b64decode(plot_image_base64))
            print(f"Temp_vs_depth plot saved to {output_directory}/temp_vs_depth_plot.png")
        else:
            print("failed generating temperature vs depth plot")

    except Exception as e:
        print(f"Error generating temperature vs depth plot: {str(e)}")

    print("Data processing completed.")


def start_batch_processing(ui):
    """
    Logic to execute when the "Batch Process" button is clicked, and process all tx0 files in the selected folder.

    This function will process multiple tx0 files, convert them to txt, filter temperature data, and calibrate resistivity.
    No image generation and no converter selection (default converter_choice = 1).

    This version uses subprocess to run the batch processing in the background, allowing the UI to remain responsive.
    """

    # Step 1: Select input folder containing tx0 files
    print("Step 1: Select input folder containing tx0 files")
    tx0_input_folder = QFileDialog.getExistingDirectory(None, "Select Folder Containing tx0 Files", "")
    if not tx0_input_folder:
        print("No tx0 input folder selected. Operation cancelled.")
        return

    # Step 2: Select temperature file
    print("Step 2: Select temperature file")
    selected_temperature_file, _ = QFileDialog.getOpenFileName(None, "Select Temperature File", "",
                                                               "Text Files (*.txt);;All Files (*)")
    if not selected_temperature_file:
        print("No temperature file selected. Operation cancelled.")
        return

    # Step 3: Select output directory for processed data
    print("Step 3: Select output directory for processed data")
    output_directory = QFileDialog.getExistingDirectory(None, "Select Output Directory", "")
    if not output_directory:  # No selection on output directory, create default output directory
        output_directory = os.path.join(os.getcwd(), 'outputs')

    corrected_output_folder_detailed = os.path.join(output_directory, 'corrected_resistivity_detailed')
    corrected_output_folder_simplified = os.path.join(output_directory, 'corrected_resistivity_simplified')

    # Ensure output directories exist
    os.makedirs(corrected_output_folder_detailed, exist_ok=True)
    os.makedirs(corrected_output_folder_simplified, exist_ok=True)

    # Temporary output folders for txt and filtered temperature data
    txt_output_folder = tempfile.mkdtemp()
    filtered_temp_output = os.path.join(tempfile.mkdtemp(), 'Newtem.txt')

    # Step 4: Call the batch process via subprocess
    # Use the subprocess to run the data_processor functions without blocking the UI
    try:
        print(f"Starting batch processing...")

        subprocess.run(
            [
                "python",  # Assuming you are using Python to run the script
                "-c",  # Inline Python code
                f"""
import os
from data_processor import convert_tx0_to_txt, filter_temperature_data_by_date, calibrate_resistivity

# Convert tx0 to txt
convert_tx0_to_txt(r'{tx0_input_folder}', r'{txt_output_folder}', '1')

# Filter temperature data by date
filter_temperature_data_by_date(r'{txt_output_folder}', r'{selected_temperature_file}', r'{filtered_temp_output}')

# Calibrate resistivity with filtered temperature data
calibrate_resistivity(r'{txt_output_folder}', r'{corrected_output_folder_detailed}', r'{corrected_output_folder_simplified}', r'{filtered_temp_output}')

print("Batch processing completed successfully.")
"""
            ],
            check=True
        )

    except subprocess.CalledProcessError as e:
        print(f"Error during batch processing: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    print("Batch processing completed for all files.")


def exit_application(MainWindow):
    """
    Exit the application.
    """
    QApplication.quit()


def reset_all_fields(ui):
    """
    Reset all input fields in the UI to their default values or empty values.
    """
    try:
        # Set all LineEdits to 0 or clear them
        ui.startXLineEdit.setText("0")
        ui.startZLineEdit.setText("0")
        ui.endXLineEdit.setText("0")
        ui.endZLineEdit.setText("0")
        ui.qualityLineEdit.setText("0")
        ui.areaLineEdit.setText("0")
        ui.LambdaLineEdit.setText("0")
        ui.IterationLineEdit.setText("0")
        ui.dPhiLineEdit.setText("0")
        ui.checkBox.setChecked(False)

        # Water Content Page Field Reset
        ui.startXLineEdit_WC.setText("0")
        ui.startZLineEdit_WC.setText("0")
        ui.endXLineEdit_WC.setText("0")
        ui.endZLineEdit_WC.setText("0")
        ui.qualityLineEdit_WC.setText("0")
        ui.areaLineEdit_WC.setText("0")
        ui.LambdaLineEdit_WC.setText("0")
        ui.IterationLineEdit_WC.setText("0")
        ui.dPhiLineEdit_WC.setText("0")
        ui.ALineEdit.setText("0")
        ui.BLineEdit.setText("0")

        # Clear the file path text box
        ui.textEditProcessedTxtPreview.clear()
        ui.textEditProcessedTempPreview.clear()

        print("All fields have been reset.")
    except Exception as e:
        print(f"Error during reset: {e}")


def open_directory(directory):
    """
    Open the specified directory in the system's file explorer.
    """
    if directory:
        if os.path.exists(directory):
            if platform.system() == "Windows":
                os.startfile(directory)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", directory])
            else:
                subprocess.Popen(["xdg-open", directory])
        else:
            print("Directory does not exist.")
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

        A = float(ui.ALineEdit.text()) if ui.ALineEdit.text() else 246.47
        B = float(ui.BLineEdit.text()) if ui.BLineEdit.text() else -0.627

        compute_water_content = ui.computeWaterContentCheckBox.isChecked()

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
        output_image_path, ert_plot_filename = startInversion(
            [start_x, start_z],
            [end_x, end_z],
            quality,
            area,
            inversion_params,
            processed_file_path
        )

        if output_image_path and os.path.exists(output_image_path):
            output_image_folder = os.path.dirname(output_image_path)
            global_inversion_params['output_image_folder'] = output_image_folder

        if ert_plot_filename and os.path.exists(ert_plot_filename):
            # Display ERT Plot
            pixmap_ert = QPixmap(ert_plot_filename)
            ui.labelERT.setPixmap(pixmap_ert)
            ui.labelERT.setScaledContents(True)
            ui.labelERT.setAlignment(QtCore.Qt.AlignCenter)
            print(f"ERT plot displayed: {ert_plot_filename}")

        if compute_water_content:
            try:
                # Run water content computation
                water_content_image_path = water_computing(
                    [start_x, start_z],
                    [end_x, end_z],
                    quality,
                    area,
                    lambda_value,
                    max_iterations,
                    dphi,
                    A,
                    B,
                    processed_file_path
                )

                # Display Water Content Image
                if water_content_image_path and os.path.exists(water_content_image_path):
                    pixmap_wc = QPixmap(water_content_image_path)
                    ui.labelSWC.setPixmap(pixmap_wc)
                    ui.labelSWC.setScaledContents(True)
                    ui.labelSWC.setAlignment(QtCore.Qt.AlignCenter)
                    global_inversion_params['output_image_folder'] = os.path.dirname(water_content_image_path)
                    print(f"Water content image displayed: {water_content_image_path}")
                else:
                    print("Water content image file not found.")

            except Exception as e:
                print(f"Error during water content computation: {e}")

        # Display Inversion Output Image
        if output_image_path and os.path.exists(output_image_path):
            pixmap = QPixmap(output_image_path)
            ui.labelDepthImage.setPixmap(pixmap)
            ui.labelDepthImage.setScaledContents(True)
            ui.labelDepthImage.setAlignment(QtCore.Qt.AlignCenter)
            print(f"Depth image displayed: {output_image_path}")
            ui.stackedWidget.setCurrentWidget(ui.page_2)
        else:
            print("Output image file not found.")
    else:
        print("No processed file selected. Please select a file first.")


def save_output_file(ui, MainWindow):
    options = QFileDialog.Options()
    file_name, _ = QFileDialog.getSaveFileName(MainWindow, "Save Output File", "", "Text Files (*.txt);;All Files (*)",
                                               options=options)
    if file_name:
        output_content = get_output_content(ui)
        with open(file_name, 'w') as file:
            file.write(output_content)
        print(f"Output saved to {file_name}")


def switch_to_page(ui, page):
    """
    Switch to the specified page of the stacked widget.
    """
    ui.stackedWidget.setCurrentWidget(page)


def get_output_content(ui):
    return ui.textEditProcessedTxtPreview.toPlainText()
