import os
import shutil
import threading
from PyQt5.QtWidgets import QFileDialog, QApplication
from pathlib import Path
from data_processor import convert_tx0_to_txt, filter_temperature_data_by_date, calibrate_resistivity


def setup_ui_logic(ui, MainWindow):
    """
    bind UI with logic

    :parameter
        ui: Ui_MainWindow instance。
        MainWindow: QMainWindow instance。
    """
    # Set dropbox
    ui.labelDropArea.setAcceptDrops(True)
    ui.labelDropArea.dragEnterEvent = lambda event: drag_enter_event(event)
    ui.labelDropArea.dropEvent = lambda event: drop_event(event, ui.textEditProcessedTxtPreview)

    # add event handler for browser button
    ui.pushButtonBrowserFiles.clicked.connect(lambda: open_file_browser(ui.textEditProcessedTxtPreview))

    # add event handler for start button (data processing)
    ui.pushButtonStartDataProcessing.clicked.connect(lambda: start_data_processing_thread(ui))

    # Add event handler for tab exit
    ui.actionExit.triggered.connect(lambda: exit_application(MainWindow))


def drag_enter_event(event):
    """
    handle drag event
    """
    if event.mimeData().hasUrls():
        event.acceptProposedAction()


def drop_event(event, text_edit):
    """
    handle drop event and print file directory
    """
    urls = event.mimeData().urls()
    files = [url.toLocalFile() for url in urls]
    target_directory = os.path.join(os.path.dirname(__file__), 'inputs/tx0_files')

    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    for file_path in files:
        if os.path.isfile(file_path):
            shutil.copy(file_path, target_directory)

    # show file dir
    text_edit.clear()
    for file in files:
        text_edit.append(file)


def open_file_browser(text_edit):
    """
    Open a dialog to add data files

    :parameter
        text_edit: show output txt dir
    """
    options = QFileDialog.Options()
    files, _ = QFileDialog.getOpenFileNames(None, "Select Files", "", "All Files (*);;Tx0 Files (*.tx0)",
                                            options=options)

    if files:
        target_directory = os.path.join(os.path.dirname(__file__), 'inputs/tx0_files')

        if not os.path.exists(target_directory):
            os.makedirs(target_directory)

        for file_path in files:
            if os.path.isfile(file_path):
                shutil.copy(file_path, target_directory)

        # show file dir
        text_edit.clear()
        for file in files:
            text_edit.append(file)


def start_data_processing_thread(ui):
    """
    Add a thread for data deletion

    :parameter
        ui: Ui_MainWindow instance.
    """
    processing_thread = threading.Thread(target=start_data_processing, args=(ui,))
    processing_thread.start()


def start_data_processing(ui):
    """
    logic after press start button

    :parameter
        ui: Ui_MainWindow instance
    """
    # get converter
    converter_choice = "1" if ui.XZcheckBox.isChecked() else "2"

    # select input and output
    current_folder = os.getcwd()
    tx0_input_folder = Path(current_folder, 'inputs/tx0_files')
    txt_output_folder = Path(current_folder, 'outputs/tmp/txt_files')
    filtered_temp_output = Path(current_folder, 'outputs/tmp/temperature_data/Newtem.txt')
    corrected_output_folder_detailed = Path(current_folder, 'outputs/corrected_resistivity_detailed')
    corrected_output_folder_simplified = Path(current_folder, 'outputs/corrected_resistivity_simplified')
    raw_temperature_file = Path(current_folder, 'inputs/raw_temperature_data/GNtemp.txt')

    # Step 1: Convert tx0 to txt
    convert_tx0_to_txt(tx0_input_folder, txt_output_folder, converter_choice)
    print("Conversion from tx0 to txt completed.")

    # Step 2: Filter temperature data by date
    filter_temperature_data_by_date(txt_output_folder, raw_temperature_file, filtered_temp_output)
    print("Temperature data filtering completed.")

    # Step 3: Calibrate resistivity
    calibrate_resistivity(txt_output_folder, corrected_output_folder_detailed, corrected_output_folder_simplified,
                          filtered_temp_output)
    print("Resistivity calibration completed.")

    print("Data processing completed.")


def exit_application(MainWindow):
    """
    exit application

    :parameter
        MainWindow: QMainWindow instance。
    """
    QApplication.quit()