"""
Created on  August 21  2024

@author: 23829101 Long Qin

Correcting the offset in the measurement data if the first electrode index (a) does not start at 1.

Columns :            a  b  m  n  rhoa
WITHOUT  columns:    X  and  Z
"""


import os

#  You can change the input and output path as need.   
# Here I am  using the current working directory as the input and output folder paths
current_folder = os.getcwd()
input_folder = current_folder
output_folder = os.path.join(current_folder, 'output')

# Ensure the output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Loop through each input file in the directory
for filename in os.listdir(input_folder):
    if filename.endswith('.tx0'):
        # Construct the input file path
        input_file_path = os.path.join(input_folder, filename)
        
        # Construct the output file name
        output_file_name = filename.replace('.tx0', '.txt')
        
        # Construct the output file path
        output_file_path = os.path.join(output_folder, output_file_name)
        
        # Read the file content
        with open(input_file_path, 'r') as input_file:
            lines = input_file.readlines()
        
        # Process electrode position data
        electrode_data = []
        electrode_start = False
        for line in lines:
            if '* Electrode positions' in line:
                electrode_start = True
                continue
            if '* Remote electrode positions' in line:
                break
            if electrode_start and '* Electrode [' in line:
                parts = line.split('=')[1].strip().split()
                x = parts[0].strip()
                z = parts[2].strip()
                electrode_data.append(f"{x}     {z}")
        
        num_electrodes = len(electrode_data)

        # Process measurement data
        measurement_data = []
        measurement_start = False
        for line in lines:
            if '* Data' in line and '*******************' in line:
                measurement_start = True
                continue
            if measurement_start and line.strip() and not line.startswith('*'):
                parts = line.split()
                 # Ensure the line has enough data
                if len(parts) < 22: 
                    continue
                a, b, m, n = parts[1], parts[2], parts[3], parts[4]
                rho = parts[10]
                measurement_data.append(f"{a} {b} {m} {n} {rho}")

        # Correct the offset if the first electrode index does not start at 1
        if measurement_data:
            first_a = int(measurement_data[0].split()[0])
            if first_a != 1:
                offset = first_a - 1
                new_measurement_data = []
                for line in measurement_data:
                    parts = line.split()
                    a, b, m, n = int(parts[0]) - offset, int(parts[1]) - offset, int(parts[2]) - offset, int(parts[3]) - offset
                    new_line = f"{a} {b} {m} {n} {parts[4]}"
                    new_measurement_data.append(new_line)
                measurement_data = new_measurement_data

        num_measurements = len(measurement_data)

        # Write the processed data to the output file
        with open(output_file_path, 'w') as output_file:
            output_file.write(f"{num_electrodes}# Number of electrodes\n")
            output_file.write("# x z\n")
            for line in electrode_data:
                output_file.write(line + "\n")
            
            output_file.write(f"{num_measurements}# Number of data\n")
            output_file.write("# a b m n rhoa\n")
            for i, line in enumerate(measurement_data, 1):
                output_file.write(f"{line}\n")
        
        print(f"Data extraction and conversion completed for {filename}.")

print("All files processed successfully.")
