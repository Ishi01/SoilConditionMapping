# main.py
from PyQt5.QtWidgets import QApplication
from controllers.MainController import Controller
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = Controller()
    controller.show_view()
    sys.exit(app.exec_())
