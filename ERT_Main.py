import os

import matplotlib.pyplot as plt
import numpy as np
import pybert as pb
import pygimli as pg
import pygimli.meshtools as mt
from pygimli.physics import ert

# %%

# set up the default value for the function
def inversion(start=[0,0], end=[47, -8], quality=33.5, area=0.5, work_dir="/Users/hayeenxue/SoilConditionMapping/"):
    "ERT Inversion and Visualization process"

    folder = r"..\..\ERT_Project\Raw"  # Update this to reflect the folder lcoation
    os.chdir(folder)

    """ Begin Workflow """

    # Iterate directory
    entries_sel = []

    for file in os.listdir():
        # check only text files
        if file.endswith(".tx0"):
            entries_sel.append(file)


    """ Create Geometry and Mesh -  This is the preferred way (but we'll talk about it next time """

    geom = mt.createWorld(
        start=start, end=end, worldMarker=False
    ) 
    pg.show(geom, boundaryMarker=True)
    mesh = mt.createMesh(
        geom, quality=quality, area=area, smooth=True
    ) 
    mesh.save("mesh.bms")


    Storage = np.zeros([np.shape(mesh.cellMarkers())[0], np.shape(entries_sel)[0]])

    """ Begin Inversion """

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
        Accur = (1 - np.shape(Argw)[0] / np.shape(rhoa)[0]) * 100  # Percentage of Accuracy
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