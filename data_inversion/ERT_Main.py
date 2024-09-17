import glob
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


# def get_first_raw_file():
#     raw_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Raw")
#     files = [
#         f for f in os.listdir(raw_folder) if os.path.isfile(os.path.join(raw_folder, f))
#     ]
#     if not files:
#         raise FileNotFoundError("No files found in the Raw folder")
#     return os.path.join(raw_folder, sorted(files)[0])


def create_mesh(start=[0, 0], end=[47, -8], quality=33.5, area=0.5):
    # Create Geometry and Mesh
    geom = mt.createWorld(start=start, end=end, worldMarker=False)
    mesh = mt.createMesh(geom, quality=quality, area=area, smooth=True)
    mesh.save("mesh.bms")
    return mesh


def startInversion(start, end, quality, area, inversion_params, file_path, zWeight=0.7):
    # Unpack inversion parameters
    lam = inversion_params["lambda"]
    maxIter = inversion_params["max_iterations"]
    dPhi = inversion_params["dphi"]
    robust_data = inversion_params["robust_data"]

    # Log inversion starting details
    print(f"Starting inversion with file: {file_path}")
    print(f"Using parameters: lambda={lam}, maxIter={maxIter}, dPhi={dPhi}, robust={robust_data}, zWeight={zWeight}")

    output_dir = ensure_output_folder()

    # Load the data file (processed file selected in the UI)
    try:
        file_to_convert = file_path  # Use the passed processed file path
    except FileNotFoundError as e:
        pg.error(str(e))
        return

    # Create the mesh
    mesh = create_mesh(start, end, quality, area)

    # Inversion preparing
    date = os.path.basename(file_to_convert)  # Extract the file name from the path
    mgr = ert.ERTManager(file_to_convert, verbose=True, debug=True)
    rhoa = np.array(mgr.data["rhoa"])
    Argw = np.argwhere(rhoa <= 0)
    pg.info("Filtered rhoa (min/max)", min(mgr.data["rhoa"]), max(mgr.data["rhoa"]))
    Accur = (1 - np.shape(Argw)[0] / np.shape(rhoa)[0]) * 100

    # Data processing: Filter negative values
    mgr.data.remove(mgr.data["rhoa"] < 0)

    # Add estimated error and geometrical factor
    mgr.data["err"] = ert.estimateError(
        mgr.data, absoluteError=0.001, relativeError=0.03
    )
    pg.info("Filtered rhoa (min/max)", min(mgr.data["rhoa"]), max(mgr.data["rhoa"]))
    mgr.data["k"] = ert.createGeometricFactors(mgr.data, numerical=True)

    # Inversion process
    tolerance = 1  # Abort criterion for chi2
    for iteration in range(maxIter):
        inv = mgr.invert(
            mesh=mesh, zWeight=zWeight, lam=lam, maxIter=1, dPhi=dPhi, CHI1OPT=5, Verbose=True
        )

        if hasattr(inv, "chi2"):
            chi2 = inv.chi2()  # Get the chi2 value for the current iteration

            # Check if chi2 is below the tolerance level
            if chi2 < tolerance:
                pg.info(f"Inversion converged at iteration {iteration}. Chi2: {chi2}")
                break

    # Storing and saving data for later manipulation
    Storage = np.zeros([np.shape(mesh.cellMarkers())[0], 1])
    Storage[:, 0] = inv
    mgr.saveResult(date[:-4])

    # Plotting
    fig1, (ax1) = plt.subplots(1, sharex=True, figsize=(16.0, 5))
    mgr.showResult(ax=ax1, cMin=50, cMax=15000)
    labels = date
    ax1.set_xlim(0, mgr.paraDomain.xmax())
    ax1.set_ylim(-8, mgr.paraDomain.ymax())
    ax1.set_title(labels)
    plt.tight_layout()

    # Save the figure as PNG in the output folder
    fig_filename = os.path.join(
        output_dir, f"inversion_result_{os.path.splitext(date)[0]}.png"
    )
    plt.savefig(fig_filename, dpi=300, bbox_inches="tight")
    print(f"Figure saved as: {fig_filename}")

    plt.close(fig1)
    plt.close("all")

    cleanup_temp_files()

    return fig_filename  # Return the path of the saved figure

# if __name__ == "__main__":
#     startInversion()
#     cleanup_temp_files()
