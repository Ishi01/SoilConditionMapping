# from lib.data_filter import extract_dates_from_filenames, filter_temperature_data
import re
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
import numpy as np


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
    # Extract depths and temperatures
    depths = [float(depth) for depth in temp_data.keys()]
    temperatures = list(temp_data.values())
    
    # Sort the data by depth (from shallowest to deepest)
    depths, temperatures = zip(*sorted(zip(depths, temperatures)))
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(temperatures, depths, marker='o')
    
    # Customize the plot
    ax.set_title('Temperature vs Depth', fontsize=16)
    ax.set_xlabel('Temperature (°C)', fontsize=12)
    ax.set_ylabel('Depth (m)', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Set y-axis to increase downwards and start from 0
    ax.set_ylim(min(depths) - 0.5, 0)  # Add some padding at the bottom
    
    # Move y-axis to the right side
    # ax.yaxis.tick_right()
    # ax.yaxis.set_label_position("right")
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    # Add temperature labels to each point
    for temp, depth in zip(temperatures, depths):
        ax.annotate(f'{temp}°C', (temp, depth), textcoords="offset points", 
                    xytext=(-10,0), ha='right', va='center', fontsize=9)
    
    # Show the plot
    plt.tight_layout()
    plt.show()

# Main execution
filename = '2024-07-10_12-00-00.tx0'
file_path = 'Long_local/GNtemp.txt'

datetime_result = extract_datetime_from_filename(filename)
target_date, target_time = datetime_result
temp_data = extract_temperature_data(file_path, target_date, target_time)
plot_temp_depth(temp_data)

'''
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
        print(temp_data)

        plot_temp_depth(temp_data)
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please check the file structure and ensure it matches the expected format.")
'''