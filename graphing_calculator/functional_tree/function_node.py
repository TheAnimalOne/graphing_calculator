from typing import TypeVar, Optional
from graphing_calculator.functional_tree.nodes import (
    Node,
    NodeType,
    UnaryNode,
    VariableNode,
)


def find_variables(tree: NodeType) -> set[str]:
    if isinstance(tree, VariableNode):
        return {tree.data}
    elif isinstance(tree, UnaryNode):
        return set()
    elif isinstance(tree, FunctionNode):
        return find_variables(tree.tree)
    else:
        l = find_variables(tree.left)
        r = find_variables(tree.right)
        return l | r


FunctionNodeType = TypeVar("FunctionNodeType", bound="FunctionNode")


class FunctionNode(Node):

    DEFINED_FUNCTIONS = {}

    def __init__(self, name: str, tree: Node, input_variables: Optional[set[str]] = None):
        self.name = name
        self.tree = tree
        self.input_variables = input_variables or find_variables(tree)
        self.DEFINED_FUNCTIONS[name] = self

    def grad(self, wrt: str) -> NodeType:
        return self.tree.grad(wrt)

    def evaluate(self, at: dict[str, float]) -> float:
        return self.tree.evaluate(at)

    def partial_evaluate(self, at: dict[str, float]) -> NodeType:
        return self.tree.partial_evaluate(at)

    def __str__(self) -> str:
        tree_str = str(self.tree)
        if tree_str.startswith("(") and tree_str.endswith(")"):
            return f"{self.name} ({', '.join(sorted(self.input_variables))}) = {tree_str[1:-1]}"
        else:
            return f"{self.name} ({', '.join(sorted(self.input_variables))}) = {tree_str}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name} -> {list(sorted(self.input_variables))}> = {repr(self.tree)}"
