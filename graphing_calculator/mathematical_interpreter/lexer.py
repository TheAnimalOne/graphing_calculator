import re

from graphing_calculator.functional_tree.nodes import OPERATOR_SYMBOL


NUMBER = r"-?\d*\.{0,1}\d+"
SYMBOLS = r"[+*()-^]"
VARIABLE = r"\w+"
PRECEDENCE = {
    OPERATOR_SYMBOL.EXP.value: (2, "right"),
    OPERATOR_SYMBOL.MULT.value: (1, "left"),
    OPERATOR_SYMBOL.DIV.value: (1, "left"),
    OPERATOR_SYMBOL.ADD.value: (0, "left"),
    OPERATOR_SYMBOL.SUB.value: (0, "left"),
}


def tokeniser(text: str) -> list[str]:
    """Produces tokens from text"""
    tokens = re.findall(f"{NUMBER}|{SYMBOLS}|{VARIABLE}", text)
    return tokens


def check_operator_precedence(op1: str, op2: str) -> bool:
    op1_precedence, op1_associativity = PRECEDENCE[op1]
    op2_precedence, _ = PRECEDENCE[op2]
    if op2_precedence > op1_precedence:
        return True
    return op2_precedence == op1_precedence and op1_associativity == 'left'


def shunting_yard_lexer(tokens: list[str]) -> list[str]:
    """Implementation of shunting yard algorithm to get RPN https://en.wikipedia.org/wiki/Shunting_yard_algorithm"""
    operators = [o.value for o in OPERATOR_SYMBOL]
    output = []
    operator_stack = []
    for token in tokens:
        if re.match(fr"{NUMBER}|{VARIABLE}", token):
            output.append(token)
        elif token in operators:
            while (operator_stack and operator_stack[-1] != "(") and (
                    check_operator_precedence(token, operator_stack[-1])):
                output.append(operator_stack.pop())
            operator_stack.append(token)
        elif token == "(":
            operator_stack.append(token)
        elif token == ")":
            while operator_stack[-1] != "(":
                if not operator_stack:
                    raise ValueError(f"Mismatched parenthesis, left parenthesis not found in operator stack")
                output.append(operator_stack.pop())
            if operator_stack[-1] != "(":
                raise ValueError(f"Mismatched parenthesis, left parenthesis not found in operator stack")\
            # remove l paren
            operator_stack.pop()
        else:
            raise ValueError(f"Unexpected {token=}")
    while operator_stack:
        if operator_stack[-1] == "(":
            raise ValueError(f"Mismatched parenthesis found on operator stack: {operator_stack}")
        output.append(operator_stack.pop())
    return output
