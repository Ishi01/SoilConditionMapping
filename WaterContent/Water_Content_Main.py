import os
import glob
import matplotlib.pyplot as plt
import numpy as np
import pygimli as pg
import pygimli.meshtools as mt
from pygimli.physics import ert


# Ensure output folder exists
def ensure_output_folder():
    current_dir = os.path.dirname(os.getcwd())
    output_dir = os.path.join(current_dir, "Output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir


# Cleanup temporary files
def cleanup_temp_files():
    patterns = [
        "*.vector", "*.matrix", "*.bmat",
        "*.vtk", "invalid.data", "mesh.bms"
    ]
    for pattern in patterns:
        for file in glob.glob(pattern):
            try:
                os.remove(file)
                print(f"Removed: {file}")
            except Exception as e:
                print(f"Error removing {file}: {e}")


# Create mesh               
def create_mesh(start=[0, 0], end=[47, -8], quality=33.5, area=0.5):
    # Create Geometry and Mesh
    geom = mt.createWorld(start=start, end=end, worldMarker=False)
    mesh = mt.createMesh(geom, quality=quality, area=area, smooth=True)
    mesh.save("mesh.bms")
    return mesh


# Compute water content
def water_computing(start=[0, 0], end=[47, -8], quality=33.5, area=0.5,
                    lam=10, maxIter=6, dPhi=2, A=246.47, B=-0.627, processed_file_path=None):
    """ERT Inversion and Visualization process"""

    output_folder = ensure_output_folder()

    # raw_data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Raw")
    # entries_sel = [file for file in os.listdir(raw_data_folder) if file.endswith(".txt")]

    file_to_process = processed_file_path

    entries_sel = [file_to_process]

    mesh = create_mesh(start=start, end=end, quality=quality, area=area)
    centers = mesh.cellCenters()
    x_coordinates = centers[:, 0]
    y_coordinates = centers[:, 1]
    storage = np.zeros([np.shape(mesh.cellMarkers())[0], len(entries_sel)])

    for i, date in enumerate(entries_sel):
        mgr = ert.ERTManager(file_to_process, verbose=True, debug=True)
        mgr.data.remove(mgr.data["rhoa"] < 0)  # Filter negative values
        mgr.data["err"] = ert.estimateError(mgr.data, absoluteError=0.001, relativeError=0.03)
        mgr.data["k"] = ert.createGeometricFactors(mgr.data, numerical=True)

        inv = mgr.invert(mesh=mesh, lam=lam, maxIter=maxIter, dPhi=dPhi, CHI1OPT=5, Verbose=True)
        storage[:, i] = inv

        mgr.saveResult(os.path.join(output_folder, f"{date[:-4]}_result.dat"))

        fSWC = lambda x: A * x ** B
        temperature_points = [(0, -5), (-10, -5)]
        t = 25.5

        temperature_points.sort(key=lambda x: x[0])
        for j in range(len(y_coordinates) - 1):
            y = y_coordinates[j]
            for i in range(len(temperature_points) - 1):
                y1, t1 = temperature_points[i]
                y2, t2 = temperature_points[i + 1]
                if y1 <= y <= y2:
                    t = t1 + (t2 - t1) * ((y - y1) / (y2 - y1))
                    break
                else:
                    t = t1 if y < y1 else t2
            storage[j, :] = (1 + 0.025 * (t - 25)) * storage[j, :]

        SWC = fSWC(storage)
        fig1, (ax1) = plt.subplots(1, figsize=(15.5, 7))

        pg.viewer.show(
            mesh=mesh, data=SWC[:, 0], hold=True, label="Soil water content",
            ax=ax1, cMin=0, cMax=30, cMap="Spectral", showMesh=True,
        )

        ax1.set_xlim(-0, mgr.paraDomain.xmax())
        ax1.set_ylim(-8, mgr.paraDomain.ymax())
        ax1.set_title(date)

        fig_filename = os.path.join(
            output_folder, f"Water_result_{os.path.basename(os.path.splitext(date)[0])}.png"
        )

        plt.savefig(fig_filename, dpi=300, bbox_inches="tight")
        print(f"Figure saved as: {fig_filename}")

        plt.close()
        plt.close("all")

        cleanup_temp_files()

    return fig_filename

# if __name__ == "__main__":
#     water_computing()

