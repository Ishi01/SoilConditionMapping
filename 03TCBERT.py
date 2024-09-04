import os
import pandas as pd
import numpy as np

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
data_dir = "02GNres2check"  # Input data directory
                            # 输入数据目录
output_dir = "03bertTCdetail"  # Detailed output directory
                               # 详细输出目录
output_dir2 = "03bertTC"  # Simplified output directory
                          # 简化输出目录
temperature_file = "Newtem.txt"  # Temperature data file
                                 # 温度数据文件

# Load temperature data
# 加载温度数据
temperature_dict = load_temperature_data(temperature_file)
# Process files
# 处理文件
process_files(data_dir, output_dir, output_dir2, temperature_dict)