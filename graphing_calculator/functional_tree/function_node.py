from typing import Optional
from graphing_calculator.functional_tree.nodes import Node, NodeType, UnaryNode, VariableNode


def find_variables(tree: NodeType) -> set[str]:
    if isinstance(tree, VariableNode):
        return  {tree.data}
    elif isinstance(tree, UnaryNode):
        return set()
    else:
        l = find_variables(tree.left)
        r = find_variables(tree.right)
        return l | r


class FunctionNode(Node):

    def __init__(self, name: str, tree: Node):
        self.name = name
        self.tree = tree
        self.input_variables = find_variables(tree)

    def grad(self, wrt: str) -> tuple[NodeType, set[str]]:
        return self.tree.grad(wrt), self.input_variables - {wrt}

    def evaluate(self, at: dict[str, float]) -> float:
        return self.tree.evaluate(at)

    def partial_evaluate(self, at: dict[str, float]) -> tuple[NodeType, set[str]]:
        return self.tree.partial_evaluate(at), self.input_variables - set(at.keys())

    def __str__(self) -> str:
        return f"{self.name} ({", ".join(self.input_variables)})"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name} -> {list(self.input_variables)}>"
