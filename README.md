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


ρ_corrected = ρ_measured * [1 + α(T - T_ref)]

当然,我可以为您提供这个校正公式的数学表达式。这个公式是用于根据温度校正电阻率的。让我们将其表示为数学公式:
ρ_corrected = ρ_measured * [1 + α(T - T_ref)]
其中:
ρ_corrected 是校正后的电阻率
ρ_measured 是测量的电阻率
α 是温度系数 (在这个公式中是 0.025 /°C)
T 是实际温度
T_ref 是参考温度 (在这个公式中是 25°C)
在代码中使用的具体公式是:
ρ_corrected = ρ_measured * [1 + 0.025(T - 25)]
This formula can be expressed mathematically as:
ρ_corrected = ρ_measured * [1 + α(T - T_ref)]
Where:
ρ_corrected is the corrected resistivity
ρ_measured is the measured resistivity
α is the temperature coefficient (0.025 /°C in this formula)
T is the actual temperature
T_ref is the reference temperature (25°C in this formula)
The specific formula used in the code is:
ρ_corrected = ρ_measured * [1 + 0.025(T - 25)]
这个公式考虑了温度对电阻率的影响,允许将测量的电阻率校正到标准温度(这里是25°C)。温度系数0.025 /°C 表示每偏离参考温度1°C,电阻率变化2.5%。
This formula accounts for the effect of temperature on resistivity, allowing the measured resistivity to be corrected to a standard temperature (25°C in this case). The temperature coefficient of 0.025 /°C indicates that for every 1°C deviation from the reference temperature, the resistivity changes by 2.5%.
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
