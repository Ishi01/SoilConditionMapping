import os
import shutil
import numpy as np
import pygimli as pg
import pygimli.meshtools as mt
from pygimli.physics import ert


class DataModel:
    def __init__(self):
        self.save_directory = None
        self.tem_field = [(0, 25)]
        self.tem = 25

    def set_save_directory(self, directory):
        self.save_directory = directory

    def get_save_directory(self):
        return self.save_directory

    def set_temperature(self, temperature):
        self.tem = temperature
        self.tem_field = [(0, self.tem)]

    def get_temperature_field(self):
        return self.tem_field

    def import_files(self, files):
        if not self.save_directory or not files:
            return []

        os.makedirs(self.save_directory, exist_ok=True)
        copied_files = []
        for file in files:
            destination_file = os.path.join(self.save_directory, os.path.basename(file))
            shutil.copy(file, destination_file)
            copied_files.append(destination_file)

        return copied_files

    def transfer_data(self, input_file_path):
        output_file_name = os.path.basename(input_file_path).replace('.tx0', '.txt')
        output_file_path = os.path.join(self.save_directory, output_file_name)

        fixed_data = ["48# Number of electrodes", "# x z"] + [f"{i}     0" for i in range(48)] + ["909# Number of data"]

        data = []
        with open(input_file_path, 'r') as input_file:
            lines = input_file.readlines()
            data = [line.strip().split() for line in lines[243:]]

        selected_data = []
        for row in data:
            row_transformed = row.copy()
            for i in [1, 2, 3, 4]:  # index of columns to transform
                item = float(row[i])
                if item >= 48:
                    row_transformed[i] = str(int(item - 48))  # Subtract 48 and convert to string
                else:
                    row_transformed[i] = str(int(item))  # Convert to string without subtracting 48
            selected_data.append([row_transformed[i] for i in [1, 2, 3, 4, 10]])  # Select the specific columns

        with open(output_file_path, 'w') as output_file:
            for line in fixed_data:
                output_file.write(line + "\n")
            output_file.write("# a b m n rhoa\n")
            for row in selected_data:
                output_file.write("\t".join(row) + "\n")

        return output_file_path

    def create_domain(self, start_x, start_y, end_x, end_y):
        return pg.meshtools.createWorld(start=[start_x, end_y], end=[end_x, start_y], worldMarker=False)

    def create_mesh(self, geom, quality, area):
        return mt.createMesh(geom, quality, area, smooth=True)

    def start_inversion(self, file_to_convert, mesh, lam, maxIter, dPhi):
        mgr = ert.ERTManager(file_to_convert, verbose=True, debug=True)
        rhoa = np.array(mgr.data['rhoa'])
        Argw = np.argwhere(rhoa <= 0)

        mgr.data.remove(mgr.data["rhoa"] < 0)
        mgr.data['err'] = ert.estimateError(mgr.data, absoluteError=0.001, relativeError=0.03)
        mgr.data['k'] = ert.createGeometricFactors(mgr.data, numerical=True)

        inv = mgr.invert(mesh=mesh, lam=lam, maxIter=maxIter, dPhi=dPhi, CHI1OPT=5, Verbose=True)

        Storage = np.zeros([np.shape(mesh.cellMarkers())[0], 1])
        Storage[:, 0] = inv

        return inv, Storage

    def calculate_water_content(self, mesh, storage, temperature_points):
        centers = mesh.cellCenters()
        y_coordinates = centers[:, 1]
        fSWC = lambda x: 246.47 * x ** (-0.627)

        temperature_points.sort(key=lambda x: x[0])
        for j in range(len(y_coordinates) - 1):
            y = y_coordinates[j]
            for i in range(len(temperature_points) - 1):
                y1, T1 = temperature_points[i]
                y2, T2 = temperature_points[i + 1]
                if y1 <= y <= y2:
                    T = T1 + (T2 - T1) * ((y - y1) / (y2 - y1))
                    break
                else:
                    T = T1 if y < y1 else T2
            storage[j, :] = (1 + 0.025 * (T - 25)) * storage[j, :]

        SWC = fSWC(storage)

        return SWC
