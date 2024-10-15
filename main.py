import sys
import time
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplashScreen
from PyQt5 import QtWidgets
from UI import Ui_MainWindow
from ui_logic import setup_ui_logic


def main():
    app = QApplication(sys.argv)

    splash_pix = QPixmap('docs/Startup.PNG')
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowFlag(Qt.FramelessWindowHint)
    splash.show()

    for i in range(1, 6):
        time.sleep(0.5)  # Fake loading time
        splash.showMessage(f"Loading... {i * 20}%", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        app.processEvents()

    main_window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(main_window)
    setup_ui_logic(ui, main_window)
    main_window.show()
    splash.close()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
