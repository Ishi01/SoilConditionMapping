import re
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

def extract_datetime_from_filename(filename):
    """
    Extracts the date and time from a filename using various regex patterns.
    
    Parameters:
    filename (str): The filename to extract the date and time from.
    
    Returns:
    tuple or None: A tuple containing the extracted date in 'YYYY-MM-DD' format 
                   and time in 'HH:MM:SS' format, or None if not found.
    
    Supported formats:
    - 'YYYY-MM-DD_HH-MM-SS'
    - 'YYYY-MM-DD'
    - 'DD_MM_YYYY'
    - 'YYYY_MM_DD'
    """
    patterns = [
        r'(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})',
        r'(\d{4})-(\d{2})-(\d{2})',
        r'(\d{2})_(\d{2})_(\d{4})',
        r'(\d{4})_(\d{2})_(\d{2})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            groups = match.groups()
            if len(groups) == 6:
                return f"{groups[0]}-{groups[1]}-{groups[2]}", f"{groups[3]}:{groups[4]}:{groups[5]}"
            elif len(groups) == 3:
                if pattern == r'(\d{2})_(\d{2})_(\d{4})':
                    return f"{groups[2]}-{groups[1]}-{groups[0]}", None
                else:
                    return f"{groups[0]}-{groups[1]}-{groups[2]}", None
    
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



def create_temp_vs_depth_plot(temp_data):
    """
    Create a temperature vs depth plot based on the provided temperature data.

    Parameters:
    temp_data (dict): Dictionary containing temperature data for different depths

    Returns:
    str: Base64 encoded string of the plot image
    """
    depths = [float(depth) for depth in temp_data.keys()]
    temperatures = list(temp_data.values())
    
    depths, temperatures = zip(*sorted(zip(depths, temperatures)))
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_facecolor('#F5F5F5')
    fig.patch.set_facecolor('#FFFFFF')
    
    line_color = '#007ACC'
    ax.plot(temperatures, depths, marker='o', color=line_color, linewidth=2, markersize=8)
    
    ax.set_title('Temperature vs Depth', fontsize=20, fontweight='bold', pad=20)
    ax.set_xlabel('Temperature (°C)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Depth (m)', fontsize=14, fontweight='bold')
    
    ax.grid(True, linestyle='--', alpha=0.7, color='#CCCCCC')
    
    y_min = min(depths) - 0.5
    ax.set_ylim(y_min, 0)
    
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    ax.tick_params(axis='both', which='major', labelsize=12)
    
    for temp, depth in zip(temperatures, depths):
        ax.annotate(f'{temp}°C', (temp, depth), 
                    textcoords="offset points",
                    xytext=(10, 0), 
                    ha='left', va='center',
                    fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
    
    top_temp = temp_data[max(temp_data.keys())]
    bottom_temp = temp_data[min(temp_data.keys())]
    ax.plot([top_temp, top_temp], [float(max(temp_data.keys())), float(max(temp_data.keys())) - 0.5], color=line_color, linewidth=2)
    ax.plot([bottom_temp, bottom_temp], [float(min(temp_data.keys())), float(min(temp_data.keys())) + 0.5], color=line_color, linewidth=2)
    
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)
    return image_base64


def display_temp_vs_depth(txo_file, GNtemp_file):
    """
    Analyze temperature data from txo and GNtemp files and return a plot.
    
    Parameters:
    txo_file (str): Path to the .tx0 file
    GNtemp_file (str): Path to the GNtemp.txt file
    
    Returns:
    str or None: Base64 encoded string of the temperature vs depth plot, or None if an error occurred
    
    Usage:
    plot_image = display_temp_vs_depth('2021-11-12_03-30-00.tx0', 'Long_local/GNtemp.txt')
    if plot_image:
        # Use plot_image (base64 string) to display the image
        print("Plot generated successfully")
    else:
        print("Failed to generate plot")
    """
    try:
        datetime_result = extract_datetime_from_filename(txo_file)
        if datetime_result is None:
            print("Error: Failed to extract date and time from filename")
            return None
        
        target_date, target_time = datetime_result
        if target_time is None:
            target_time = "00:00:00"  # Default time if not provided
        
        temp_data = extract_temperature_data(GNtemp_file, target_date, target_time)
        
        if not temp_data:
            print("Error: Failed to extract temperature data")
            return None
        
        plot_image = create_temp_vs_depth_plot(temp_data)
        
        return plot_image
    except Exception as e:
        print(f"Error: {str(e)}")
        return None