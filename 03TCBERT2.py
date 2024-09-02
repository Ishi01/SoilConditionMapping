import os
import pandas as pd
import numpy as np
from datetime import datetime

def load_temperature_data(temperature_file):
    print(f"Loading temperature data from {temperature_file}")
    temperature_data = pd.read_csv(temperature_file, sep="\t", parse_dates=['time'])
    temperature_dict = {row['time']: row for index, row in temperature_data.iterrows()}
    print(f"Loaded temperature data for {len(temperature_dict)} entries.")
    return temperature_dict

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

def find_nearest_temperature(time, temperature_dict):
    target_time = datetime.strptime(time, '%Y-%m-%d_%H-%M-%S')
    nearest_time = min(temperature_dict.keys(), key=lambda x: abs(x - target_time))
    return temperature_dict[nearest_time]

def process_files(data_dir, output_dir, output_dir2, temperature_dict):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    if not os.path.exists(output_dir2):
        os.makedirs(output_dir2)
        print(f"Created output directory: {output_dir2}")

    depths = [-4, -3.5, -3, -1.5, -1, -0.5]

    for file_name in os.listdir(data_dir):
        if file_name.endswith(".txt"):
            file_path = os.path.join(data_dir, file_name)
            print(f"Processing file: {file_name}")
            with open(file_path, 'r') as f:
                header_lines = [next(f) for _ in range(51)]

            data = pd.read_csv(file_path, skiprows=52, delim_whitespace=True, names=['a', 'b', 'm', 'n', 'resistivity', 'x', 'z'])
            data['z'] = pd.to_numeric(data['z'], errors='coerce')
            data['resistivity'] = pd.to_numeric(data['resistivity'], errors='coerce')

            date_str = file_name.split('.')[0]  # Assuming format is 'YYYY-MM-DD_HH-MM-SS.txt'
            nearest_temp_data = find_nearest_temperature(date_str, temperature_dict)
            temperatures = nearest_temp_data[1:7].values.astype(float)
            
            data['interpolated_temperature'] = data['z'].apply(lambda z: interpolate_temperature(z, depths, temperatures))
            data['corrected_resistivity'] = data.apply(lambda row: apply_calibration(row['resistivity'], row['interpolated_temperature']), axis=1)
            
            output_file_path = os.path.join(output_dir, file_name)
            output_file_path2 = os.path.join(output_dir2, file_name)
            with open(output_file_path, 'w') as f:
                f.writelines(header_lines)
                f.write("# a    b    m    n    resistivity    x    z    interpolated_temperature    corrected_resistivity\n")
                data.to_csv(f, sep='\t', index=False, header=False, float_format='%g')
            with open(output_file_path2, 'w') as f:
                f.writelines(header_lines)
                f.write("# a    b    m    n    rhoa\n")
                for _, row in data.iterrows():
                    f.write(f"{int(row['a']):>6}\t{int(row['b']):>6}\t{int(row['m']):>6}\t{int(row['n']):>6}\t{row['corrected_resistivity']:>15.2f}\n")

            print(f"Processed and saved: {output_file_path}")
            print(f"Processed and saved: {output_file_path2}")

data_dir = "./02GNres2check"
output_dir = "./03bertTCdetail"
output_dir2 = "./03bertTC"
temperature_file = "./Newtem.txt"

temperature_dict = load_temperature_data(temperature_file)
process_files(data_dir, output_dir, output_dir2, temperature_dict)
