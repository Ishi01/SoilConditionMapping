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
        """This method is shared and parses common data fields."""
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
                a, b, m, n = int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])
                rho = parts[10]
                measurement_data.append(self.format_measurement_data(a, b, m, n, rho, parts))
        return measurement_data

    def correct_offsets(self, measurement_data):
        """Corrects the offset of electrode indices to start from 1 based on actual data."""
        corrected_data = []  # Initialize the corrected_data list

        if measurement_data:
            first_a = min(data[0] for data in measurement_data)
            offset = first_a - 1  # Calculate offset to normalize to 1

            for data in measurement_data:
                a, b, m, n = data[:4]
                corrected_data.append(
                    self.format_corrected_data(a - offset, b - offset, m - offset, n - offset, data[4:]))

        return corrected_data  # Return the initialized list

    def format_measurement_data(self, a, b, m, n, rho, parts):
        """Formats the measurement data for writing, including x and z coordinates."""
        x = parts[18]
        z = parts[20]
        return a, b, m, n, rho, x, z

    def format_corrected_data(self, a_new, b_new, m_new, n_new, rest_data):
        """Formats corrected data for output including x and z coordinates."""
        rho, x, z = rest_data
        return f"{a_new} {b_new} {m_new} {n_new} {rho} {x} {z}"

    def write_output_file(self, output_file_path, electrode_data, measurement_data):
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(f"{len(electrode_data)}# Number of electrodes\n")
            output_file.write("# x z\n")
            for line in electrode_data:
                output_file.write(line + "\n")

            output_file.write(f"{len(measurement_data)}# Number of data\n")
            output_file.write("# a b m n rhoa x z\n")
            for line in measurement_data:
                output_file.write(line + "\n")

    def process_file(self, filename):
        lines = self.read_input_file(filename)
        electrode_data = self.process_electrode_data(lines)
        measurement_data = self.process_measurement_data(lines)
        measurement_data = self.correct_offsets(measurement_data)  # Correct offsets to start from 1
        output_file_name = filename.replace('.tx0', '.txt')
        output_file_path = os.path.join(self.output_folder, output_file_name)
        self.write_output_file(output_file_path, electrode_data, measurement_data)
        print(f"Data extraction and conversion completed for {filename}.")


class NoXZTx0ToTxtConverter(Tx0ToTxtConverter):
    def format_measurement_data(self, a, b, m, n, rho, parts):
        """Formats the measurement data without x and z coordinates."""
        return a, b, m, n, rho

    def format_corrected_data(self, a_new, b_new, m_new, n_new, rest_data):
        """Formats corrected data for output without x and z coordinates."""
        rho = rest_data[0]
        return f"{a_new} {b_new} {m_new} {n_new} {rho}"

    def write_output_file(self, output_file_path, electrode_data, measurement_data):
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(f"{len(electrode_data)}# Number of electrodes\n")
            output_file.write("# x z\n")
            for line in electrode_data:
                output_file.write(line + "\n")

            output_file.write(f"{len(measurement_data)}# Number of data\n")
            output_file.write("# a b m n rhoa\n")
            for line in measurement_data:
                output_file.write(line + "\n")

