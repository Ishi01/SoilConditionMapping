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
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir2, exist_ok=True)

    depths = [-4, -3.5, -3, -1.5, -1, -0.5]

    for file_name in os.listdir(data_dir):
        if file_name.endswith(".txt"):
            file_path = data_dir / file_name
            print(f"Processing file: {file_name}")

            try:
                with open(file_path, 'r') as f:
                    header_lines = [next(f) for _ in range(51)]

                data = pd.read_csv(file_path, skiprows=52, delim_whitespace=True,
                                   names=['a', 'b', 'm', 'n', 'resistivity', 'x', 'z'])
                data['z'] = pd.to_numeric(data['z'], errors='coerce')
                data['resistivity'] = pd.to_numeric(data['resistivity'], errors='coerce')

                date_str = file_name.split('_')[0]
                try:
                    date = pd.to_datetime(date_str).date()
                except ValueError:
                    print(f"Date format error in file name: {file_name}")
                    continue

                if date in temperature_dict:
                    temp_data = temperature_dict[date]
                    if temp_data.shape[1] < 7:
                        print(f"Temperature data format error for date {date}")
                        continue
                    temperatures = temp_data.iloc[0, 1:7].values.astype(float)
                    print(f"Temperatures for {date}: {temperatures}")

                    data['interpolated_temperature'] = data['z'].apply(
                        lambda z: interpolate_temperature(z, depths, temperatures))
                    data['corrected_resistivity'] = data.apply(
                        lambda row: apply_calibration(row['resistivity'], row['interpolated_temperature']), axis=1)

                    output_file_path = output_dir / file_name
                    output_file_path2 = output_dir2 / file_name

                    with open(output_file_path, 'w', newline='') as f:
                        f.writelines(header_lines)
                        f.write(
                            "# a    b   m   n   resistivity x   z   interpolated_temperature    corrected_resistivity\n")
                        data.to_csv(f, sep='\t', index=False, header=False, float_format='%g')

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


