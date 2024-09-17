from lib.data_filter import extract_dates_from_filenames, filter_temperature_data
import re
'''

    plot the temp and depth as requested

    Parameters:
        filename and time

    Returns:
        An image of the relationship between tempearture and depth
   
'''

# Utility function 
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
