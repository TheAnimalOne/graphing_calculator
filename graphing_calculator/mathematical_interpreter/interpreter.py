import re

from graphing_calculator.functional_tree.nodes import (
    NodeType,
    OperatorSymbol,
    ConstantNode,
    VariableNode,
    AdditionNode,
    SubtractionNode,
    MultiplicationNode,
    DivisionNode,
    ExponentialNode,
)


NUMBER = r"-?\d*\.{0,1}\d+"
SYMBOLS = r"[+*()-^]"
VARIABLE = r"\w+"
PRECEDENCE = {
    OperatorSymbol.EXP: (2, "right"),
    OperatorSymbol.MULT: (1, "left"),
    OperatorSymbol.DIV: (1, "left"),
    OperatorSymbol.ADD: (0, "left"),
    OperatorSymbol.SUB: (0, "left"),
}
NODE_BY_OPERATOR = {
    OperatorSymbol.EXP: ExponentialNode,
    OperatorSymbol.MULT: MultiplicationNode,
    OperatorSymbol.DIV: DivisionNode,
    OperatorSymbol.ADD: AdditionNode,
    OperatorSymbol.SUB: SubtractionNode,
}


def tokeniser(text: str) -> list[str]:
    """Produces tokens from text"""
    tokens = re.findall(f"{NUMBER}|{SYMBOLS}|{VARIABLE}", text)
    return tokens


def check_operator_precedence(op1: OperatorSymbol, op2: OperatorSymbol) -> bool:
    """Check operator precedence, taking into account the associativity"""
    op1_precedence, op1_associativity = PRECEDENCE[op1]
    op2_precedence, _ = PRECEDENCE[op2]
    if op2_precedence > op1_precedence:
        return True
    return op2_precedence == op1_precedence and op1_associativity == 'left'


def shunting_yard_lexer(tokens: list[str | OperatorSymbol]) -> list[str]:
    """Implementation of shunting yard algorithm to get RPN https://en.wikipedia.org/wiki/Shunting_yard_algorithm"""
    operators = [o for o in OperatorSymbol]
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
                raise ValueError(f"Mismatched parenthesis, left parenthesis not found in operator stack")
            # remove l paren
            operator_stack.pop()
        else:
            raise ValueError(f"Unexpected {token=}")
    while operator_stack:
        if operator_stack[-1] == "(":
            raise ValueError(f"Mismatched parenthesis found on operator stack: {operator_stack}")
        output.append(operator_stack.pop())
    return output


def parse_rpn_to_functional_tree(output_rpn: list[str]) -> NodeType:
    """Parses an expression in RPN form into a Node Tree"""
    output = []
    for token in output_rpn:
        if re.match(NUMBER, token):
            node = ConstantNode(float(token))
        elif re.match(VARIABLE, token):
            node =  VariableNode(token)
        elif re.match(SYMBOLS, token):
            r_node = output.pop()
            l_node = output.pop()
            node = NODE_BY_OPERATOR[token](l_node, r_node)
        else:
            raise ValueError(f"Failure to parse {token=}")
        output.append(node)
    if len(output) == 1:
        return output[0]
    raise ValueError(f"Parse failure for {output_rpn=}, final stack position is {output=}")


def interpret_text_to_tree(mathematical_expression: str) -> NodeType:
    """Interprets a mathematical expression as a Node Tree"""
    tokens = tokeniser(mathematical_expression)
    rpn = shunting_yard_lexer(tokens)
    tree = parse_rpn_to_functional_tree(rpn)
    return tree
