import os
import shutil
import threading
import time
from matplotlib import pyplot as plt
import pygimli as pg
import pygimli.meshtools as mt
from pygimli.physics import ert
import tkinter as tk
from tkinter import filedialog

# Define paths to the processed data directories
processed_data_dir1 = os.path.join(os.path.dirname(__file__), 'outputs/corrected_resistivity_detailed')
processed_data_dir2 = os.path.join(os.path.dirname(__file__), 'outputs/corrected_resistivity_simplified')

# Threading event
inversion_done_event = threading.Event()

def select_directory():
    """
    Function to open a file dialog to select a directory.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    selected_dir = filedialog.askdirectory(title="Select Processed Data Directory")
    root.destroy()
    return selected_dir

def inversion(
        processed_data_dir,
        start=[0, 0],
        end=[47, -8],
        quality=33.5,
        area=0.5,
        work_dir=None,
        inversion_params=None
):
    """
    ERT Inversion and Visualization
    """
    if work_dir is None:
        work_dir = os.getcwd()

    # Resistivity img
    output_dir = os.path.join(work_dir, 'outputs/resis_mapping')
    os.makedirs(output_dir, exist_ok=True)

    # tmp mesh
    tmp_dir = os.path.join(work_dir, 'outputs/tmp')
    os.makedirs(tmp_dir, exist_ok=True)

    # Find all txt files in the folder
    entries_sel = [file for file in os.listdir(processed_data_dir) if file.endswith(".txt")]

    # Creating geometrics and meshes
    geom = mt.createWorld(start=start, end=end, worldMarker=False)
    pg.show(geom, boundaryMarker=True)
    mesh = mt.createMesh(geom, quality=quality, area=area, smooth=True)
    pg.show(mesh)

    # Ensure inversion_params is not None
    if inversion_params is None:
        inversion_params = {}  # use empty dict

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

        # Save mesh with a unique name in outputs/tmp
        mesh_filename = f"{date.replace('.txt', '')}.bms"
        mesh_filepath = os.path.join(tmp_dir, mesh_filename)
        mesh.save(mesh_filepath)

        # Save and display
        fig1, ax1 = plt.subplots(1, figsize=(16.0, 5))
        mgr.showResult(ax=ax1, cMin=50, cMax=1000)
        labels = date
        ax1.set_xlim(-0, mgr.paraDomain.xmax())
        ax1.set_ylim(-10, mgr.paraDomain.ymax())
        ax1.set_title(labels)
        plt.tight_layout()

        # Save figure to outputs/resis_mapping
        output_image_path = os.path.join(output_dir, f"{date.replace('.txt', '')}_result.png")
        fig1.savefig(output_image_path)

        plt.close(fig1)

    plt.show()

    # thread event set
    inversion_done_event.set()


def delete_temporary_files(work_dir):
    """
    auto delete vector files
    """
    # wait for inversion to complete
    inversion_done_event.wait()

    # Wait for a short period to ensure files are not in use
    time.sleep(1)

    # delete designated files
    for folder in os.listdir(work_dir):
        folder_path = os.path.join(work_dir, folder)
        # Ensure the folder is not input or output related, and not the main folders
        if os.path.isdir(folder_path) and folder not in ['outputs', 'inputs', 'lib', '.git']:
            try:
                shutil.rmtree(folder_path)
            except OSError as e:
                print(f"Error: {folder_path} : {e.strerror}")

    # exit
    os._exit(0)


# Main function
if __name__ == "__main__":
    work_dir = os.getcwd()

    processed_data_dir2 = select_directory()

    # Check if a directory was selected
    if not processed_data_dir2:
        print("No directory selected, exiting.")
        exit()

    # 2 thread
    inversion_thread = threading.Thread(target=inversion, args=(processed_data_dir2,),
                                        kwargs={'work_dir': work_dir, 'inversion_params': {}})
    deletion_thread = threading.Thread(target=delete_temporary_files, args=(work_dir,))

    var = deletion_thread.daemon

    inversion_thread.start()
    deletion_thread.start()

    inversion_thread.join()