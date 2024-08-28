import os
import Tx0ToTxtConverter

def test_main():
    current_folder = os.getcwd()
    input_folder = current_folder
    output_folder = os.path.join(current_folder, 'output')

    # Create instance for 3 types of converter
    # converter = Tx0ToTxtConverter(input_folder, output_folder)  # basic converter
    # converter = OffsetCorrectorTx0ToTxtConverter(input_folder, output_folder)  # offset corrected converter
    # converter = NoXZTx0ToTxtConverter(input_folder, output_folder)  # coverter without X and Z

    # delete comment to change converter
    converter = Tx0ToTxtConverter(input_folder, output_folder)
    # converter = OffsetCorrectorTx0ToTxtConverter(input_folder, output_folder)
    # converter = NoXZTx0ToTxtConverter(input_folder, output_folder)

    # make sure to have a output folder
    converter.ensure_output_folder_exists()

    # lopping through file
    for filename in os.listdir(input_folder):
        if filename.endswith('.tx0'):
            converter.process_file(filename)

if __name__ == "__main__":
    test_main()
