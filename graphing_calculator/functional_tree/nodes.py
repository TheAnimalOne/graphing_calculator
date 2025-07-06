from typing import TypeVar
from abc import ABC, abstractmethod
from enum import StrEnum

NodeType = TypeVar("NodeType", bound="Node")


class OperatorSymbol(StrEnum):
    ADD = "+"
    SUB = "-"
    MULT = "*"
    DIV = "/"
    EXP = "^"


class Node(ABC):
    """General Node class, all `Node`s are expected to calculate a value, partially calculate and find gradient"""
    @abstractmethod
    def grad(self, wrt: str) -> NodeType:
        """Calculate the derivative of the current node, with respect to (wrt) given variable"""
        pass

    @abstractmethod
    def evaluate(self, at: dict[str, float]) -> float:
        """Calculate the value of the node, expects all input variables to have value in `at`"""
        pass

    @abstractmethod
    def partial_evaluate(self, at: dict[str, float]) -> NodeType:
        """Partially calculate, filling in all given variables with constants in `at`"""
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass


class UnaryNode(Node, ABC):
    """General class for Node with 1 input"""
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {repr(self.data)}>"


class BinaryOpNode(Node, ABC):
    """General class for Node with 2 inputs"""
    SYMBOL = ""

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return f"{str(self.left)} {self.SYMBOL} {str(self.right)}"

    def __repr__(self):
        return f"<{self.__class__.__name__}: {repr(self.left)}, {repr(self.right)}>"


class ConstantNode(UnaryNode):
    """data = float value"""

    def grad(self, wrt) -> NodeType:
        """Gradient const -> 0"""
        return ConstantNode(0)

    def evaluate(self, at) -> float:
        return self.data

    def partial_evaluate(self, at) -> NodeType:
        return ConstantNode(self.data)


class VariableNode(UnaryNode):
    """data = variable name"""

    def grad(self, wrt) -> NodeType:
        """Gradient x -> 1 if w.r.t. x else 0 """
        if self.data == wrt:
            return ConstantNode(1)
        else:
            return ConstantNode(0)

    def evaluate(self, at) -> float:
        return at[self.data]

    def partial_evaluate(self, at) -> NodeType:
        value_or_none = at.get(self.data)
        return ConstantNode(value_or_none) if value_or_none else VariableNode(self.data)


class AdditionNode(BinaryOpNode):
    """left = f(x), right = g(x)"""
    SYMBOL = OperatorSymbol.ADD

    def grad(self, wrt) -> NodeType:
        """Gradient f(x) + g(x) -> f'(x) + g'(x)"""
        l = self.left.grad(wrt)
        r = self.right.grad(wrt)
        if isinstance(l, ConstantNode) and isinstance(r, ConstantNode):
            return ConstantNode(l.data + r.data)
        return AdditionNode(l, r)

    def evaluate(self, at: dict[str, float]) -> float:
        return self.left.evaluate(at) + self.right.evaluate(at)

    def partial_evaluate(self, at: dict[str, float]) -> NodeType:
        l = self.left.partial_evaluate(at)
        r = self.right.partial_evaluate(at)
        if isinstance(l, ConstantNode) and isinstance(r, ConstantNode):
            return ConstantNode(l.data + r.data)
        return AdditionNode(l, r)

    def __str__(self):
        return f"({super().__str__()})"


class SubtractionNode(BinaryOpNode):
    """left = f(x), right = g(x)"""
    SYMBOL = OperatorSymbol.SUB

    def grad(self, wrt) -> NodeType:
        """Gradient f(x) - g(x) -> f'(x) - g'(x)"""
        l = self.left.grad(wrt)
        r = self.right.grad(wrt)
        if isinstance(l, ConstantNode) and isinstance(r, ConstantNode):
            return ConstantNode(l.data - r.data)
        return SubtractionNode(l, r)

    def evaluate(self, at: dict[str, float]) -> float:
        return self.left.evaluate(at) - self.right.evaluate(at)

    def partial_evaluate(self, at: dict[str, float]) -> NodeType:
        l = self.left.partial_evaluate(at)
        r = self.right.partial_evaluate(at)
        if isinstance(l, ConstantNode) and isinstance(r, ConstantNode):
            return ConstantNode(l.data - r.data)
        return SubtractionNode(l, r)

    def __str__(self):
        return f"({super().__str__()})"


class MultiplicationNode(BinaryOpNode):
    """left = f(x), right = g(x)"""
    SYMBOL = OperatorSymbol.MULT

    def grad(self, wrt) -> NodeType:
        """Gradient f(x) * g(x) -> f'(x) * g(x) + f(x) * g'(x)"""
        f_grad = self.left.grad(wrt)
        if isinstance(f_grad, ConstantNode) and isinstance(self.right, ConstantNode):
            f_grad_g = ConstantNode(f_grad.data * self.right.data)
        elif isinstance(f_grad, ConstantNode) and f_grad.data == 0:
            f_grad_g = ConstantNode(0)
        elif isinstance(self.right, ConstantNode) and self.right.data == 0:
            f_grad_g = ConstantNode(0)
        else:
            f_grad_g = MultiplicationNode(f_grad, self.right)

        g_grad = self.right.grad(wrt)
        if isinstance(g_grad, ConstantNode) and isinstance(self.left, ConstantNode):
            g_grad_f = ConstantNode(g_grad.data * self.left.data)
        elif isinstance(g_grad, ConstantNode) and g_grad.data == 0:
            g_grad_f = ConstantNode(0)
        elif isinstance(self.left, ConstantNode) and self.left.data == 0:
            g_grad_f = ConstantNode(0)
        else:
            g_grad_f = MultiplicationNode(g_grad, self.left)

        if isinstance(f_grad_g, ConstantNode) and isinstance(g_grad_f, ConstantNode):
            return ConstantNode(f_grad_g.data + g_grad_f.data)
        return AdditionNode(f_grad_g, g_grad_f)

    def evaluate(self, at: dict[str, float]) -> float:
        return self.left.evaluate(at) * self.right.evaluate(at)

    def partial_evaluate(self, at: dict[str, float]) -> NodeType:
        l = self.left.partial_evaluate(at)
        r = self.right.partial_evaluate(at)
        if isinstance(l, ConstantNode) and l.data == 0:
            return ConstantNode(0)
        elif isinstance(r, ConstantNode) and r.data == 0:
            return ConstantNode(0)
        elif isinstance(l, ConstantNode) and isinstance(r, ConstantNode):
            return ConstantNode(l.data * r.data)
        else:
            return MultiplicationNode(l, r)


class DivisionNode(BinaryOpNode):
    """left = f(x), right = g(x)"""
    SYMBOL = OperatorSymbol.DIV

    def grad(self, wrt) -> NodeType:
        """Gradient f(x) / g(x) -> (f'(x) * g(x) - f(x) * g'(x)) / (g(x))^2"""
        f_grad = self.left.grad(wrt)
        if isinstance(f_grad, ConstantNode) and isinstance(self.right, ConstantNode):
            f_grad_g = ConstantNode(f_grad.data * self.right.data)
        elif isinstance(f_grad, ConstantNode) and f_grad.data == 0:
            f_grad_g = ConstantNode(0)
        elif isinstance(self.right, ConstantNode) and self.right.data == 0:
            f_grad_g = ConstantNode(0)
        else:
            f_grad_g = MultiplicationNode(f_grad, self.right)

        g_grad = self.right.grad(wrt)
        if isinstance(g_grad, ConstantNode) and isinstance(self.left, ConstantNode):
            g_grad_f = ConstantNode(g_grad.data * self.left.data)
        elif isinstance(g_grad, ConstantNode) and g_grad.data == 0:
            g_grad_f = ConstantNode(0)
        elif isinstance(self.left, ConstantNode) and self.left.data == 0:
            g_grad_f = ConstantNode(0)
        else:
            g_grad_f = MultiplicationNode(g_grad, self.left)

        if isinstance(f_grad_g, ConstantNode) and isinstance(g_grad_f, ConstantNode):
            numerator = ConstantNode(f_grad_g.data - g_grad_f.data)
        else:
            numerator =  SubtractionNode(f_grad_g, g_grad_f)

        if isinstance(self.right, ConstantNode):
            denominator = ConstantNode(self.right.data ** 2)
        else:
            denominator = ExponentialNode(self.right, ConstantNode(2))

        if isinstance(numerator, ConstantNode) and isinstance(denominator, ConstantNode):
            return ConstantNode(numerator.data / denominator.data)
        return DivisionNode(numerator, denominator)

    def evaluate(self, at: dict[str, float]) -> float:
        denominator = self.right.evaluate(at)
        if denominator == 0:
            raise ZeroDivisionError(f"Cannot compute {self.left} / {self.right}")
        return self.left.evaluate(at) / denominator

    def partial_evaluate(self, at: dict[str, float]) -> NodeType:
        l = self.left.partial_evaluate(at)
        r = self.right.partial_evaluate(at)
        if isinstance(l, ConstantNode) and isinstance(r, ConstantNode):
            return ConstantNode(l.data / r.data)
        return DivisionNode(l, r)


class ExponentialNode(BinaryOpNode):
    """left = f(x), right = n"""
    SYMBOL = OperatorSymbol.EXP

    def grad(self, wrt) -> NodeType:
        """Gradient f(x) ^ n -> n * f'(x) * (f(x))^(n-1)"""
        n = self.right.data
        f_grad = self.left.grad(wrt)
        if isinstance(f_grad, ConstantNode):
            l = ConstantNode(n * f_grad.data)
        else:
            l = MultiplicationNode(ConstantNode(n), f_grad)

        if n-1 == 0:
            r = ConstantNode(1)
        elif n-1 == 1:
            r = self.left
        else:
            r = ExponentialNode(self.left, ConstantNode(n - 1))
        if isinstance(l, ConstantNode) and isinstance(r, ConstantNode):
            return ConstantNode(l.data ** r.data)
        return MultiplicationNode(l, r)

    def evaluate(self, at: dict[str, float]) -> float:
        return self.left.evaluate(at) ** self.right.evaluate(at)

    def partial_evaluate(self, at: dict[str, float]) -> NodeType:
        l = self.left.partial_evaluate(at)
        r = self.right.partial_evaluate(at)
        if isinstance(l, ConstantNode) and isinstance(r, ConstantNode):
            return ConstantNode(l.data ** r.data)
        return ExponentialNode(l, r)
