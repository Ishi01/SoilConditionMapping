import os
import shutil
import threading
from PyQt5.QtWidgets import QFileDialog, QApplication, QDialogButtonBox
from pathlib import Path
from data_processor import convert_tx0_to_txt, filter_temperature_data_by_date, calibrate_resistivity
import tempfile
import subprocess
import platform
from data_inversion.ERT_Main import startInversion, cleanup_temp_files

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
    ui.buttonBoxResetConfirmSave.button(QDialogButtonBox.Reset).clicked.connect(lambda: reset_all_fields(ui))

    # Set up the "Save" button click event to save the output
    ui.buttonBoxResetConfirmSave.button(QDialogButtonBox.Reset).clicked.connect(lambda: save_output_file(ui, MainWindow))


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
    threading.Thread(target=startInversion, args=([start_x, start_z], [end_x, end_z], quality, area),
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

def select_processed_file():
    """
    Open Browser to select processed files
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


def select_processed_file():
    """
    打开文件选择对话框以选择处理好的文件（如.txt等），并返回其路径。
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

    Parameters:
        ui: Instance of Ui_MainWindow.
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
        # Optionally handle the error by showing a message box or logging
        return

    processed_file_path = select_processed_file()

    if processed_file_path:
        inversion_params = {
            "lambda": lambda_value,
            "max_iterations": max_iterations,
            "dphi": dphi,
            "robust_data": robust_data
        }

        # Start inversion process using the selected file and parameters
        threading.Thread(target=startInversion, args=([start_x, start_z], [end_x, end_z], quality, area),
                         kwargs={"inversion_params": inversion_params, "file_path": processed_file_path}).start()
    else:
        print("No processed file selected. Please select a file first.")


def save_output_file(ui, MainWindow):
    options = QFileDialog.Options()
    file_name, _ = QFileDialog.getSaveFileName(MainWindow, "Save Output File", "", "Text Files (*.txt);;All Files (*)", options=options)
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

