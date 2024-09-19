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
