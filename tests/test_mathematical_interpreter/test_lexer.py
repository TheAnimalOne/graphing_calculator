import pytest

from graphing_calculator.mathematical_interpreter.lexer import tokeniser, shunting_yard_lexer


TEST_NAMES = "input_text, expected_result"
TEST_TOKENISER = [
    "21 + 3423 + 34324.342412 + 33423412.145123432134 + x",
    "3 ^ 1233.2 * 4753 + 123 + -3213.2",
    "adf2 + dsf31 - sA3asd / 23123.2131 * 23123.2"
]
TEST_LEXER = {
    "3 + 4 * 2 / ( 1 - 5 ) ^ 2 ^ 3": "3 4 2 * 1 5 - 2 3 ^ ^ / +"
}

@pytest.mark.parametrize(TEST_NAMES, [(v, v.split(" ")) for v in TEST_TOKENISER])
def test_tokeniser(input_text: str, expected_result: list[str]):
    assert tokeniser(input_text) == expected_result

@pytest.mark.parametrize(TEST_NAMES, [(k.split(" "), v.split(" ")) for k, v in TEST_LEXER.items()])
def test_shunting_yard_lexer(input_text: list[str], expected_result: list[str]):
    assert shunting_yard_lexer(input_text) == expected_result
