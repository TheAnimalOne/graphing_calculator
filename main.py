import sys
import ctypes

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from graphing_calculator.ui_components.calculator_window import CalculatorWindow

APP_ID = u'graphing_calculator_app.v1.0.0'


def main():
    print("Starting App!")
    # add logo to bar
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    graphing_calculator_app = QApplication([])
    # add logo
    # graphing_calculator_app.setWindowIcon(QIcon("classes/convertible.png"))
    # set dark mode
    graphing_calculator_app.styleHints().setColorScheme(Qt.ColorScheme.Dark)
    calculator_app_window = CalculatorWindow()
    calculator_app_window.show()
    sys.exit(graphing_calculator_app.exec())

if __name__ == "__main__":
    main()