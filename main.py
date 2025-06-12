import sys
import multiprocessing as mp
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

def apply_stylesheets(qss, app):
    with open(qss, "r") as f:
        _style = f.read()
    app.setStyleSheet(_style)

if __name__ == '__main__':
    mp.set_start_method("spawn")
    app = QApplication(sys.argv)
    window = MainWindow()
    apply_stylesheets('./utils/stylesheets/test.qss', app)
    window.show()
    sys.exit(app.exec_())