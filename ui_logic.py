import os
import shutil
import threading
from PyQt5.QtWidgets import QFileDialog, QApplication
from pathlib import Path

from PyQt5.uic.properties import QtWidgets

from ERT_Main import inversion
from data_processor import convert_tx0_to_txt, filter_temperature_data_by_date, calibrate_resistivity
import tempfile
import subprocess
import platform

# Global variables to store file paths
global_tx0_input_folder = None  # Global variable to store the path of the tx0 folder
global_selected_temperature_file = None  # Global variable to store the selected temperature file path


def setup_ui_logic(ui, MainWindow):
    """
    Bind UI events and logic.

    Parameters:
        ui: Instance of Ui_MainWindow.
        MainWindow: Instance of QMainWindow.
    """
    # Set up the "Browser" button click event for Tx0 files
    ui.pushButtonBrowserFiles.clicked.connect(lambda: open_file_browser(ui.textEditProcessedTxtPreview, tx0=True))

    # Set up the "Browser" button click event for Temperature files
    ui.pushButtonBrowserTempFiles.clicked.connect(lambda: open_file_browser(ui.textEditProcessedTempPreview, tx0=False))

    # Set up the "Start" button click event (for data processing)
    ui.pushButtonStartDataProcessing.clicked.connect(lambda: start_data_processing_thread(ui))

    # Set up "OK" button to capture inversion parameters and start inversion
    ui.buttonBoxResetConfirmSave.accepted.connect(lambda: start_inversion_with_parameters(ui))

    # Set up the "Exit" menu exit event
    ui.actionExit.triggered.connect(lambda: exit_application(MainWindow))

    # Set up "OpenTx0Dir" button click event
    ui.pushButtonOpenTx0Dir.clicked.connect(lambda: open_directory(global_tx0_input_folder))

    # Set up "OpenTempDir" button click event
    ui.pushButtonTempDir.clicked.connect(lambda: open_directory(global_selected_temperature_file))

    # Set up the "Reset" button click event to reset all inputs
    ui.buttonBoxResetConfirmSave.button(QtWidgets.QDialogButtonBox.Reset).clicked.connect(lambda: reset_all_fields(ui))

    # Set up the "Save" button click event to save the output
    ui.buttonBoxResetConfirmSave.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(lambda: save_output_file(ui))

def start_inversion_with_parameters(ui):
    """
    Capture inversion parameters from the UI and initiate inversion processing.

    Parameters:
        ui: Instance of Ui_MainWindow.
    """
    # Capture inversion parameters from the UI
    start_x = float(ui.startXLineEdit.text()) if ui.startXLineEdit.text() else 0
    start_z = float(ui.startZLineEdit.text()) if ui.startZLineEdit.text() else 0
    end_x = float(ui.endXLineEdit.text()) if ui.endXLineEdit.text() else 47
    end_z = float(ui.endZLineEdit.text()) if ui.endZLineEdit.text() else -8
    quality = float(ui.horizontalSlider.value())
    area = float(ui.areaLineEdit.text()) if ui.areaLineEdit.text() else 0.5
    lambda_value = float(ui.LambdaLineEdit.text()) if ui.LambdaLineEdit.text() else 0.1
    max_iterations = int(ui.IterationLineEdit.text()) if ui.IterationLineEdit.text() else 10
    dphi = float(ui.dPhiLineEdit.text()) if ui.dPhiLineEdit.text() else 0.01
    robust_data = ui.checkBox.isChecked()

    # Pack parameters into dictionary
    inversion_params = {
        "lambda": lambda_value,
        "max_iterations": max_iterations,
        "dphi": dphi,
        "robust_data": robust_data
    }

    # Start inversion process using ERT_Main's inversion function
    threading.Thread(target=inversion, args=([start_x, start_z], [end_x, end_z], quality, area),
                     kwargs={"inversion_params": inversion_params}).start()



def open_file_browser(text_edit, tx0=True):
    """
    Open a file selection dialog and copy selected files to the specified directory.

    Parameters:
        text_edit: QTextEdit component to display selected file paths.
        tx0: Boolean to determine if selecting tx0 files or temperature file.
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


def start_data_processing_thread(ui):
    """
    Start a thread for data processing.

    Parameters:
        ui: Instance of Ui_MainWindow.
    """
    processing_thread = threading.Thread(target=start_data_processing, args=(ui,))
    processing_thread.start()


def start_data_processing(ui):
    """
    Logic to execute when the "Start" button is clicked.

    Parameters:
        ui: Instance of Ui_MainWindow.
    """
    global global_tx0_input_folder
    global global_selected_temperature_file

    # Get the converter option
    converter_choice = "1" if ui.XZcheckBox.isChecked() else "2"

    # If the tx0 folder is not set, prompt the user to select it
    if not global_tx0_input_folder:
        print("Please use the 'Browser' button to select tx0 files first.")
        return

    # If the temperature file is not set, prompt the user to select it
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

    Parameters:
        MainWindow: Instance of QMainWindow.
    """
    QApplication.quit()


def reset_all_fields(ui):
    """
    Reset all input fields in the UI to their default values.

    Parameters:
        ui: Instance of Ui_MainWindow.
    """
    # Reset geometry and inversion parameters
    ui.startXLineEdit.setText("0")
    ui.startZLineEdit.setText("0")
    ui.endXLineEdit.setText("47")
    ui.endZLineEdit.setText("-8")
    ui.qualityLineEdit.setText("33.5")
    ui.horizontalSlider.setValue(33)  # Set the slider to a default position corresponding to quality 33.5
    ui.areaLineEdit.setText("0.5")
    ui.LambdaLineEdit.setText("0.1")
    ui.IterationLineEdit.setText("10")
    ui.dPhiLineEdit.setText("0.01")
    ui.checkBox.setChecked(False)  # Uncheck the "Robust Data" checkbox

    # Clear text edits for file paths
    ui.textEditProcessedTxtPreview.clear()
    ui.textEditProcessedTempPreview.clear()

def get_output_content(ui):
    """
    Retrieves the output content from the UI components to be saved in a file.

    Parameters:
        ui: Instance of Ui_MainWindow.

    Returns:
        A string containing the formatted output content to be saved.
    """
    # Gather inversion parameters from the UI
    start_x = ui.startXLineEdit.text()
    start_z = ui.startZLineEdit.text()
    end_x = ui.endXLineEdit.text()
    end_z = ui.endZLineEdit.text()
    quality = ui.qualityLineEdit.text()
    area = ui.areaLineEdit.text()
    lambda_value = ui.LambdaLineEdit.text()
    max_iterations = ui.IterationLineEdit.text()
    dphi = ui.dPhiLineEdit.text()
    robust_data = ui.checkBox.isChecked()

    # Get file paths from text edits
    processed_txt_files = ui.textEditProcessedTxtPreview.toPlainText()
    processed_temp_files = ui.textEditProcessedTempPreview.toPlainText()

    # Format the collected data into a string for saving
    output_content = (
        "Inversion Parameters:\n"
        f"Start X: {start_x}\n"
        f"Start Z: {start_z}\n"
        f"End X: {end_x}\n"
        f"End Z: {end_z}\n"
        f"Quality: {quality}\n"
        f"Area: {area}\n"
        f"Lambda: {lambda_value}\n"
        f"Max Iterations: {max_iterations}\n"
        f"dPhi: {dphi}\n"
        f"Robust Data: {'Yes' if robust_data else 'No'}\n\n"
        "Processed Tx0 Files:\n"
        f"{processed_txt_files}\n\n"
        "Processed Temperature Files:\n"
        f"{processed_temp_files}\n"
    )

    return output_content



def open_directory(directory):
    """
    Open the specified directory in the system's file explorer.

    Parameters:
        directory: Path to the directory to open.
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


def save_output_file(ui, MainWindow):
    """
    Opens a file dialog to allow the user to save the output to a location on their computer.

    Parameters:
        ui: Instance of Ui_MainWindow.
        MainWindow: Instance of QMainWindow.
    """
    # Open a file dialog to select the location and filename to save the output
    options = QFileDialog.Options()
    file_name, _ = QFileDialog.getSaveFileName(MainWindow, "Save Output File", "", "Text Files (*.txt);;All Files (*)", options=options)

    if file_name:
        # Define what to save in the output file
        output_content = get_output_content(ui)  # Define the method to get the content to be saved

        # Write the output content to the selected file
        with open(file_name, 'w') as file:
            file.write(output_content)
        print(f"Output saved to {file_name}")