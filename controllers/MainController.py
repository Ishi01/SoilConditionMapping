# controller.py
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtWidgets import QFileDialog, QGraphicsPixmapItem, QDialog, QTableWidgetItem, QVBoxLayout, QPushButton
from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from models.DataManager import DataModel
from views.MainWindowView import MainView

import os
import matplotlib.pyplot as plt
import numpy as np
import pygimli as pg


class Controller:
    def __init__(self):
        self.model = DataModel()
        self.view = MainView()

        # Connect signals to slots
        self.view.pushButton_importfile.clicked.connect(self.open_file_dialog)
        self.view.pushButton_Import.clicked.connect(self.switch_to_preprocessing_tab)
        self.view.pushButton_Transfer_Data.clicked.connect(self.data_show)
        self.view.pushButton_next_to_domain.clicked.connect(self.jump_to_next_page)
        self.view.pushButton_next_to_visualization.clicked.connect(self.jump_to_next_visualization)

        self.view.pushButton_domain_apply.clicked.connect(self.create_domain)
        self.view.pushButton_next_to_mesh.clicked.connect(self.next_to_mesh)
        self.view.pushButton_mesh_save.clicked.connect(self.create_mesh)

        self.view.pushButton_inversion_apply.clicked.connect(self.startInversion)
        self.view.pushButton_inversion_save.clicked.connect(self.saveFig)
        self.view.pushButton_next_to_watercontent.clicked.connect(self.next_to_watercontent)

        self.view.pushButton_watercontent_calculate.clicked.connect(self.showImage)
        self.view.doubleSpinBox_Temperature.valueChanged.connect(self.update_variable)
        self.view.pushButton_import_soil_field.clicked.connect(self.openTableDialog)
        self.view.pushButton_multiplefiles_processing.clicked.connect(self.data_processing_multiple_files)

        self.view.pushButton_next_to_vis.clicked.connect(self.next_to_vis)

    def show_view(self):
        self.view.show()

    def open_file_dialog(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self.view, "Select .tx0 files", "",
                                                "TX0 Files (*.tx0);;All Files (*)", options=options)
        save_directory = QFileDialog.getExistingDirectory(self.view, "Select Directory")

        if not save_directory:
            return

        self.model.set_save_directory(save_directory)

        copied_files = self.model.import_files(files)
        self.view.listWidget_file_list.clear()
        for file in copied_files:
            item = QtWidgets.QListWidgetItem(file)
            item.setForeground(QColor('black'))
            self.view.listWidget_file_list.addItem(item)

        if copied_files:
            with open(copied_files[0], 'r') as f:
                content = f.read()
                self.view.textBrowser_showdata.setPlainText(content)

    def switch_to_preprocessing_tab(self):
        index_of_page = 1
        self.view.tabWidget_Data.setCurrentIndex(index_of_page)

    def data_show(self):
        save_directory = self.model.get_save_directory()
        os.chdir(save_directory)
        for file in os.listdir(save_directory):
            if file.endswith('.txt'):
                with open(file, 'r') as f:
                    content = f.read()
                    self.view.textBrowser_showdata.setPlainText(content)
                break

    def jump_to_next_page(self):
        index_of_page = 1
        self.view.tabWidget_Importing.setCurrentIndex(index_of_page)

    def jump_to_next_visualization(self):
        index_of_page = 4
        self.view.tabWidget_Importing.setCurrentIndex(index_of_page)

    def create_domain(self):
        start_x = self.view.spinBox_startX.value()
        start_y = self.view.spinBox_startY.value()
        end_x = self.view.spinBox_endX.value()
        end_y = self.view.spinBox_endY.value()

        geom = self.model.create_domain(start_x, start_y, end_x, end_y)
        ax = self.view.canvas_domain.figure.add_subplot(111)
        ax.clear()
        ax.yaxis.set_major_locator(plt.MultipleLocator(2.0))

        pg.show(geom, ax=ax, boundary=True)
        self.view.canvas_domain.draw()

    def create_mesh(self):
        quality = self.view.doubleSpinBox_quality.value()
        area = self.view.doubleSpinBox_area.value()
        geom = self.model.create_domain(0, 0, 50, 50)  # domain creation, (x,y) axis with limit of (0-50,0-50)

        mesh = self.model.create_mesh(geom, quality, area)
        ax = self.view.canvas_mesh.figure.add_subplot(111)
        ax.clear()
        ax.yaxis.set_major_locator(plt.MultipleLocator(2.0))

        pg.show(mesh, ax=ax, boundary=True)
        self.view.canvas_mesh.draw()

    def next_to_mesh(self):
        index_of_page = 1
        self.view.tabWidget.setCurrentIndex(index_of_page)

    def startInversion(self):
        save_directory = self.model.get_save_directory()
        maxIter = self.view.spinBox_Iterations.value()
        lam = self.view.spinBox_Lambda.value()
        dPhi = self.view.spinBox_dPhi.value()

        file_to_convert = None
        os.chdir(save_directory)
        for file in os.listdir(save_directory):
            if file.endswith('.txt'):
                file_to_convert = file
                break

        geom = self.model.create_domain(0, 0, 50, 50)  # mesh domain with grid, (x,y) axis with limit of (0-50,0-50)
        mesh = self.model.create_mesh(geom, 1, 1)

        inv, storage = self.model.start_inversion(file_to_convert, mesh, lam, maxIter, dPhi)

        fig1, (ax1) = plt.subplots(1, sharex=True, figsize=(16.0, 5))
        ax1.set_xlim(0, 50)
        ax1.set_ylim(-8, 50)
        ax1.set_title(file_to_convert)

        self.view.canvas = FigureCanvas(fig1)
        self.view.inversion_result_layout.addWidget(self.view.canvas)
        self.view.inversion_result_widget.update()
        self.view.fig1 = fig1

    def saveFig(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getSaveFileName(
            None, "Save Figure", "", "PNG Files (*.png);;All Files (*)", options=options
        )

        if file_name:
            self.view.fig1.savefig(file_name, format="png")

    def showImage(self):
        try:
            geom = self.model.create_domain(0, 0, 50, 50)
            mesh = self.model.create_mesh(geom, 1, 1)
            storage = np.zeros([np.shape(mesh.cellMarkers())[0], 1])
            tem_field = self.model.get_temperature_field()

            SWC = self.model.calculate_water_content(mesh, storage, tem_field)

            fig1, (ax1) = plt.subplots(1, sharex=(True), figsize=(15.5, 7), gridspec_kw={'height_ratios': [2]})
            pg.viewer.show(mesh=mesh, data=SWC[:, 0], hold=True, label='Soil water content', ax=ax1, cMin=0, cMax=30,
                           cMap='Spectral', showMesh=True)
            labels = "Water Content"
            ax1.set_xlim(-0, 50)
            ax1.set_ylim(-8, 50)
            ax1.set_title(labels)
            plt.savefig('result_wat.jpg')
            plt.close()

            image_path = "result_wat.jpg"
            pixmap = QPixmap(image_path)
            canvas_width = 765
            canvas_height = 600
            scaled_pixmap = pixmap.scaled(canvas_width, canvas_height, QtCore.Qt.KeepAspectRatio)

            pixmap_item = QGraphicsPixmapItem(scaled_pixmap)
            self.view.scene.clear()
            self.view.scene.addItem(pixmap_item)
            self.view.scene.setSceneRect(pixmap_item.boundingRect())

        except Exception as e:
            print("An error occurred:", e)

    def update_variable(self, value):
        self.model.set_temperature(value)

    def openTableDialog(self):
        dialog = TableDialog(self.view.Water_content)
        dialog.exec_()

    def data_processing_multiple_files(self):
        pass

    def next_to_watercontent(self):
        index_of_page = 3
        self.view.tabWidget_Importing.setCurrentIndex(index_of_page)

    def next_to_vis(self):
        index_of_page = 4
        self.view.tabWidget_Importing.setCurrentIndex(index_of_page)


class TableDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Editable Table Dialog')

        self.table_widget = QtWidgets.QTableWidget(self)
        self.table_widget.setEditTriggers(QtWidgets.QTableWidget.AllEditTriggers)

        self.button = QtWidgets.QPushButton('Get Values', self)
        self.button.setGeometry(50, 220, 100, 30)
        try:
            self.button.clicked.connect(self.getValues)
        except Exception as e:
            print("An error occurred:", e)

        self.table_widget.setRowCount(3)
        self.table_widget.setColumnCount(2)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.table_widget)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def getValues(self):
        values = []
        global tem_field
        tem_field = []

        for row in range(self.table_widget.rowCount()):
            row_values = []
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                if item is not None:
                    row_values.append(item.text())
                else:
                    row_values.append('')
            values.append(row_values)

        tem_field = [(float(row[0]), float(row[1])) for row in values]
