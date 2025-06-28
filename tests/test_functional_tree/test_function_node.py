import pytest

from graphing_calculator.functional_tree.nodes import (
    NodeType,
    VariableNode,
    AdditionNode,
    ConstantNode,
    MultiplicationNode,
    ExponentialNode
)
from graphing_calculator.functional_tree.function_node import find_variables

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