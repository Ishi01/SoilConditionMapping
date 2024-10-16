import os
from lib.Tx0ToTxtPolymorph import NoXZTx0ToTxtConverter, Tx0ToTxtConverter
from lib.data_filter import extract_dates_from_filenames, filter_temperature_data
from lib.resistivity_temperature_correction import load_temperature_data, process_files
import pandas as pd


def convert_tx0_to_txt(input_folder, output_folder, converter_choice):
    """Convert tx0 files to txt files using the selected converter."""
    if converter_choice == "1":
        converter = Tx0ToTxtConverter(input_folder, output_folder)
    elif converter_choice == "2":
        converter = NoXZTx0ToTxtConverter(input_folder, output_folder)
    else:
        print("Invalid converter option. Please choose 1 or 2.")
        return

    converter.ensure_output_folder_exists()
    for filename in os.listdir(input_folder):
        if filename.endswith('.tx0'):
            converter.process_file(filename)
    print("Conversion from tx0 to txt completed.")


def filter_temperature_data_by_date(txt_data_dir, raw_temp_file, output_temp_file):
    try:
        print(f"Starting temperature data filtering with raw temperature file: {raw_temp_file}")
        dates = extract_dates_from_filenames(txt_data_dir)
        print(f"Extracted dates from txt filenames: {dates}")

        # Check if dates are correctly extracted
        if not dates or not all(pd.to_datetime(d, errors='coerce') for d in dates):
            print("No valid dates extracted from txt filenames. Check the txt files or extraction logic.")
            return

        filter_temperature_data(raw_temp_file, dates, output_temp_file)
        print(f"Temperature data filtered and saved to {output_temp_file}")

    except Exception as e:
        print(f"Error during temperature data filtering: {e}")



def calibrate_resistivity(input_folder, output_dir_detailed, output_dir_simplified, temperature_file):
    """Calibrate resistivity using the temperature data."""
    try:
        print(f"Starting resistivity calibration with temperature file: {temperature_file}")

        if not os.path.exists(temperature_file):
            print("Temperature file does not exist.")
            return

        temperature_dict = load_temperature_data(temperature_file)
        print(f"Loaded temperature data: {temperature_dict}")

        if not temperature_dict:
            print("Temperature data is empty or invalid.")
            return

        process_files(input_folder, output_dir_detailed, output_dir_simplified, temperature_dict)
        print("Resistivity calibration completed.")
    except Exception as e:
        print(f"Error during resistivity calibration: {e}")

