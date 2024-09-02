# Data Processing Workflow for tx0_to_txt_temp Pipeline

# 1. Run ```tx0_to_txt_offset.py```

   - **Input**: `tx0_files` folder
   - **Output**: `output_txt_offset` folder

```python
python tx0_to_txt_offset.py tx0_files/ output_txt_offset/

```

# 2. Run ```Newtem.py```


   - **Input**: `output_txt_offset` folder and `GNtemp.txt` file
   - **Output**: `Newtem.txt` 

```python
python Newtem.py output_txt_offset/ GNtemp.txt

```


# 3. Run ```txt_temp.py```

   - **Input**: `output_txt_offset` folder and `Newtem.txt` file
   - **Output**: `tx0_to_txt_temp` folder

```python
python txt_temp.py Newtem.txt output_txt_offset/ 
```

# 4. Run ```auto_tx0_txt_temp.py``` to automate the above process.

   - **Input**: `tx0_files` folder and  `GNtemp.txt` file
   - **Output**: `tx0_to_txt_temp` folder

```python
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
