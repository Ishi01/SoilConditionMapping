# Data Processing Workflow for tx0_to_txt_temp Pipeline

# 1. Run ```tx0_to_txt_offset.py```

   - **Input**: `tx0_files` folder
   - **Output**: `output_txt_offset` folder

```bash
python tx0_to_txt_offset.py tx0_files/ output_txt_offset/

```

# 2. Run ```Newtem.py```


   - **Input**: `output_txt_offset` folder and `GNtemp.txt` file
   - **Output**: `Newtem.txt` 

```bash
python Newtem.py output_txt_offset/ GNtemp.txt

```


# 3. Run ```txt_temp.py```

   - **Input**: `output_txt_offset` folder and `Newtem.txt` file
   - **Output**: `tx0_to_txt_temp` folder

```bash
python txt_temp.py Newtem.txt output_txt_offset/ 
```

# 4. Run ```auto_tx0_txt_temp.py``` to automate the above process.

   - **Input**: `tx0_files` folder and  `GNtemp.txt` file
   - **Output**: `tx0_to_txt_temp` folder

```bash
python auto_tx0_txt_temp.py
```
## Temperature Correction Formula for Resistivity

### Math formula 
This formula can be expressed mathematically as:
ρ_corrected = ρ_measured * [1 + α(T - T_ref)]
Where:
ρ_corrected is the **corrected resistivity**
ρ_measured is the **measured resistivity**
α is the temperature **coefficient** (0.025 /°C in this formula)
T is the **actual** temperature
T_ref is the `reference` temperature (25°C in this formula)
The specific `formula` used in the code is:
ρ_corrected = ρ_measured * [1 + 0.025(T - 25)]

This formula accounts for the **effect of temperature on resistivity**, allowing the measured resistivity to be corrected to a **standard temperature** of 25°C. The temperature coefficient of 0.025 /°C means that for every **1°C deviation** from the reference temperature, the resistivity changes by **2.5%**.

# Temperature Extraction and Visualization Tool

This Python tool processes temperature data from `.tx0` files based on specific date and time extracted from the filename. It then visualizes the temperature at various depths using a customized plot.

## Table of Contents

1. [Description](#description)
2. [Installation](#installation)


## Description

This tool extracts temperature data from a `.txt` file (`GNtemp.txt`) for a specific date and time based on filenames that include date and time in various formats. It allows users to visualize the temperature variation with depth using a well-formatted plot.

### Input:
- Filenames containing date and time (formats: `YYYY-MM-DD_HH-MM-SS`, `YYYY-MM-DD`, `DD_MM_YYYY`, or `YYYY_MM_DD`).
- Temperature data stored in a `.txt` file (`GNtemp.txt`), where each row represents temperature readings at different depths and times.

### Output:
- A plot showing the relationship between temperature and depth for a given date and time.

## Installation

Make sure you have Python and the necessary libraries installed:

```bash
pip install pandas matplotlib
```


# Soil Condition Inversion Mapping 

## Overview 

This project is part of the **CITS5206** course and focuses on soil condition mapping using inversion techniques. The project utilizes the **PyGIMLi** library for geophysical inversion and **PyQt5** for the user interface. Please note that this project is designed to run exclusively on **Windows**.

## Prerequisites <!-- This is a subheading -->

- **Operating System**: Windows 
- **Python Distribution**: Anaconda3
- **Libraries**: 
  - PyGIMLi 
  - PyQt5
  - Imageio
  - Pip
  - Matplotlib
  - Numpy

## Installation Instructions 

Follow the steps below to set up your environment and get started with the project.

### Step 1: Install Anaconda and Python3

1. Download and install [Anaconda3](https://www.anaconda.com/products/distribution#download-section). <!-- This is a numbered list -->
2. Ensure Python 3 is installed with Anaconda.

### Step 2: Create a Virtual Environment

1. Open the **Anaconda Prompt**.
2. Create a new virtual environment named `pg` with the required libraries by executing the following command:

   ```bash
   conda create -n pg -c gimli -c conda-forge pygimli=1.4.3
3. Activate virtual environment using code below after successfully installed the virtual environment.
   
    ```bash
   conda activate pg

### Step 3: Install libraries

1. Install Imageio
    ```bash
   pip install pandas
   
### Step 4: Run the Python script

1.  Run main.py in the project using terminal or preset IDEs.

# Trouble Shooting

### Alternative Flow 1 Set System Environment Variables (If using Windows)
If you're using an IDE that does not automatically integrate with Anaconda (such as PyCharm or others), you may need to manually configure your system environment variables:
1. Open the System Properties:
- Right-click on This PC or My Computer and select Properties.
- Click on Advanced system settings.
- Click on Environment Variables.
2. Modify the Path variable in the System variables section:
- Click Edit.
- Add the following paths to the list if Anaconda is installed under C:\
- {Your install location}\Anaconda3
- {Your install location}\Anaconda3\Scripts
- {Your install location}\Anaconda3\condabin
- Replace **Your install location**.
3. Click OK to close all dialogs.

### Alternative Flow 2 Configure IDE to Use Anaconda Environment
1. Open any Python file in Visual Studio Code.
2. Find Python Interpreter or press Ctrl + Shift + P to open the Command Palette If you are using VS Code.
3. Type or select Python: Select Interpreter.
4. Choose the Anaconda environment pg from the list.

# Credits
This software is built on previous work from repository [Soil-Conditions](https://github.com/wintelestr/Soil-Conditions)
