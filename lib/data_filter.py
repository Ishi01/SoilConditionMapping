import os
import re
import pandas as pd


def extract_dates_from_filenames(data_dir):
    """
    Extracts dates from filenames in a directory, handling different formats.

    Parameters:
        data_dir (str): The directory containing the data files.

    Returns:
        list: A list of dates in 'YYYY-MM-DD' format.
    """
    dates = []
    for filename in os.listdir(data_dir):
        if filename.endswith('.txt') or filename.endswith('.tx0'):
            date_part = extract_date_from_filename(filename)
            if date_part:
                dates.append(date_part)
    return dates


def extract_date_from_filename(filename):
    """
    Extracts the date from a filename using regex patterns.

    Parameters:
        filename (str): The filename to extract the date from.

    Returns:
        str or None: The extracted date in 'YYYY-MM-DD' format or None if no date is found.
    """
    # Try matching the 'YYYY-MM-DD' format first
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
    if match:
        return match.group(0)

    # Try matching the 'DD_MM_YYYY' format
    match = re.search(r'(\d{2})_(\d{2})_(\d{4})', filename)
    if match:
        # Convert 'DD_MM_YYYY' to 'YYYY-MM-DD'
        day, month, year = match.groups()
        return f"{year}-{month}-{day}"

    # Try matching the 'YYYY_MM_DD' format
    match = re.search(r'(\d{4})_(\d{2})_(\d{2})', filename)
    if match:
        # Convert 'YYYY_MM_DD' to 'YYYY-MM-DD'
        year, month, day = match.groups()
        return f"{year}-{month}-{day}"

    return None


def filter_temperature_data(temperature_file, dates, output_file):
    """
    Filters temperature data based on matching dates and saves the filtered data.

    Parameters:
        temperature_file (str): The file path of the temperature data.
        dates (list): A list of dates to filter by.
        output_file (str): The file path to save the filtered data.
    """
    # Load the original temperature data
    temp_df = pd.read_csv(temperature_file, on_bad_lines='skip', delimiter="\t", header=0, parse_dates=[0], dayfirst=True)

    # Convert dates to pandas datetime for matching
    temp_df['date'] = temp_df['time'].dt.strftime('%Y-%m-%d')

    # Filter rows where the date is in the list of dates from the txt files
    filtered_df = temp_df[temp_df['date'].isin(dates)]

    # Save the filtered temperature data
    filtered_df.to_csv(output_file, sep="\t", index=False)


