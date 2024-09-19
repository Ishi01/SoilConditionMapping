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