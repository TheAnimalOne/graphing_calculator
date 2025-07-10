import re
from enum import StrEnum
from numpy import linspace

import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QLabel,
    QTabWidget,
    QLineEdit,
    QWidget,
    QComboBox,
    QListWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QGridLayout,
)
from graphing_calculator.functional_tree.function_node import FunctionNode, find_variables
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
        self.plot_graph = None
        self.func_options = None
        self.var_options = None
        self.x_min = None
        self.x_max = None
        self.plot_button = None
        self.clear_button = None
        self.current_x = None
        graphing_tab = self.create_graph_tab()

        tab.addTab(calculator_tab, 'Calculate')
        tab.addTab(graphing_tab, 'Graph')

        main_layout.addWidget(tab, 0, 0, 2, 1)
        self.show()

    def create_calc_tab(self) -> QWidget:
        calc_tab = QWidget(self)
        layout = QVBoxLayout()
        l = QListWidget()
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
        self.plot_graph = pg.PlotWidget()
        self.plot_graph.showGrid(x=True, y=True)
        layout.addWidget(self.plot_graph)
        graph_info_layout = QVBoxLayout()

        # choose func
        func_layout = QHBoxLayout()
        func_options = QComboBox(parent=self)
        func_options.addItems(FunctionNode.DEFINED_FUNCTIONS.keys())
        self.func_options = func_options
        func_layout.addWidget(QLabel("function name:"))
        func_layout.addWidget(func_options)
        graph_info_layout.addLayout(func_layout)

        # choose x axis variable
        x_layout = QHBoxLayout()
        variables = [f.input_variables for f in FunctionNode.DEFINED_FUNCTIONS.values()]
        variables = list(set().union(*variables))
        var_options = QComboBox(parent=self)
        var_options.addItems(variables)
        self.var_options = var_options
        x_layout.addWidget(QLabel("x-axis variable name:"))
        x_layout.addWidget(var_options)
        graph_info_layout.addLayout(x_layout)

        # plot func range
        x_range_layout = QHBoxLayout()
        x_range_layout.addWidget(QLabel("plot range: "))
        x_range_layout.addWidget(QLabel("min"))
        x_min_value = QLineEdit(parent=self)
        self.x_min = x_min_value
        x_range_layout.addWidget(x_min_value)
        x_range_layout.addWidget(QLabel("max"))
        x_max_value = QLineEdit(parent=self)
        self.x_max = x_max_value
        x_range_layout.addWidget(x_max_value)
        graph_info_layout.addLayout(x_range_layout)

        # buttons
        buttons_layout = QHBoxLayout()
        plot_button = QPushButton("Plot Graph")
        self.plot_button = plot_button
        plot_button.pressed.connect(self.add_plot_to_graph)
        buttons_layout.addWidget(plot_button)

        # clear button
        clear_button = QPushButton("Clear Graphs")
        self.clear_button = clear_button
        clear_button.pressed.connect(self.clear_graph)
        buttons_layout.addWidget(clear_button)
        graph_info_layout.addLayout(buttons_layout)
        layout.addLayout(graph_info_layout)

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
                result = tree.evaluate(at) if set(at.keys()) == find_variables(tree) else tree.partial_evaluate(at)
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
                diff_func = FunctionNode(f"{func.name}_x", diff)
                self.history.addItem(str(diff_func))

        self.refresh_widgets()

    def add_plot_to_graph(self):
        func_name = self.func_options.currentText()
        func = FunctionNode.DEFINED_FUNCTIONS[func_name]
        x_var = self.var_options.currentText()
        if func.input_variables and x_var not in func.input_variables:
            raise ValueError(f"Cannot plot {x_var} for {func_name}")
        if self.current_x is not None and self.current_x != x_var:
            self.clear_graph()
        min_val, max_val = float(self.x_min.text()), float(self.x_max.text())
        xs = linspace(min_val, max_val, 100_000)
        ys = [func.evaluate({x_var: x}) for x in xs]
        self.plot_graph.plot(xs, ys)
        self.current_x = x_var

    def clear_graph(self):
        if self.plot_graph is not None:
            self.plot_graph.clear()

    def refresh_widgets(self):
        if self.func_options is not None:
            self.func_options.clear()
            self.func_options.addItems(FunctionNode.DEFINED_FUNCTIONS.keys())

        if self.var_options is not None:
            variables = [f.input_variables for f in FunctionNode.DEFINED_FUNCTIONS.values()]
            variables = list(set().union(*variables))
            self.var_options.clear()
            self.var_options.addItems(variables)