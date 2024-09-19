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