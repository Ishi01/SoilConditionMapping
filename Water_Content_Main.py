import os
import matplotlib.pyplot as plt
import numpy as np
import pygimli as pg
import pygimli.meshtools as mt
from pygimli.physics import ert


'''
This function will compute the two-dimensional distribution of 
water content at a constant temperature of 25 degrees
'''
def watercomputing(start=[0, 0], end=[47, -8],quality=33.5, area=0.5,lam=10, maxIter=6, dPhi=2,A=246.47,B=-0.627):
  "ERT Inversion and Visualization process"

  folder = r"."  # Update this to reflect the folder lcoation
  os.chdir(folder)

  ''' Begin Workflow '''

  # Iterate directory
  entries_sel = []

  for file in os.listdir():
          # check only text files
          if file.endswith('.txt'):
                  entries_sel.append(file)

  ''' Create Geometry and Mesh'''

  geom = mt.createWorld(start, end,
                        worldMarker=False)  
  #pg.show(geom, boundaryMarker=True)
  mesh = mt.createMesh(geom, quality, area,
                        smooth=True)  
  print("mesh", mesh)
  mesh.save("mesh.bms")

  centers = mesh.cellCenters()
  x_coordinates = centers[:, 0]
  y_coordinates = centers[:, 1]
  np.shape(centers)
  print("x_coordinates", x_coordinates)
  print("y_coordinates", y_coordinates)
  Storage = np.zeros([np.shape(mesh.cellMarkers())[0], np.shape(entries_sel)[0]])

  ''' Begin Inversion '''

  for i in range(0, len(entries_sel) - 1):

          date = entries_sel[i]
          mgr = ert.ERTManager(entries_sel[i], verbose=True, debug=True)  # load the file
          rhoa = np.array(mgr.data['rhoa'])  # convert resistivity data in numpy vector
          Argw = np.argwhere(rhoa <= 0)  # index of negative resistance
          #pg.info('Filtered rhoa (min/max)', min(mgr.data['rhoa']), max(mgr.data['rhoa']))
          #Accur = (1 - np.shape(Argw)[0] / np.shape(rhoa)[0]) * 100  # Percentage of Accuracy
          # as (1 - negative values/total values) * 100
          # Accur is something I'd like to be printed as information

          ''' Filter negative value '''

          mgr.data.remove(mgr.data[
                                  "rhoa"] < 0)  # Remove the data directly (This should be ok with a fixed mesh created outside of the for cycle)

          ''' Add estimated Error and geometrical factor'''

          mgr.data['err'] = ert.estimateError(mgr.data, absoluteError=0.001,
                                              relativeError=0.03)  # Leave as it is for now
          pg.info('Filtered rhoa (min/max)', min(mgr.data['rhoa']), max(mgr.data['rhoa']))
          mgr.data['k'] = ert.createGeometricFactors(mgr.data, numerical=True)  # Leave as it is for now
          #ert.show(mgr.data)

          '''Inversion '''

          inv = mgr.invert(mesh=mesh, lam=lam, maxIter=maxIter, dPhi=dPhi, CHI1OPT=5,
                            Verbose=True)  # We want to able to input
          # maxIter, Lam, dPhi

          # More complex way of inverting. WE WILL Look at it later

          # inv = mgr.invert(secNodes=2,SURFACESMOOTH=1,paraDX=0.5,TOPOGRAPHY=1, PARA2DQUALITY=33.8,EQUIDISTBOUNDARY=1, paraMaxCellSize=2.0,
          #                 maxIter=20, LAMBDA=30, CHI1OPT=2, verbose=True)

          # np.testing.assert_approx_equal(mgr.inv._inv.chi2(),2)  assessing the quality of the inversion with Chi^2 metric

          '''Storing and saving data for later manipulation'''

          Storage[:, i] = inv  # Save in Variable for manipulation
          mgr.saveResult(date[:-4])  # Save results in folder
          print("12", mgr.saveResult(date[:-4]))
          print(Storage)
          '''Plotting'''

          # fig1, (ax1) = plt.subplots(1, sharex=(True), figsize=(16.0, 5))
          # mgr.showResult(ax=ax1, cMin=50, cMax=15000)
          # labels = date
          # ax1.set_xlim(-0, mgr.paraDomain.xmax())
          # ax1.set_ylim(-8, mgr.paraDomain.ymax())
          # ax1.set_title(labels)
          # plt.tight_layout()
          # plt.close()

          ##%%

          '''Converting resistivity to soil water content and visualize'''
          # pg.viewer.showMesh(mesh,data=Storage[:,1]-Storage[:,0])
          fSWC = lambda x: A * x ** B
          fSWC_2 = lambda x: 211 * x ** (-0.59)

          # temperature
          # Define the temperature points
          # temperature_points = [
          #         (0, -5),
          #         (-10, -5)
          # ]
          global tem_field
          print("t111111111111111",tem_field)
          temperature_points = tem_field
          temperature_points.sort(key=lambda x: x[0])
          for j in range(len(y_coordinates) - 1):
                  y = y_coordinates[j]
                  # Find the temperature segment the current belongs to
                  for i in range(len(temperature_points) - 1):
                          y1, T1 = temperature_points[i]
                          y2, T2 = temperature_points[i + 1]
                          if y1 <= y <= y2:
                                  # Linearly interpolate the temperature value
                                  T = T1 + (T2 - T1) * ((y - y1) / (y2 - y1))
                                  break
                          else:
                                  # If y is out of bounds of the temperature points, use the nearest boundary value
                                  T = T1 if y < y1 else T2
                  Storage[j, :] = (1 + 0.025 * (T - 25)) * Storage[j, :]

          # T = 25.5
          # Storage1 = (1 + 0.025 * (T - 25))*Storage
          # SWC = fSWC(Storage1)

          SWC = fSWC(Storage)

          print("11111111111")
          print(Storage)

          fig1, (ax1) = plt.subplots(1, sharex=(True), figsize=(15.5, 7), gridspec_kw={'height_ratios': [2]})
          # plt.close()
          pg.viewer.show(mesh=mesh, data=SWC[:, 0], hold=True, label='Soil water content', ax=ax1, cMin=0,
                          cMax=30,
                          cMap='Spectral', showMesh=True)
          print("12321321131321")

          labels = date
          ax1.set_xlim(-0, mgr.paraDomain.xmax())
          ax1.set_ylim(-8, mgr.paraDomain.ymax())
          ax1.set_title(labels)
          plt.savefig('result_water_content.jpg')
          plt.close()
          print("end")
          # plt.tight_layout()
          # plt.show()



# plt.savefig('result_water_content.jpg')
# result=fig1
# self.result=result
#
# plt.tight_layout()
# plt.show()