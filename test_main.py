import os
from converter.Tx0ToTxtPolymorph import OffsetCorrectorTx0ToTxtConverter, NoXZTx0ToTxtConverter, Tx0ToTxtConverter


def test_main():
    current_folder = os.getcwd()
    input_folder = current_folder
    output_folder = os.path.join(current_folder, 'output')

    # delete comment to change converter
    #converter_basic = Tx0ToTxtConverter(input_folder, output_folder)
    #converter_offset = OffsetCorrectorTx0ToTxtConverter(input_folder, output_folder)
    converter_NoXZ = NoXZTx0ToTxtConverter(input_folder, output_folder)


    # lopping through file
    for filename in os.listdir(input_folder):
        if filename.endswith('.tx0'):
            #converter_basic.process_file(filename)
            #converter_offset.process_file(filename)
            converter_NoXZ.process_file(filename)

if __name__ == "__main__":
    test_main()
