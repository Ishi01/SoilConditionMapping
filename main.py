import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from UI import Ui_MainWindow
from ui_logic import setup_ui_logic


def main():
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(main_window)
    setup_ui_logic(ui, main_window)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
