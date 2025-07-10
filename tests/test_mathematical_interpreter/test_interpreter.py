import pytest

from graphing_calculator.mathematical_interpreter.interpreter import (
    tokeniser,
    shunting_yard_lexer,
    parse_rpn_to_functional_tree,
    interpret_text_to_tree,
)


TEST_NAMES_LEXER = "input_text, expected_result"
TEST_TOKENISER = [
    "21 + 3423 + 34324.342412 + 33423412.145123432134 + x",
    "3 ^ 1233.2 * 4753 + 123 + -3213.2",
    "adf2 + dsf31 - sA3asd / 23123.2131 * 23123.2",
    "( ( 20 - 10 ) * ( 30 - 20 ) / 10 + 10 ) * 2",
    "3 * 10 - 1000",
]
TEST_LEXER = {
    "3 + 4 * 2 / ( 1 - 5 ) ^ 2 ^ 3": "3 4 2 * 1 5 - 2 3 ^ ^ / +".split(" "),
    "( ( 20 - 10 ) * ( 30 - 20 ) / 10 + 10 ) * 2": "20 10 - 30 20 - * 10 / 10 + 2 *".split(" "),
}
TEST_LEXER_FAIL = [
    "( ( ( ( 3 ) ) ) ) )",
    "( ( ( ( 3 ) ) ) ) (",
    " + + + + ) ) ) ) (",
    "!@# $@# %^",
]


TEST_NAMES_PARSER = "rpn, expected_result"
TEST_PARSER = {
    "x 3 +": 6,
    "3 4 2 * 1 5 - 2 3 ^ ^ / +": 3.0001220703125,
    "x 4 2 * 1 5 - 2 x ^ ^ / +": 3.0001220703125, # check works with variable
    "20 10 - 30 20 - * 10 / 10 + 2 *": 40,
    "20 10 - 30 20 - * 10 / 10 + x 1 - *": 40, # check works with variable
}


TEST_NAMES_INTERPRET = "math_expression, expected_result"
TEST_INTERPRETER = [
    "x^3 + 3*x^2 + 3*x + 1",
    "32+2+17/31/3*2134",
    "x ^ x",
    "x * x - x ^ 2",
    "x*x-x^2",
    "x*(x-x)^2",
    "x^(3+3)*x^(2+3)*(x+1)",
    "3 *10 - 1000",
    "12 / 2 + 3 * 11 - 20",
    "17 - 36 / 6 + 5 * 12",
    "11 + 12 * 5 - 11",
    "4 + 8 - 14 / 2",
    "14 + 96 / 8 * 3 - 5",
    "6 + 12 - 4 * 4",
    "-3 * (4 + 6)",
    "(9 + 6) * (2 - 3) + 5^2",
    "8 / 4 * (6 + 2 / 4) + 32 - 2",
    "0.34 / 1.7 + 45 * 2",
    "15 + 9 / 6 - 4",
    "24 - 17 * 8 - 16",
    "7 + 6 * (12 - 7)",
    "(7^2 + 11) / 5",
    "-2 + (5 * -3) - (-6 / 2)",
]


@pytest.mark.parametrize(TEST_NAMES_LEXER, [(v, v.split(" ")) for v in TEST_TOKENISER])
def test_tokeniser(input_text: str, expected_result: list[str]):
    assert tokeniser(input_text) == expected_result


@pytest.mark.parametrize(TEST_NAMES_LEXER, [(k.split(" "), v) for k, v in TEST_LEXER.items()])
def test_shunting_yard_lexer(input_text: list[str], expected_result: list[str]):
    assert shunting_yard_lexer(input_text) == expected_result


@pytest.mark.parametrize("input_text", [txt.split(" ") for txt in TEST_LEXER_FAIL])
def test_shunting_yard_lexer_fail(input_text: list[str]):
    with pytest.raises(Exception):
        shunting_yard_lexer(input_text)


@pytest.mark.parametrize(TEST_NAMES_PARSER, TEST_PARSER.items())
def test_parse_rpn_to_functional_tree(rpn: str, expected_result: float):
    tree =  parse_rpn_to_functional_tree(rpn.split(" "))
    assert tree.evaluate({"x": 3}) == expected_result


@pytest.mark.parametrize(
    TEST_NAMES_INTERPRET,
    [(txt, eval(txt.replace("x", "3").replace("^", "**"))) for txt in TEST_INTERPRETER]
)
def test_interpret_text_to_tree(math_expression: str, expected_result: float):
    tree = interpret_text_to_tree(math_expression)
    assert tree.evaluate({"x": 3}) == expected_result
