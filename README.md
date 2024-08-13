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
   pip install imageio
   
### Step 4: Run the Python script

1.  Run main.py in the project using terminal or preset IDEs.

# Trouble Shooting

### Alternative Flow 1 Set System Environment Variables
If you're using an IDE that does not automatically integrate with Anaconda (such as PyCharm or others), you may need to manually configure your system environment variables:
1. Open the System Properties:
- Right-click on This PC or My Computer and select Properties.
- Click on Advanced system settings.
- Click on Environment Variables.
2. Modify the Path variable in the System variables section:
- Click Edit.
- Add the following paths to the list if Anaconda is installed under C:\
- C:\Users\YourUsername\Anaconda3
- C:\Users\YourUsername\Anaconda3\Scripts
- C:\Users\YourUsername\Anaconda3\condabin
- Replace **YourUsername** with your actual Windows username.
3. Click OK to close all dialogs.

### Alternative Flow 2 Configure IDE to Use Anaconda Environment
1. Open any Python file in Visual Studio Code.
2. Find Python Interpreter or press Ctrl + Shift + P to open the Command Palette If you are using VS Code.
3. Type or select Python: Select Interpreter.
4. Choose the Anaconda environment pg from the list.

# Credits
This software is built on previous work from repository [Soil-Conditions](https://github.com/wintelestr/Soil-Conditions)