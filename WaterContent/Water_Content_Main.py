import os
import matplotlib.pyplot as plt
import numpy as np
import pygimli as pg
import pygimli.meshtools as mt
from pygimli.physics import ert

def ensure_output_folder():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, "Output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir


def cleanup_temp_files():
    patterns = [
        "*.vector",
        "*.matrix",
        "*.bmat",
        "fop-model1.vtk",
        "invalid.data",
        "mesh.bms",
    ]
    for pattern in patterns:
        for file in glob.glob(pattern):
            try:
                os.remove(file)
                print(f"Removed: {file}")
            except Exception as e:
                print(f"Error removing {file}: {e}")

"""
This function will compute the two-dimensional distribution of 
water content at a constant temperature of 25 degrees
"""

def watercomputing(
    start=[0, 0],
    end=[47, -8],
    quality=33.5,
    area=0.5,
    lam=10,
    maxIter=6,
    dPhi=2,
    A=246.47,
    B=-0.627,
):
    "ERT Inversion and Visualization process"

    # Define output directory
    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_folder, exist_ok=True)  # Create the output directory if it doesn't exist

    # Change working directory to where raw data files are located
    raw_data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Raw")
    os.chdir(raw_data_folder)

    """ Begin Workflow """

    # Iterate directory
    entries_sel = [file for file in os.listdir() if file.endswith(".txt")]

    """ Create Geometry and Mesh"""

    geom = mt.createWorld(start, end, worldMarker=False)
    mesh = mt.createMesh(geom, quality, area, smooth=True)
    print("mesh", mesh)
    mesh_path = os.path.join(output_folder, "mesh.bms")
    mesh.save(mesh_path)

    centers = mesh.cellCenters()
    x_coordinates = centers[:, 0]
    y_coordinates = centers[:, 1]
    Storage = np.zeros([np.shape(mesh.cellMarkers())[0], len(entries_sel)])

    """ Begin Inversion """

    for i, date in enumerate(entries_sel):
        mgr = ert.ERTManager(date, verbose=True, debug=True)  # load the file
        rhoa = np.array(mgr.data["rhoa"])  # convert resistivity data in numpy vector
        Argw = np.argwhere(rhoa <= 0)  # index of negative resistance

        """ Filter negative value """
        mgr.data.remove(mgr.data["rhoa"] < 0)
        """ Add estimated Error and geometrical factor """
        mgr.data["err"] = ert.estimateError(mgr.data, absoluteError=0.001, relativeError=0.03)
        pg.info("Filtered rhoa (min/max)", min(mgr.data["rhoa"]), max(mgr.data["rhoa"]))
        mgr.data["k"] = ert.createGeometricFactors(mgr.data, numerical=True)

        """Inversion """
        inv = mgr.invert(mesh=mesh, lam=lam, maxIter=maxIter, dPhi=dPhi, CHI1OPT=5, Verbose=True)

        """Storing and saving data for later manipulation"""
        Storage[:, i] = inv
        result_path = os.path.join(output_folder, f"{date[:-4]}_result.dat")
        mgr.saveResult(result_path)
        print("Saved result to", result_path)
        print(Storage)

        """Plotting"""
        fSWC = lambda x: A * x**B

        # fixed temperature (it can be an input in GUI and adjust later)
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

        print("SWC Data:")
        print(Storage)

        fig1, (ax1) = plt.subplots(1, sharex=True, figsize=(15.5, 7), gridspec_kw={"height_ratios": [2]})

        pg.viewer.show(
            mesh=mesh,
            data=SWC[:, 0],
            hold=True,
            label="Soil water content",
            ax=ax1,
            cMin=0,
            cMax=30,
            cMap="Spectral",
            showMesh=True,
        )

        labels = date
        ax1.set_xlim(-0, mgr.paraDomain.xmax())
        ax1.set_ylim(-8, mgr.paraDomain.ymax())
        ax1.set_title(labels)
        image_path = os.path.join(output_folder, "result_water_content.jpg")
        plt.savefig(image_path)
        plt.close()
        print("Saved plot to", image_path)

    print("Processing completed.")

if __name__ == "__main__":
    watercomputing()
