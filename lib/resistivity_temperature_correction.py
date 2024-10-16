import os
import pandas as pd
import numpy as np


def load_temperature_data(temperature_file):
    print(f"Loading temperature data from {temperature_file}")
    try:
        temperature_data = pd.read_csv(temperature_file, sep="\t", parse_dates=['time'])
        temperature_data['date'] = temperature_data['time'].dt.date
        temperature_dict = {}
        for date, group in temperature_data.groupby('date'):
            temperature_dict[date] = group
        print(f"Loaded temperature data for {len(temperature_dict)} days.")
        return temperature_dict
    except FileNotFoundError:
        print(f"Temperature file {temperature_file} not found.")
        return {}
    except Exception as e:
        print(f"Error loading file: {e}")
        return {}


def interpolate_temperature(z, depths, temperatures):
    if z < min(depths):
        return temperatures[0]
    elif z > max(depths):
        return temperatures[-1]
    return np.interp(z, depths, temperatures)


def apply_calibration(resistivity, temperature):
    if temperature is None or np.isnan(temperature):
        return None
    return resistivity * (1 + 0.025 * (temperature - 25))


def process_files(data_dir, output_dir, output_dir2, temperature_dict):
    """
    Process files in the input directory, apply temperature correction, and save the results.

    Args:
    - data_dir: Directory containing input .txt files
    - output_dir: Directory for detailed output files
    - output_dir2: Directory for simplified output files
    - temperature_dict: Dictionary containing temperature data grouped by date
    """
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir2, exist_ok=True)

    depths = [-4, -3.5, -3, -1.5, -1, -0.5]  # List of depths for temperature interpolation

    for file_name in os.listdir(data_dir):
        if file_name.endswith(".txt"):
            file_path = os.path.join(data_dir, file_name)
            print(f"Processing file: {file_name}")

            try:
                # Step 1: Read file header (first 51 lines)
                with open(file_path, 'r') as f:
                    header_lines = [next(f) for _ in range(51)]

                # Step 2: Read the data section and ensure numeric data types for 'resistivity' and 'z'
                data = pd.read_csv(file_path, skiprows=52, delim_whitespace=True,
                                   names=['a', 'b', 'm', 'n', 'resistivity', 'x', 'z'])

                # Ensure that 'resistivity' and 'z' are numeric. Non-numeric entries will be converted to NaN.
                data['z'] = pd.to_numeric(data['z'], errors='coerce')
                data['resistivity'] = pd.to_numeric(data['resistivity'], errors='coerce')

                # Drop rows where 'z' or 'resistivity' are NaN (invalid data)
                data.dropna(subset=['z', 'resistivity'], inplace=True)

                # Step 3: Extract the date from the filename
                date_str = file_name.split('_')[0]
                try:
                    date = pd.to_datetime(date_str).date()
                except ValueError:
                    print(f"Date format error in file name: {file_name}")
                    continue

                # Step 4: Apply temperature correction if temperature data is available for the date
                if date in temperature_dict:
                    temp_data = temperature_dict[date]
                    if temp_data.shape[1] < 7:  # Ensure there are at least 6 temperature columns
                        print(f"Temperature data format error for date {date}")
                        continue
                    temperatures = temp_data.iloc[0, 1:7].values.astype(float)
                    print(f"Temperatures for {date}: {temperatures}")

                    # Step 5: Interpolate temperatures for each depth and apply resistivity calibration
                    data['interpolated_temperature'] = data['z'].apply(
                        lambda z: interpolate_temperature(z, depths, temperatures))
                    data['corrected_resistivity'] = data.apply(
                        lambda row: apply_calibration(row['resistivity'], row['interpolated_temperature']), axis=1)

                    # Step 6: Save results to the output directories
                    output_file_path = os.path.join(output_dir, file_name)
                    output_file_path2 = os.path.join(output_dir2, file_name)

                    # Detailed output file (includes interpolated temperature and corrected resistivity)
                    with open(output_file_path, 'w', newline='') as f:
                        f.writelines(header_lines)
                        f.write(
                            "# a    b   m   n   resistivity   x   z   interpolated_temperature   corrected_resistivity\n")
                        data.to_csv(f, sep='\t', index=False, header=False, float_format='%g')

                    # Simplified output file (only includes corrected resistivity)
                    with open(output_file_path2, 'w') as f:
                        f.writelines(header_lines)
                        f.write("# a    b    m    n    rhoa\n")
                        for _, row in data.iterrows():
                            f.write(
                                f"{int(row['a']):>6}\t{int(row['b']):>6}\t{int(row['m']):>6}\t{int(row['n']):>6}\t{row['corrected_resistivity']:>15.2f}\n")

                    print(f"Processed and saved: {output_file_path}")
                    print(f"Processed and saved: {output_file_path2}")
                else:
                    print(f"No temperature data available for the date in {file_name}")

            except FileNotFoundError:
                print(f"Data file {file_name} not found")
            except Exception as e:
                print(f"Error loading {file_name}: {e}")



