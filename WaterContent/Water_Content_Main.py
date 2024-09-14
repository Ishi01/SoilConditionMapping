import os
import glob
import matplotlib.pyplot as plt
import numpy as np
import pygimli as pg
import pygimli.meshtools as mt
from pygimli.physics import ert

# Ensure output folder exists
def ensure_output_folder():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, "Output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

# Cleanup temporary files
def cleanup_temp_files():
    patterns = [
        "*.vector", "*.matrix", "*.bmat",
        "fop-model1.vtk", "invalid.data", "mesh.bms"
    ]
    for pattern in patterns:
        for file in glob.glob(pattern):
            try:
                os.remove(file)
                print(f"Removed: {file}")
            except Exception as e:
                print(f"Error removing {file}: {e}")

# Compute water content
def watercomputing(start=[0, 0], end=[47, -8], quality=33.5, area=0.5,
                   lam=10, maxIter=6, dPhi=2, A=246.47, B=-0.627):
    """ERT Inversion and Visualization process"""
    
    output_folder = ensure_output_folder()

    raw_data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Raw")
    entries_sel = [file for file in os.listdir(raw_data_folder) if file.endswith(".txt")]

    geom = mt.createWorld(start, end, worldMarker=False)
    mesh = mt.createMesh(geom, quality, area, smooth=True)
    mesh.save("mesh.bms")

    centers = mesh.cellCenters()
    x_coordinates = centers[:, 0]
    y_coordinates = centers[:, 1]
    Storage = np.zeros([np.shape(mesh.cellMarkers())[0], len(entries_sel)])

    for i, date in enumerate(entries_sel):
        mgr = ert.ERTManager(os.path.join(raw_data_folder, date), verbose=True, debug=True)
        mgr.data.remove(mgr.data["rhoa"] < 0)  # Filter negative values
        mgr.data["err"] = ert.estimateError(mgr.data, absoluteError=0.001, relativeError=0.03)
        mgr.data["k"] = ert.createGeometricFactors(mgr.data, numerical=True)
        
        inv = mgr.invert(mesh=mesh, lam=lam, maxIter=maxIter, dPhi=dPhi, CHI1OPT=5, Verbose=True)
        Storage[:, i] = inv

        mgr.saveResult(os.path.join(output_folder, f"{date[:-4]}_result.dat"))

        fSWC = lambda x: A * x**B
        temperature_points = [(0, -5), (-10, -5)]
        T = 25.5
        
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
            Storage[j, :] = (1 + 0.025 * (T - 25)) * Storage[j, :]

        SWC = fSWC(Storage)
        fig1, (ax1) = plt.subplots(1, figsize=(15.5, 7))

        pg.viewer.show(
            mesh=mesh, data=SWC[:, 0], hold=True, label="Soil water content",
            ax=ax1, cMin=0, cMax=30, cMap="Spectral", showMesh=True,
        )

        ax1.set_xlim(-0, mgr.paraDomain.xmax())
        ax1.set_ylim(-8, mgr.paraDomain.ymax())
        ax1.set_title(date)
        plt.savefig(os.path.join(output_folder, "result_water_content.jpg"))
        plt.close()

if __name__ == "__main__":
    watercomputing()
    cleanup_temp_files()