import sys
from enum import StrEnum

from PyQt6.QtWidgets import (
    QTabWidget,
    QLineEdit,
    QWidget,
    QLayout,
    QComboBox,
    QPlainTextEdit,
    QListWidget,
    QVBoxLayout,
    QDateEdit,
    QPushButton,
    QHBoxLayout,
    QAbstractItemView,
    QGridLayout,
    QApplication,
)
from graphing_calculator.functional_tree.function_node import FunctionNode
from graphing_calculator.mathematical_interpreter.interpreter import interpret_text_to_tree


class CalculationOptions(StrEnum):
    CALCULATE = "CALC"
    DEFINE = "DEFN"
    DIFFERENTIATE = "DIFF"


APP_NAME = "Graphing Calculator"


class CalculatorWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)

        main_layout = QGridLayout(self)
        self.setLayout(main_layout)

        # create a tab widget
        tab = QTabWidget(self)

        # create calculator tab
        self.text_box = None
        self.calc_type = None
        self.history = None
        self.current_line_text = None
        calculator_tab = self.create_calc_tab()

        # create graphing tab
        graphing_tab = self.create_graph_tab()

        # add pane to the tab widget
        tab.addTab(calculator_tab, 'Calculate')
        tab.addTab(graphing_tab, 'Graph')

        main_layout.addWidget(tab, 0, 0, 2, 1)
        self.show()

    def create_calc_tab(self) -> QWidget:
        calc_tab = QWidget(self)
        layout = QVBoxLayout()
        l = QListWidget()
        l.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.history = l
        layout.addWidget(l)

        h_box = QHBoxLayout()
        calc_options = QComboBox(parent=self)
        calc_options.addItems(CalculationOptions)
        self.calc_type = calc_options
        h_box.addWidget(calc_options)

        text_box = QLineEdit(parent=self)
        text_box.setMaximumHeight(25)
        text_box.returnPressed.connect(self.calculate)
        self.text_box = text_box
        h_box.addWidget(text_box)

        layout.addLayout(h_box)
        calc_tab.setLayout(layout)
        return calc_tab

    def create_graph_tab(self) -> QWidget:
        graph_tab = QWidget(self)
        layout = QVBoxLayout()
        graph_tab.setLayout(layout)
        return graph_tab

    def calculate(self):
        mode = self.calc_type.currentText()
        text = self.text_box.text()
        self.text_box.clear()
        if not text:
            return None

        self.history.addItem(text)
        print(text)

        match mode:
            case CalculationOptions.CALCULATE:
                if "," in text:
                    math_expression, variable_data = text.split(",")
                else:
                    math_expression = text
                try:
                    variable_data = {}
                    tree = interpret_text_to_tree(math_expression)
                    result = tree.evaluate(variable_data)
                    self.history.addItem(str(result))
                except Exception as e:
                    print(e)
            case CalculationOptions.DEFINE:
                if "=" not in text:
                    raise ValueError(f"Entered text must contain '=' for {mode=}, {text=}")
                func_name, tree = text.split("=")
                # tree = interpret_text_to_tree(text)
                # func = FunctionNode(name, tree)
                # self.history.addItem(func)
            case CalculationOptions.DIFFERENTIATE:
                # name = "f"
                # func = FunctionNode.DEFINED_FUNCTIONS[name]
                # wrt = "x"
                # diff = func.grad(wrt)
                # self.history.addItem(diff)
                pass
