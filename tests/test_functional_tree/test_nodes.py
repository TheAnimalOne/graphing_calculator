import pytest
from typing import Any

from graphing_calculator.functional_tree.nodes import (
    NodeType,
    UnaryNode,
    BinaryOpNode,
    ConstantNode,
    VariableNode,
    AdditionNode,
    SubtractionNode,
    MultiplicationNode,
    DivisionNode,
    ExponentialNode,
)


def create_values(const: dict[NodeType, dict[str, Any]], key: str) -> list[tuple]:
    return [
        (node, res) for node, exp_results in const.items() if (res:=exp_results.get(key)) is not None
    ]

# tests constants
TEST_NAMES = "node, exp_result"
UNARY_NODE_TEST_VALUES = {
    ConstantNode(7): {
        "grad": 0,
        "eval": 7,
        "part_val": 7,
        "str": "7",
        "repr": "<ConstantNode: 7>"
    },
    ConstantNode(1000): {
        "grad": 0,
        "eval": 1000,
        "part_val": 1000,
        "str": "1000",
        "repr": "<ConstantNode: 1000>"
    },
    VariableNode("x"): {
        "grad": 1,
        "eval": 3,
        "part_val": 3,
        "str": "x",
        "repr": "<VariableNode: 'x'>"
    },
    VariableNode("y"): {
        "grad": 0,
        # NOTE: cannot eval for y wrt x
        # "eval": 3,
        "part_val": "y",
        "str": "y",
        "repr": "<VariableNode: 'y'>"
    },
}

BINARY_NODE_TEST_VALUES = {
    AdditionNode(VariableNode("x"), ConstantNode(7)): {
        "grad": "1",
        "eval": 10,
        "part_val": "10",
        "str": "(x + 7)",
        "repr": "<AdditionNode: <VariableNode: 'x'>, <ConstantNode: 7>>"
    },
    SubtractionNode(VariableNode("x"), ConstantNode(7)): {
        "grad": "1",
        "eval": -4,
        "part_val": "-4",
        "str": "(x - 7)",
        "repr": "<SubtractionNode: <VariableNode: 'x'>, <ConstantNode: 7>>"
    },
    MultiplicationNode(VariableNode("x"), ConstantNode(7)): {
        "grad": "7",
        "eval": 21,
        "part_val": "21",
        "str": "x * 7",
        "repr": "<MultiplicationNode: <VariableNode: 'x'>, <ConstantNode: 7>>"
    },
    DivisionNode(VariableNode("x"), ConstantNode(7)): {
        "grad": str(1/7),
        "eval": 3/7,
        "part_val": str(3/7),
        "str": "x / 7",
        "repr": "<DivisionNode: <VariableNode: 'x'>, <ConstantNode: 7>>"
    },
    ExponentialNode(VariableNode("x"), ConstantNode(7)): {
        "grad": "7 * x ^ 6",
        "eval": 3 ** 7,
        "part_eval": str(3 ** 7),
        "str": "x ^ 7",
        "repr": "<ExponentialNode: <VariableNode: 'x'>, <ConstantNode: 7>>"
    },
    AdditionNode(VariableNode("x"), VariableNode("z")): {
        "grad": "1",
        "eval": 2,
        "part_val": "(3 + z)",
        "str": "(x + z)",
        "repr": "<AdditionNode: <VariableNode: 'x'>, <VariableNode: 'z'>>"
    },
    AdditionNode(VariableNode("x"), AdditionNode(VariableNode("z"), ConstantNode(7))): {
        "grad": "1",
        "eval": 9,
        "part_val": "(3 + (z + 7))",
        "str": "(x + (z + 7))",
    },
    ExponentialNode(AdditionNode(
        MultiplicationNode(ConstantNode(3), VariableNode("x")),
        ConstantNode(7)), ConstantNode(2)): {
        "grad": "6 * (3 * x + 7)",
        "eval": 256,
        "part_val": "256",
        "str": "(3 * x + 7) ^ 2",
    },
    ExponentialNode(AdditionNode(
        MultiplicationNode(ConstantNode(3), VariableNode("x")),
        ConstantNode(7)), ConstantNode(-1)): {
        "grad": "-3 * (3 * x + 7) ^ -2",
        "eval": 1/16,
        "str": "(3 * x + 7) ^ -1",
    },
}


@pytest.mark.parametrize(TEST_NAMES, create_values(UNARY_NODE_TEST_VALUES, "grad"))
def test_grad_unary_node(node: UnaryNode, exp_result):
    assert node.grad("x").data == exp_result


@pytest.mark.parametrize(TEST_NAMES, create_values(UNARY_NODE_TEST_VALUES, "part_val"))
def test_part_eval_unary_node(node: UnaryNode, exp_result):
    assert node.partial_evaluate({"x": 3}).data == exp_result


@pytest.mark.parametrize(TEST_NAMES, create_values(BINARY_NODE_TEST_VALUES, "grad"))
def test_grad_binary_node(node: BinaryOpNode, exp_result):
    assert str(node.grad("x")) == exp_result


@pytest.mark.parametrize(TEST_NAMES, create_values(BINARY_NODE_TEST_VALUES, "part_val"))
def test_part_eval_binary_node(node: BinaryOpNode, exp_result):
    assert str(node.partial_evaluate({"x": 3})) == exp_result


@pytest.mark.parametrize(
    TEST_NAMES,
    create_values({**UNARY_NODE_TEST_VALUES, **BINARY_NODE_TEST_VALUES}, "eval")
)
def test_eval_unary_node(node: UnaryNode, exp_result):
    assert node.evaluate({"x": 3, "z": -1}) == exp_result


@pytest.mark.parametrize(
    TEST_NAMES,
    create_values({**UNARY_NODE_TEST_VALUES, **BINARY_NODE_TEST_VALUES}, "str")
)
def test_str_node(node: UnaryNode, exp_result):
    assert str(node) == exp_result


@pytest.mark.parametrize(
    TEST_NAMES,
    create_values({**UNARY_NODE_TEST_VALUES, **BINARY_NODE_TEST_VALUES}, "repr")
)
def test_repr_node(node: UnaryNode, exp_result):
    assert repr(node) == exp_result
