import pytest

from graphing_calculator.functional_tree.nodes import (
    NodeType,
    VariableNode,
    AdditionNode,
    ConstantNode,
    MultiplicationNode,
    ExponentialNode
)
from graphing_calculator.functional_tree.function_node import (
    find_variables,
    FunctionNode,
)

EIGHT = ConstantNode(8)
X = VariableNode("x")
Y = VariableNode("y")
Z = VariableNode("z")
X_AND_Y = AdditionNode(
    AdditionNode(X, EIGHT),
    AdditionNode(Y, EIGHT),
)
X_AND_Y_AND_Z_1 = MultiplicationNode(
    Z,
    X_AND_Y
)
X_AND_Y_AND_Z_2 = ExponentialNode(X_AND_Y_AND_Z_1, ConstantNode(3))

TEST_TREES = {
    EIGHT: set(),
    X: {"x"},
    X_AND_Y: {"x", "y"},
    X_AND_Y_AND_Z_1: {"x", "y", "z"},
    X_AND_Y_AND_Z_2: {"x", "y", "z"},
}


TEST_NAMES = ("tree", "expected_result")


@pytest.mark.parametrize(TEST_NAMES, [(k, v) for k, v in TEST_TREES.items()])
def test_find_variables(tree: NodeType, expected_result):
    assert find_variables(tree) == expected_result


TEST_NAMES_FUNC = ("name", "tree", "expected_result")

TEST_FUNC = {
    ("f", X_AND_Y): {
        "grad": "1",
        "eval": 20,
        "part_eval": "(11 + (y + 8))",
        "str": "f (x, y) = (x + 8) + (y + 8)",
        "repr": f"<FunctionNode: f -> ['x', 'y']> = {repr(X_AND_Y)}"
    },
    ("g", X_AND_Y_AND_Z_1): {
        "grad": "(0 + 1 * z)",
        "eval": 40,
        "part_eval": "z * (11 + (y + 8))",
        "str": "g (x, y, z) = z * ((x + 8) + (y + 8))",
        "repr": f"<FunctionNode: g -> ['x', 'y', 'z']> = {repr(X_AND_Y_AND_Z_1)}"
    }
}


@pytest.mark.parametrize(TEST_NAMES_FUNC, [(*k, v.get("grad")) for k, v in TEST_FUNC.items() if v.get("grad")])
def test_func_node_grad(name: str, tree: NodeType, expected_result):
    assert str(FunctionNode(name, tree).grad("x")) == expected_result


@pytest.mark.parametrize(TEST_NAMES_FUNC, [(*k, v.get("eval")) for k, v in TEST_FUNC.items() if v.get("eval")])
def test_func_node_eval(name: str, tree: NodeType, expected_result):
    assert FunctionNode(name, tree).evaluate({"x": 3, "y": 1, "z": 2}) == expected_result


@pytest.mark.parametrize(TEST_NAMES_FUNC, [(*k, v.get("part_eval")) for k, v in TEST_FUNC.items() if v.get("part_eval")])
def test_func_node_part_val(name: str, tree: NodeType, expected_result):
    assert str(FunctionNode(name, tree).partial_evaluate({"x": 3})) == expected_result


@pytest.mark.parametrize(TEST_NAMES_FUNC, [(*k, v.get("str")) for k, v in TEST_FUNC.items() if v.get("str")])
def test_func_node_str(name: str, tree: NodeType, expected_result):
    assert str(FunctionNode(name, tree)) == expected_result


@pytest.mark.parametrize(TEST_NAMES_FUNC, [(*k, v.get("repr")) for k, v in TEST_FUNC.items() if v.get("repr")])
def test_func_node_repr(name: str, tree: NodeType, expected_result):
    assert repr(FunctionNode(name, tree)) == expected_result
