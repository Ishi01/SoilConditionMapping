"""
Created on  August 15  2024

@author: 23829101 Long Qin
"""

import os

# 使用当前工作目录作为输入和输出文件夹路径
current_folder = os.getcwd()
input_folder = current_folder
output_folder = os.path.join(current_folder, 'output')

# ENsure output folder exists 确保输出文件夹存在
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# loop through each input file 循环处理每个输入文件
for filename in os.listdir(input_folder):
    if filename.endswith('.tx0'):
        # construct input file path 构建输入文件路径
        input_file_path = os.path.join(input_folder, filename)
        
        # construct output file 构建输出文件名
        output_file_name = filename.replace('.tx0', '.txt')
        
        # construct output file path 构建输出文件路径
        output_file_path = os.path.join(output_folder, output_file_name)
        
        # read the input file .tx0 读取文件内容
        with open(input_file_path, 'r') as input_file:
            lines = input_file.readlines()
        
        # deal with position of electrode 处理电极位置数据
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
        
        # deal with data 处理测量数据
        measurement_data = []
        measurement_start = False
        for line in lines:
            if '* Data' in line and '*******************' in line:
                measurement_start = True
                continue
            if measurement_start and line.strip() and not line.startswith('*'):
                parts = line.split()
                if len(parts) < 22:  # ensure enough columns 确保行有足够的数据
                    continue
                a, b, m, n = parts[1], parts[2], parts[3], parts[4]
                rho = parts[10]
                x = parts[16]
                z = parts[20]
                measurement_data.append(f"{a} {b} {m} {n} {rho} {x} {z}")
        
        num_measurements = len(measurement_data)
        
        # write the content to the output file 写入输出文件
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
