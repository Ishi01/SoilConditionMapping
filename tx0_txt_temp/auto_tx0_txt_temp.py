import subprocess
import os

# 定义各个步骤的文件路径
script1 = 'tx0_to_txt_offset.py'
script2 = 'Newtem.py'
script3 = 'txt_temp.py'

# 设置输入输出目录
tx0_files_dir = 'tx0_files'
output_txt_offset_dir = 'output_txt_offset'
newtem_output_file = 'Newtem.txt'

# 执行第一个脚本 tx0_to_txt_offset.py
print("Step 1: Running tx0_to_txt_offset.py")
subprocess.run(['python', script1])

# 检查第一个步骤的输出是否存在
if not os.path.exists(output_txt_offset_dir):
    print(f"Error: Output directory {output_txt_offset_dir} not found. Exiting.")
    exit(1)

# 执行第二个脚本 Newtem.py
print("Step 2: Running Newtem.py")
subprocess.run(['python', script2])

# 检查第二个步骤的输出是否存在
if not os.path.exists(newtem_output_file):
    print(f"Error: Output file {newtem_output_file} not found. Exiting.")
    exit(1)

# 执行第三个脚本 txt_temp.py
print("Step 3: Running txt_temp.py")
subprocess.run(['python', script3])

print("All steps completed successfully.")
