"""
Created on  August 15,  2024,
Refactored on August 26, 2024,

@author: 23829101 Long Qin
@Refactored by: 23750564 Peter Wang
Refactor notes: Added polymorphism to lower the repeat code use, Integrate 3 files into 1
"""

import os


class Tx0ToTxtConverter:
    def __init__(self, input_folder, output_folder):
        self.input_folder = input_folder
        self.output_folder = output_folder

    def ensure_output_folder_exists(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def read_input_file(self, filename):
        input_file_path = os.path.join(self.input_folder, filename)
        with open(input_file_path, 'r', encoding='utf-8') as input_file:
            return input_file.readlines()

    def process_electrode_data(self, lines):
        electrode_data = []
        electrode_start = False
        for line in lines:
            if '* Electrode positions' in line:
                electrode_start = True
                continue
            if '* Remote electrode positions' in line:
                break
            if electrode_start and '* Electrode [' in line:
                parts = line.split('=')[1].strip().split()
                if len(parts) >= 3:
                    x = parts[0].strip()
                    z = parts[2].strip()
                    electrode_data.append(f"{x}     {z}")
        return electrode_data

    def process_measurement_data(self, lines):
        measurement_data = []
        measurement_start = False
        for line in lines:
            if '* Data' in line and '*******************' in line:
                measurement_start = True
                continue
            if measurement_start and line.strip() and not line.startswith('*'):
                parts = line.split()
                if len(parts) < 22:
                    continue
                a, b, m, n = parts[1], parts[2], parts[3], parts[4]
                rho = parts[10]
                x = parts[18]
                z = parts[20]
                measurement_data.append(f"{a} {b} {m} {n} {rho} {x} {z}")
        return measurement_data

    def write_output_file(self, output_file_path, electrode_data, measurement_data):
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(f"{len(electrode_data)}# Number of electrodes\n")
            output_file.write("# x z\n")
            for line in electrode_data:
                output_file.write(line + "\n")

            output_file.write(f"{len(measurement_data)}# Number of data\n")
            output_file.write("# a b m n rhoa x z\n")
            for line in measurement_data:
                output_file.write(f"{line}\n")

    def process_file(self, filename):
        lines = self.read_input_file(filename)
        electrode_data = self.process_electrode_data(lines)
        measurement_data = self.process_measurement_data(lines)
        output_file_name = filename.replace('.tx0', '.txt')
        output_file_path = os.path.join(self.output_folder, output_file_name)
        self.write_output_file(output_file_path, electrode_data, measurement_data)
        print(f"Data extraction and conversion completed for {filename}.")


class OffsetCorrectorTx0ToTxtConverter(Tx0ToTxtConverter):
    def process_measurement_data(self, lines):
        measurement_data = super().process_measurement_data(lines)
        if measurement_data:
            first_a = int(measurement_data[0].split()[0])
            if first_a != 1:
                offset = first_a - 1
                corrected_data = []
                for line in measurement_data:
                    parts = line.split()
                    a, b, m, n = int(parts[0]) - offset, int(parts[1]) - offset, int(parts[2]) - offset, int(
                        parts[3]) - offset
                    new_line = f"{a} {b} {m} {n} {parts[4]} {parts[5]} {parts[6]}"
                    corrected_data.append(new_line)
                measurement_data = corrected_data
        return measurement_data


class NoXZTx0ToTxtConverter(Tx0ToTxtConverter):
    def process_measurement_data(self, lines):
        measurement_data = []
        measurement_start = False
        for line in lines:
            if '* Data' in line and '*******************' in line:
                measurement_start = True
                continue
            if measurement_start and line.strip() and not line.startswith('*'):
                parts = line.split()
                if len(parts) < 22:
                    continue
                a, b, m, n = parts[1], parts[2], parts[3], parts[4]
                rho = parts[10]
                measurement_data.append(f"{a} {b} {m} {n} {rho}")
        return measurement_data


def main():
    current_folder = os.getcwd()
    input_folder = current_folder
    output_folder = os.path.join(current_folder, 'output')

    # You can use any of the following converters
    converters = [
        Tx0ToTxtConverter(input_folder, output_folder),
        OffsetCorrectorTx0ToTxtConverter(input_folder, output_folder),
        NoXZTx0ToTxtConverter(input_folder, output_folder)
    ]

    for converter in converters:
        converter.ensure_output_folder_exists()
        for filename in os.listdir(input_folder):
            if filename.endswith('.tx0'):
                converter.process_file(filename)


if __name__ == "__main__":
    main()
