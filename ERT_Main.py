import os
from matplotlib import pyplot as plt
import numpy as np

import pygimli as pg
import pygimli.meshtools as mt
from pygimli.physics import ert

# Define paths to the processed data directories
processed_data_dir1 = os.path.join(os.path.dirname(__file__), 'outputs/corrected_resistivity_detailed')
processed_data_dir2 = os.path.join(os.path.dirname(__file__), 'outputs/corrected_resistivity_simplified')


def inversion(
        processed_data_dir,  # 处理后数据所在目录
        start=[0, 0],
        end=[47, -8],
        quality=33.5,
        area=0.5,
        work_dir=None,
        inversion_params=None  # 用于配置反演参数的字典
):
    """
    ERT Inversion and Visualisation
    """
    if work_dir is None:
        work_dir = os.getcwd()

    os.makedirs(work_dir, exist_ok=True)

    # Set the current working directory
    os.chdir(processed_data_dir)

    # Find all txt files in the folder
    entries_sel = [file for file in os.listdir() if file.endswith(".txt")]

    # Creating geometrics and meshes
    geom = mt.createWorld(start=start, end=end, worldMarker=False)
    pg.show(geom, boundaryMarker=True)
    mesh = mt.createMesh(geom, quality=quality, area=area, smooth=True)
    mesh.save("mesh.bms")

    Storage = np.zeros([np.shape(mesh.cellMarkers())[0], np.shape(entries_sel)[0]])

    # Ensure inversion_params ! None
    if inversion_params is None:
        inversion_params = {}  # use empty dic

    # Inversion
    for i, date in enumerate(entries_sel):
        # Set working dir
        current_work_dir = os.path.join(work_dir, date)
        os.makedirs(current_work_dir, exist_ok=True)
        os.chdir(current_work_dir)

        file_path = os.path.join(processed_data_dir, date)
        mgr = ert.ERTManager(file_path, verbose=True, debug=True)

        # remove negative rhoa
        mgr.data.remove(mgr.data["rhoa"] < 0)

        # adds error estimation
        mgr.data["err"] = ert.estimateError(
            mgr.data, absoluteError=0.001, relativeError=0.03
        )
        mgr.data["k"] = ert.createGeometricFactors(mgr.data, numerical=True)
        ert.show(mgr.data)

        # use params to do the inversion
        inv = mgr.invert(
            mgr.data,
            **inversion_params  # params provided by UI
        )

        # Save and display
        fig1, ax1 = plt.subplots(1, figsize=(16.0, 5))
        mgr.showResult(ax=ax1, cMin=50, cMax=1000)
        labels = date
        ax1.set_xlim(-0, mgr.paraDomain.xmax())
        ax1.set_ylim(-10, mgr.paraDomain.ymax())
        ax1.set_title(labels)
        plt.tight_layout()

    plt.show()
    return fig1


# Main function
if __name__ == "__main__":
    inversion(processed_data_dir2, inversion_params={})
