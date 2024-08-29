import os
from pathlib import Path
from lib.Tx0ToTxtPolymorph import NoXZTx0ToTxtConverter, Tx0ToTxtConverter
from lib.data_filter import extract_dates_from_filenames, filter_temperature_data
from lib.resistivity_temperature_correction import load_temperature_data, process_files


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
    """Filter temperature data based on the dates extracted from txt filenames."""
    dates = extract_dates_from_filenames(txt_data_dir)
    filter_temperature_data(raw_temp_file, dates, output_temp_file)
    print(f"Temperature data filtered and saved to {output_temp_file}")


def calibrate_resistivity(input_folder, output_dir_detailed, output_dir_simplified, temperature_file):
    """Calibrate resistivity using the temperature data."""
    temperature_dict = load_temperature_data(temperature_file)
    process_files(input_folder, output_dir_detailed, output_dir_simplified, temperature_dict)
    print("Resistivity calibration completed.")


def main():
    current_folder = os.getcwd()
    tx0_input_folder = Path(current_folder, 'inputs/tx0_files')
    txt_output_folder = Path(current_folder, 'outputs/tmp/txt_files')
    filtered_temp_output = Path(current_folder, 'outputs/tmp/temperature_data/Newtem.txt')
    corrected_output_folder_detailed = Path(current_folder, 'outputs/corrected_resistivity_detailed')
    corrected_output_folder_simplified = Path(current_folder, 'outputs/corrected_resistivity_simplified')
    raw_temperature_file = Path(current_folder, 'inputs/raw_temperature_data/GNtemp.txt')

    # Step 1: Convert tx0 to txt
    print("Select Converter:")
    print("1: Offset Converter (Tx0ToTxtConverter)")
    print("2: Offset Converter without X and Z axis (NoXZTx0ToTxtConverter)")
    converter_choice = input("Input number (1 or 2): ")
    convert_tx0_to_txt(tx0_input_folder, txt_output_folder, converter_choice)

    # Step 2: Filter temperature data by date
    filter_temperature_data_by_date(txt_output_folder, raw_temperature_file, filtered_temp_output)

    # Step 3: Calibrate resistivity
    calibrate_resistivity(txt_output_folder, corrected_output_folder_detailed, corrected_output_folder_simplified,
                          filtered_temp_output)


if __name__ == "__main__":
    main()
