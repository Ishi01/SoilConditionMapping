import os
from converter.Tx0ToTxtPolymorph import NoXZTx0ToTxtConverter, Tx0ToTxtConverter


def test_main():
    current_folder = os.getcwd()
    input_folder = os.path.join(current_folder, 'data/tx0_files')
    output_folder = os.path.join(current_folder, 'data/txt_files')

    # 提示用户选择转换器
    print("Select Converter:")
    print("1: Offset Converter (Tx0ToTxtConverter)")
    print("2: Offset Converter without X and z axis(NoXZTx0ToTxtConverter)")

    # 从用户输入获取选择
    choice = int(input("Input number (1 or 2: "))

    # 根据选择初始化相应的转换器
    if choice == 1:
        converter = Tx0ToTxtConverter(input_folder, output_folder)
    elif choice == 2:
        converter = NoXZTx0ToTxtConverter(input_folder, output_folder)
    else:
        print("Invalid converter, only converter 1 or 2")
        return

    # 确保输出文件夹存在
    converter.ensure_output_folder_exists()

    # 遍历文件夹中的每个 tx0 文件并处理
    for filename in os.listdir(input_folder):
        if filename.endswith('.tx0'):
            converter.process_file(filename)


if __name__ == "__main__":
    test_main()
