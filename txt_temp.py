 #   original  name is  03TCBERT.py
 #   New name  is txt_temp.py

import os
import shutil
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog


def tx0_to_txt_offset(input_folder, output_folder):
    """
    Created on August 21, 2024

    @author: 23829101 Long Qin

    Columns : a  b  m  n  rhoa  x z

    Correcting the offset in the measurement data if the first electrode index (a) does not start at 1.
    """

    # Ensure the output folder exists
    #This shouldn't be necessary anymore but no harm in keeping it so 
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
                    if len(parts) < 22:  # Ensure the line has enough data
                        continue
                    a, b, m, n = parts[1], parts[2], parts[3], parts[4]
                    rho = parts[10]
                    x = parts[18]
                    z = parts[20]
                    measurement_data.append(f"{a} {b} {m} {n} {rho} {x} {z}")

            # Correct the offset if the first electrode index does not start at 1
            if measurement_data:
                first_a = int(measurement_data[0].split()[0])
                if first_a != 1:
                    offset = first_a - 1       
                    new_measurement_data = []
                    for line in measurement_data:
                        parts = line.split()
                        a, b, m, n = int(parts[0]) - offset, int(parts[1]) - offset, int(parts[2]) - offset, int(parts[3]) - offset
                        new_line = f"{a} {b} {m} {n} {parts[4]} {parts[5]} {parts[6]}"
                        new_measurement_data.append(new_line)

                    measurement_data = new_measurement_data
                    # The following two lines  can be deleted, it is used for debugging 
                    for line in measurement_data:
                        print(line)

            num_measurements = len(measurement_data)
            # Write the processed data to the output file
            with open(output_file_path, 'w') as output_file:
                output_file.write(f"{num_electrodes}# Number of electrodes\n")
                output_file.write("# x z\n")
                for line in electrode_data:
                    output_file.write(line + "\n")
                
                output_file.write(f"{num_measurements}# Number of data\n")
                output_file.write("# a b m n rhoa x z\n")
                for i, line in enumerate(measurement_data, 1):
                    output_file.write(f"{line}\n")
            
            print(f"Data extraction and conversion completed for {filename}.")

    print("All files processed successfully.")



def load_temperature_data(temperature_file):
    # Load temperature data from file
    # 从文件加载温度数据
    print(f"Loading temperature data from {temperature_file}")
    temperature_data = pd.read_csv(temperature_file, sep="\t", parse_dates=['time'])
    # Extract date
    # 提取日期
    temperature_data['date'] = temperature_data['time'].dt.date
    temperature_dict = {}
    # Group by date and store in dictionary
    # 按日期分组并存储在字典中
    for date, group in temperature_data.groupby('date'):
        temperature_dict[date] = group
    print(f"Loaded temperature data for {len(temperature_dict)} days.")
    return temperature_dict

def interpolate_temperature(z, depths, temperatures):
    # Interpolate temperature for a given depth
    # 对给定深度插值温度
    if z < min(depths):
        return temperatures[0]  # If depth is less than minimum, return shallowest temperature
                                # 如果深度小于最小深度,返回最浅处温度
    elif z > max(depths):
        return temperatures[-1]  # If depth is greater than maximum, return deepest temperature
                                 # 如果深度大于最大深度,返回最深处温度
    return np.interp(z, depths, temperatures)  # Linear interpolation
                                               # 线性插值

def apply_calibration(resistivity, temperature):
    # Apply temperature calibration to resistivity
    # 应用温度校正到电阻率
    if temperature is None or np.isnan(temperature):
        return None
    return resistivity * (1 + 0.025 * (temperature - 25))  # Calibration formula
                                                          # 校正公式

def process_files(data_dir, output_dir, output_dir2, temperature_dict):
    # Ensure output directories exist
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    if not os.path.exists(output_dir2):
        os.makedirs(output_dir2)
        print(f"Created output directory: {output_dir2}")

    depths = [-4, -3.5, -3, -1.5, -1, -0.5]  # Temperature measurement depths
                                             # 温度测量深度

    for file_name in os.listdir(data_dir):
        if file_name.endswith(".txt"):
            file_path = os.path.join(data_dir, file_name)
            print(f"Processing file: {file_name}")

            # Read file header
            # 读取文件头
            with open(file_path, 'r') as f:
                header_lines = [next(f) for _ in range(51)]

            # Read data section
            # 读取数据部分
            data = pd.read_csv(file_path, skiprows=52, delim_whitespace=True, 
                               names=['a', 'b', 'm', 'n', 'resistivity', 'x', 'z'])
            data['z'] = pd.to_numeric(data['z'], errors='coerce')
            data['resistivity'] = pd.to_numeric(data['resistivity'], errors='coerce')

            # Extract date from filename
            # 从文件名提取日期
            date_str = file_name.split('_')[0]
            date = pd.to_datetime(date_str).date()
            print(f"Extracted date: {date}")

            if date in temperature_dict:
                temp_data = temperature_dict[date]
                temperatures = temp_data.iloc[0, 1:7].values.astype(float)
                print(f"Temperatures for {date}: {temperatures}")
                
                # Interpolate temperatures and correct resistivity
                # 插值温度并校正电阻率
                data['interpolated_temperature'] = data['z'].apply(lambda z: interpolate_temperature(z, depths, temperatures))
                data['corrected_resistivity'] = data.apply(lambda row: apply_calibration(row['resistivity'], row['interpolated_temperature']), axis=1)
                
                # Save detailed output
                # 保存详细输出
                output_file_path = os.path.join(output_dir, file_name)
                output_file_path2 = os.path.join(output_dir2, file_name)

                with open(output_file_path, 'w') as f:
                    f.writelines(header_lines)
                    f.write("# a    b    m    n    resistivity    x    z    interpolated_temperature    corrected_resistivity\n")
                    data.to_csv(f, sep='\t', index=False, header=False, float_format='%g')  # Keep integers as integers
                                                                                            # 保持整数格式

                # Save simplified output
                # 保存简化输出
                with open(output_file_path2, 'w') as f:
                    f.writelines(header_lines)
                    f.write("# a    b    m    n    rhoa\n")
                    for _, row in data.iterrows():
                        f.write(f"{int(row['a']):>6}\t{int(row['b']):>6}\t{int(row['m']):>6}\t{int(row['n']):>6}\t{row['corrected_resistivity']:>15.2f}\n")

                print(f"Processed and saved: {output_file_path}")
                print(f"Processed and saved: {output_file_path2}")
            else:
                print(f"No temperature data available for the date in {file_name}")

# Main program
# 主程序

def main():

    #get current directory for starting point of askdirectory function
    current_dir = os.getcwd()

    #get the input directory
    input_dialogue_title = "Please select the input folder"
    inputpath = filedialog.askdirectory(initialdir=current_dir, title=input_dialogue_title)
    #list the output directory path
    outputpath = os.path.join(current_dir, "output_txt_offset")

    #pass them to the convert function
    tx0_to_txt_offset(inputpath, outputpath)

    data_dir = "output_txt_offset"  # Input data directory
                                    # 输入数据目录
   
    #define title for file dialogue
    d_out_dir_msg = "Please select the detailed output directory"
    #get output_dir using a file_dialgue and user selection
    output_dir = filedialog.askdirectory(initialdir=current_dir, title=d_out_dir_msg)
    # output_dir = "txt_corr_temp_detail"  # Detailed output directory
                                # 详细输出目录
    #define title for simple file dialogue
    s_out_dir_msg = "Please select the simplified output directory"
    #get the location of the simplified output-directory
    output_dir2 = filedialog.askdirectory(initialdir=current_dir, title=s_out_dir_msg)
    #output_dir2 = "txt_corr_temp"  # Simplified output directory
                            # 简化输出目录

    #use the temperature file output by the previous file
    temperature_file = "Newtem.txt"  # Temperature data file
                                    # 温度数据文件

    # Load temperature data
    # 加载温度数据
    temperature_dict = load_temperature_data(temperature_file)
    # Process files
    # 处理文件
    process_files(data_dir, output_dir, output_dir2, temperature_dict)

    #clean up data used mid-processing
    shutil.rmtree('output_txt_offset')