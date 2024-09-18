import re
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

def extract_datetime_from_filename(filename):
    """
    Extracts the date and time from a filename using regex patterns.
    
    Parameters:
        filename (str): The filename to extract the date and time from.
    
    Returns:
        tuple or None: A tuple containing the extracted date in 'YYYY-MM-DD' format 
                       and time in 'HH:MM:SS' format, or None if not found.
    """
    # Try matching the 'YYYY-MM-DD_HH-MM-SS' format
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})', filename)
    if match:
        date = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        time = f"{match.group(4)}:{match.group(5)}:{match.group(6)}"
        return date, time

    # Try matching the 'YYYY-MM-DD' format
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
    if match:
        return match.group(0), None

    # Try matching the 'DD_MM_YYYY' format
    match = re.search(r'(\d{2})_(\d{2})_(\d{4})', filename)
    if match:
        day, month, year = match.groups()
        return f"{year}-{month}-{day}", None

    # Try matching the 'YYYY_MM_DD' format
    match = re.search(r'(\d{4})_(\d{2})_(\d{2})', filename)
    if match:
        year, month, day = match.groups()
        return f"{year}-{month}-{day}", None

    return None

# 测试函数
test_filenames = [
    "2024-07-10_12-00-00.txt",
    "2023-05-15_report.pdf",
    "15_05_2023_data.csv",
    "2022_12_31_summary.docx",
    "nodate_file.txt"
]

for filename in test_filenames:
    result = extract_datetime_from_filename(filename)
    print(f"Filename: {filename}")
    print(f"Result: {result}")
    print()


def extract_datetime_from_filename(filename):
    """
    Extracts the date and time from a filename using regex patterns.
    
    Parameters:
        filename (str): The filename to extract the date and time from.
    
    Returns:
        tuple or None: A tuple containing the extracted date in 'YYYY-MM-DD' format
                        and time in 'HH:MM:SS' format, or None if not found.
    """
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})', filename)
    if match:
        date = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        time = f"{match.group(4)}:{match.group(5)}:{match.group(6)}"
        return date, time
    return None

def extract_temperature_data(file_path, target_date, target_time):
    """
    Extract temperature data from GNtemp.txt file for the closest time to the specified date and time.

    Parameters:
    file_path (str): Path to the GNtemp.txt file
    target_date (str): Target date in 'YYYY-MM-DD' format
    target_time (str): Target time in 'HH:MM:SS' format

    Returns:
    dict: Dictionary containing temperature data for different depths
    """
    df = pd.read_csv(file_path, sep='\t')
    print("Columns in the file:", df.columns.tolist())
    
    datetime_col = df.columns[0]
    df['datetime'] = pd.to_datetime(df[datetime_col], format='%d/%m/%Y %I:%M:%S %p', errors='coerce')
    
    target_datetime = f"{target_date} {target_time}"
    target_dt = datetime.strptime(target_datetime, '%Y-%m-%d %H:%M:%S')
    
    closest_time = df.iloc[(df['datetime'] - target_dt).abs().argsort()[:1]].index[0]
    
    depth_columns = ['-4', '-3.5', '-3', '-1.5', '-1', '-0.5']
    temp_data = df.loc[closest_time, depth_columns].to_dict()
    
    return temp_data

def plot_temp_depth(temp_data):
    """
    Plot the temperature vs depth data with depth from -0.5m to -4m.

    Parameters:
    temp_data (dict): Dictionary containing temperature data for different depths

    Returns:
    None (displays the plot)
    """
    sorted_data = sorted(temp_data.items(), key=lambda x: float(x[0]))
    depths = [-float(depth) for depth, _ in sorted_data]
    temperatures = [temp for _, temp in sorted_data]

    plt.figure(figsize=(10, 8))
    
    plt.plot(temperatures, depths, marker='o', linestyle='-', color='b', markersize=8)
    
    plt.title('Temperature vs Depth', fontsize=16, pad=20)
    plt.xlabel('Temperature (°C)', fontsize=12)
    plt.ylabel('Depth (m)', fontsize=12)
    
    plt.ylim(min(depths) - 0.5, max(depths) + 0.5)
    plt.yticks(depths)
    
    plt.xlim(min(temperatures) - 1, max(temperatures) + 1)
    
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    for temp, depth in zip(temperatures, depths):
        plt.annotate(f'{temp:.1f}°C', (temp, depth), xytext=(5, 5), 
                     textcoords='offset points', fontsize=9,
                     bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

    plt.tight_layout()
    
    plt.savefig('temperature_vs_depth.png', dpi=300, bbox_inches='tight')
    
    plt.show()
# Main execution
filename = '2024-07-10_12-00-00.tx0'
file_path = 'Long_local/GNtemp.txt'

datetime_result = extract_datetime_from_filename(filename)
if datetime_result is None:
    print(f"Could not extract date and time from filename: {filename}")
else:
    target_date, target_time = datetime_result
    print(f"Extracted date: {target_date}, time: {target_time}")

    try:
        temp_data = extract_temperature_data(file_path, target_date, target_time)
        print(f"Temperature data (closest to {target_date} {target_time}):")
        for depth, temp in temp_data.items():
            print(f"Depth {depth} m: {temp}°C")
        
        plot_temp_depth(temp_data)
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please check the file structure and ensure it matches the expected format.")