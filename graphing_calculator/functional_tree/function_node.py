from typing import TypeVar
from graphing_calculator.functional_tree.nodes import Node, NodeType, UnaryNode, VariableNode


def find_variables(tree: NodeType) -> set[str]:
    if isinstance(tree, VariableNode):
        return {tree.data}
    elif isinstance(tree, UnaryNode):
        return set()
    else:
        l = find_variables(tree.left)
        r = find_variables(tree.right)
        return l | r


FunctionNodeType = TypeVar("FunctionNodeType", bound="FunctionNode")


class FunctionNode(Node):

    def __init__(self, name: str, tree: Node, input_variables: set[str]):
        self.name = name
        self.tree = tree
        self.input_variables = input_variables or find_variables(tree)

    def grad(self, wrt: str) -> FunctionNodeType:
        return FunctionNode(
            self.name + "'",
            self.tree.grad(wrt),
            self.input_variables - {wrt}
        )

    def evaluate(self, at: dict[str, float]) -> float:
        return self.tree.evaluate(at)

    def partial_evaluate(self, at: dict[str, float]) -> FunctionNodeType:
        return FunctionNode(
            self.name + "1",
            self.tree.partial_evaluate(at),
            self.input_variables - set(at.keys()),
        )

    def __str__(self) -> str:
        tree_str = str(self.tree)
        if tree_str.startswith("(") and tree_str.endswith(")"):
            return f"{self.name} ({', '.join(self.input_variables)}) = {tree_str[1:-1]}"
        else:
            return f"{self.name} ({', '.join(self.input_variables)}) = {tree_str}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name} -> {list(self.input_variables)}> = {repr(self.tree)}"
