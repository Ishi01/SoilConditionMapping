import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog

def extract_dates_from_filenames(data_dir):
    dates = []
    for filename in os.listdir(data_dir):
        if filename.endswith('.txt'):
            date_part = filename.split('_')[0]  # Assumes filenames are in the format 'YYYY-MM-DD_otherinfo.txt'
            dates.append(date_part)
    return dates

def filter_temperature_data(temperature_file, dates, output_file):
    # Load the original temperature data
    temp_df = pd.read_csv(temperature_file, sep="\t", header=0, parse_dates=[0], dayfirst=True)
    
    # Convert dates to pandas datetime for matching
    temp_df['date'] = temp_df['time'].dt.strftime('%Y-%m-%d')

    # Filter rows where the date is in the list of dates from the txt files
    filtered_df = temp_df[temp_df['date'].isin(dates)]
    
    # Save the filtered temperature data
    filtered_df.to_csv(output_file, sep="\t", index=False)



def main():
    # Directory containing the txt files
    data_dir = "output_txt_offset"

    #Select the temperature

    # Path to the original temperature file
    current_folder = os.getcwd()
    #temperature_file = "GNtemp.txt"
    temp_msg = "Please select the temperature file"
    temperature_file = filedialog.askopenfilename(initialdir=current_folder, title=temp_msg)
    
    # Path to save the filtered temperature data
    output_file = "GeneratedTemp.txt"

    # Extract dates from filenames
    dates = extract_dates_from_filenames(data_dir)

    # Filter temperature data and save it to a new file
    filter_temperature_data(temperature_file, dates, output_file)

