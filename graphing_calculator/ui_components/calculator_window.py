import re
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
        # l.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
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
        try:
            self._calculate()
        except Exception as e:
            print(e)
            self.history.addItem(f"ERR! {e}")

    def _calculate(self):
        mode = self.calc_type.currentText()
        text = self.text_box.text()
        self.text_box.clear()
        if not text:
            return None

        self.history.addItem(f"{mode} {text}")
        text = text.replace(" ", "")
        match mode:
            case CalculationOptions.CALCULATE:
                if "," in text:
                    math_expression, variable_data = text.split(",")
                    variable_data = re.findall(r"\w+=\d+", variable_data)
                    variable_data = {var.split("=")[0]: float(var.split("=")[1]) for var in variable_data}
                else:
                    math_expression, variable_data = text, None
                at = variable_data or {}
                tree = interpret_text_to_tree(math_expression)
                result = tree.evaluate(at)
                self.history.addItem(str(result))

            case CalculationOptions.DEFINE:
                if "=" not in text:
                    raise ValueError(f"Entered text must contain '=' for {mode=}, {text=}")
                func_name, math_expression = text.split("=")
                tree = interpret_text_to_tree(math_expression)
                func = FunctionNode(func_name, tree)
                self.history.addItem(str(func))

            case CalculationOptions.DIFFERENTIATE:
                if "," not in text:
                    raise ValueError(f"Must include 1 differentiating variable for {mode=}, {text=}")
                name, wrt = text.split(",")
                func = FunctionNode.DEFINED_FUNCTIONS[name]
                diff = func.grad(wrt)
                self.history.addItem(str(diff))
