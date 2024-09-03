import os

import matplotlib.pyplot as plt
import numpy as np
import pybert as pb
import pygimli as pg
import pygimli.meshtools as mt
from pygimli.physics import ert

# %%


# set up the default value for the function
def inversion(
    start=[0, 0],
    end=[47, -8],
    quality=33.5,
    area=0.5,
    work_dir="D:/Python/SoilConditionMapping/03bertTC",
):
    "ERT Inversion and Visualization process"

    # Print the current working directory
    print("Current Working Directory:", os.getcwd())

    # Define the folder path
    folder = work_dir
    print("Expected directory:", folder)

    # Check if the folder exists
    if os.path.isdir(folder):
        print("Directory exists:", folder)
    else:
        print("Directory not found:", folder)

    """ Begin Workflow """

    """ 
    `entries_sel` is reading the orginal `.tx0` files
    but now need to read the integrated file (including the `txt` and temprature data)
    Then it will be have the index inbound error in line 181 => `data=SWC[:, 1],`
    So need to figure out which data should be used to plot the model (2 figures) in the end
    """
    



    # Iterate directory
    entries_sel = []

    for file in os.listdir():
        # check only text files
        if file.endswith(".txt"):
            entries_sel.append(file)

    print("files:", os.listdir())
    print("entries_sel:", entries_sel)

    """ Create Geometry and Mesh -  This is the preferred way (but we'll talk about it next time """

    geom = mt.createWorld(start=start, end=end, worldMarker=False)
    pg.show(geom, boundaryMarker=True)
    mesh = mt.createMesh(geom, quality=quality, area=area, smooth=True)
    mesh.save("mesh.bms")

    Storage = np.zeros([np.shape(mesh.cellMarkers())[0], np.shape(entries_sel)[0]])

    print("Storage shape:", Storage.shape)

    """ Begin Inversion """

    """ 
    - line24-27 & line52-59:
    this place is reading `tx0` files and doing the inversion, 
    but now we should change to read the intergrated file(includding the txt and temprature data) and  then do the inversion
    
    - after that, it should be identical to line64 to load the intergrated file, then use the `mgr.invert` to plot the result
    """
    for i in range(0, len(entries_sel) - 1):

        date = entries_sel[i]

        """ Create working directory"""
        work_dir = work_dir + date
        os.makedirs(work_dir, exist_ok=True)
        os.chdir(work_dir)

        """ Load the inputs into the library"""

        mgr = ert.ERTManager(entries_sel[i], verbose=True, debug=True)  # load the file

        """ Search for negative values and calculate accuracy"""

        rhoa = np.array(mgr.data["rhoa"])  # convert resistivity data in numpy vector
        Argw = np.argwhere(rhoa <= 0)  # index of negative resistance
        pg.info("Filtered rhoa (min/max)", min(mgr.data["rhoa"]), max(mgr.data["rhoa"]))
        Accur = (
            1 - np.shape(Argw)[0] / np.shape(rhoa)[0]
        ) * 100  # Percentage of Accuracy
        # as (1 - negative values/total values) * 100 # Accur is something I'd like to be printed as information

        """ Remove negative value 2 methods - Use first """

        mgr.data.remove(
            mgr.data["rhoa"] < 0
        )  # Remove the data directly (This should be ok with a fixed mesh created outside of the for cycle)

        # for i in range(0,len(Argw)):
        #     rhoa[Argw[i]] = rhoa[Argw[i] - 1]  # Replace negative with previous value NB. This needs to be improved
        # mgr.data['rhoa'] = rhoa                 # Feed back the corrected resistance vector

        """ Add estimated Error and geometrical factor - These are needed by the """

        mgr.data["err"] = ert.estimateError(
            mgr.data, absoluteError=0.001, relativeError=0.03
        )  # Leave as it is for now
        pg.info("Filtered rhoa (min/max)", min(mgr.data["rhoa"]), max(mgr.data["rhoa"]))
        mgr.data["k"] = ert.createGeometricFactors(
            mgr.data, numerical=True
        )  # Leave as it is for now
        ert.show(mgr.data)

        """Inversion """

        # inv = mgr.invert(mesh=mesh, lam=10, maxIter=6, dPhi=2, CHI1OPT=5, Verbose=True) # We want to able to input
        # maxIter, Lam, dPhi

        # More complex way of inverting. WE WILL Look at it later

        # inv = mgr.invert(SURFACESMOOTH=1,paraDX=0.8,TOPOGRAPHY=1, PARA2DQUALITY=33.8, paraMaxCellSize=0.5,
        #                  maxIter=10, LAMBDA=30, CHI1OPT=2, verbose=True)

        inv = mgr.invert(
            mgr.data,
            lam=50,
            verbose=True,
            paraDX=0.3,
            paraMaxCellSize=10,
            paraDepth=20,
            quality=33.5,
            maxIter=10,
            dPhi=0.5,
            robustData=True,
        )

        # np.testing.assert_approx_equal(mgr.inv._inv.chi2(),2)  assessing the quality of the inversion with Chi^2 metric

        """Storing and saving data for later manipulation"""

        # Storage[:,i]= inv # Save in Variable for manipulation
        # mgr.saveResult(date[:-4]) # Save results in folder

        """Plotting"""

        fig1, (ax1) = plt.subplots(1, figsize=(16.0, 5))
        mgr.showResult(ax=ax1, cMin=50, cMax=1000)
        labels = date
        ax1.set_xlim(-0, mgr.paraDomain.xmax())
        ax1.set_ylim(-10, mgr.paraDomain.ymax())
        ax1.set_title(labels)
        plt.tight_layout()

    ##%%

    """Converting resistivity to soil water content and visualize"""
    # pg.viewer.showMesh(mesh,data=Storage[:,1]-Storage[:,0])
    fSWC = lambda x: 246.47 * x ** (-0.627)
    fSWC_2 = lambda x: 211 * x ** (-0.59)

    SWC = fSWC(Storage)

    print("x shape:", Storage.shape)
    print("fSWC shape:", SWC.shape)
    print("SWC shape:", SWC.shape)

    fig1, (ax1) = plt.subplots(
        1, sharex=(True), figsize=(15.5, 7), gridspec_kw={"height_ratios": [2]}
    )
    pg.viewer.show(
        mesh=mesh,
        data=SWC[:, 1],
        hold=True,
        label="Soil waeter content",
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
    plt.tight_layout()
    plt.show()

    return fig1
