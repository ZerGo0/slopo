from pathlib import Path
from textwrap import dedent

from slopo.indexing.parsing.lang.python import parse

from .conftest import unit_at_line

FIXTURES = Path(__file__).parent / "fixtures" / "python"


def test_strips_comments_and_docstring():
    unit = parse((FIXTURES / "Comments.py").read_bytes())[0]

    assert unit.start_line == 1
    assert unit.end_line == 6
    assert unit.context == "def with_comments(a, b):"
    assert unit.body_node_count == 16
    assert unit.body == dedent(
        """\
        total = a + b
        url = "http://example.com/#section"

        return total"""
    )


def test_body_node_count_across_body_shapes():
    body_sizes = parse((FIXTURES / "BodySizes.py").read_bytes())

    stub = unit_at_line(body_sizes, 1)
    assert stub.body_node_count == 3

    empty = unit_at_line(body_sizes, 4)
    assert empty.body_node_count == 2

    fibonacci = unit_at_line(body_sizes, 8)
    assert fibonacci.body_node_count == 38


def test_extracts_blocks_with_enclosing_function():
    functions = parse((FIXTURES / "Functions.py").read_bytes())

    classify = unit_at_line(functions, 8)
    assert classify.end_line == 14
    assert classify.kind == "function"
    assert classify.context == "def classify(n):"
    assert classify.body == dedent(
        """\
        if n < 0:
            return "negative"
        elif n == 0:
            return "zero"
        else:
            return "positive\""""
    )

    if_branch = unit_at_line(functions, 9)
    assert if_branch.end_line == 10
    assert if_branch.kind == "block"
    assert if_branch.context == "if n < 0:"
    assert if_branch.body == 'return "negative"'

    elif_branch = unit_at_line(functions, 11)
    assert elif_branch.end_line == 12
    assert elif_branch.kind == "block"
    assert elif_branch.context == "elif n == 0:"
    assert elif_branch.body == 'return "zero"'

    else_branch = unit_at_line(functions, 13)
    assert else_branch.end_line == 14
    assert else_branch.kind == "block"
    assert else_branch.context == "else:"
    assert else_branch.body == 'return "positive"'


def test_extracts_functions():
    functions = parse((FIXTURES / "Functions.py").read_bytes())

    greet = unit_at_line(functions, 4)
    assert greet.end_line == 5
    assert greet.context == "def greet(name):"
    assert greet.body == 'return f"{prefix}, {name}!"'

    sum_evens = unit_at_line(functions, 17)
    assert sum_evens.end_line == 18
    assert sum_evens.context == "def sum_evens(numbers):"
    assert sum_evens.body == "return sum(x for x in numbers if x % 2 == 0)"

    init = unit_at_line(functions, 32)
    assert init.end_line == 33
    assert init.context == "def __init__(self, start=0):"
    assert init.body == "self.value = start"

    increment = unit_at_line(functions, 35)
    assert increment.end_line == 37
    assert increment.context == "def increment(self, by=1):"
    assert increment.body == dedent(
        """\
        self.value += by
        return self.value"""
    )


def test_extracts_decorated_function_with_decorator_in_context():
    functions = parse((FIXTURES / "Functions.py").read_bytes())

    decorated = unit_at_line(functions, 25)
    assert decorated.end_line == 28
    assert decorated.context == dedent(
        """\
        @_identity
        def decorated(items):"""
    )
    assert decorated.body == dedent(
        """\
        total = sum(items)
        return total * 2"""
    )


def test_extracts_nested_function_alongside_enclosing_function():
    nested = parse((FIXTURES / "Nested.py").read_bytes())

    make_adder = unit_at_line(nested, 1)
    assert make_adder.end_line == 5
    assert make_adder.context == "def make_adder(base):"
    assert make_adder.body == dedent(
        """\
        def add(x):
            return base + x

        return add"""
    )

    add = unit_at_line(nested, 2)
    assert add.end_line == 3
    assert add.context == "def add(x):"
    assert add.body == "return base + x"


def test_extracts_lambdas_with_full_body_and_context():
    lambdas = parse((FIXTURES / "Lambdas.py").read_bytes())

    assert len(lambdas) == 6

    doubler = unit_at_line(lambdas, 2)
    assert doubler.end_line == 2
    assert doubler.kind == "function"
    assert doubler.context == "doubler = lambda x:"
    assert doubler.body == "x * 2"

    filter_lambda = unit_at_line(lambdas, 3)
    assert filter_lambda.end_line == 3
    assert filter_lambda.kind == "function"
    assert filter_lambda.context == "filter lambda x:"
    assert filter_lambda.body == "x > 0"

    sorted_lambda = unit_at_line(lambdas, 4)
    assert sorted_lambda.end_line == 4
    assert sorted_lambda.kind == "function"
    assert sorted_lambda.context == "sorted lambda x:"
    assert sorted_lambda.body == "-x"

    classify = unit_at_line(lambdas, 8)
    assert classify.end_line == 12
    assert classify.kind == "function"
    assert classify.context == "classify = lambda x:"
    assert classify.body == dedent(
        """\
        (
            "high" if x > 90
            else "mid" if x > 50
            else "low"
        )"""
    )

    extract = unit_at_line(lambdas, 14)
    assert extract.end_line == 18
    assert extract.kind == "function"
    assert extract.context == "extract = lambda items:"
    assert extract.body == dedent(
        """\
        [
            x * 2
            for x in items
            if x > 0
        ]"""
    )


def test_extracts_conditional_branches_with_full_body_and_context():
    conditionals = parse((FIXTURES / "Conditionals.py").read_bytes())

    assert len(conditionals) == 8

    if_branch = unit_at_line(conditionals, 3)
    assert if_branch.end_line == 5
    assert if_branch.context == "if score >= 90:"
    assert if_branch.body == dedent(
        """\
        label = "excellent"
        score = score - bonus"""
    )

    elif_70 = unit_at_line(conditionals, 6)
    assert elif_70.end_line == 8
    assert elif_70.context == "elif score >= 70:"
    assert elif_70.body == dedent(
        """\
        base = score - 70
        label = f"good ({base})\""""
    )

    elif_50 = unit_at_line(conditionals, 9)
    assert elif_50.end_line == 10
    assert elif_50.context == "elif score >= 50:"
    assert elif_50.body == 'label = "average"'

    else_branch = unit_at_line(conditionals, 11)
    assert else_branch.end_line == 14
    assert else_branch.context == "else:"
    assert else_branch.body == dedent(
        """\
        label = "below average"
        score = 0
        bonus = 0"""
    )

    below_lo = unit_at_line(conditionals, 20)
    assert below_lo.end_line == 22
    assert below_lo.context == "if value < lo:"
    assert below_lo.body == dedent(
        """\
        deficit = lo - value
        adjusted = lo + deficit // 2"""
    )

    above_hi = unit_at_line(conditionals, 23)
    assert above_hi.end_line == 25
    assert above_hi.context == "elif value > hi:"
    assert above_hi.body == dedent(
        """\
        adjusted = hi
        return adjusted - 1"""
    )


def test_extracts_loop_bodies_with_full_body_and_context():
    loops = parse((FIXTURES / "Loops.py").read_bytes())

    assert len(loops) == 6

    simple_for_values = unit_at_line(loops, 3)
    assert simple_for_values.end_line == 5
    assert simple_for_values.context == "for x in values:"
    assert simple_for_values.body == dedent(
        """\
        total += x
        values.append(total)"""
    )

    simple_for = unit_at_line(loops, 11)
    assert simple_for.end_line == 12
    assert simple_for.context == "for x in xs:"
    assert simple_for.body == "best = x if x > best else best"

    while_loop = unit_at_line(loops, 18)
    assert while_loop.end_line == 20
    assert while_loop.context == "while n > 0:"
    assert while_loop.body == dedent(
        """\
        a, b = b, a + b
        n = n - 1"""
    )


def test_extracts_exception_handling_blocks_with_full_body_and_context():
    exceptions = parse((FIXTURES / "Exceptions.py").read_bytes())

    assert len(exceptions) == 8

    try_body = unit_at_line(exceptions, 3)
    assert try_body.end_line == 5
    assert try_body.context == "try:"
    assert try_body.body == dedent(
        """\
        value = int(text)
        value = value * 2"""
    )

    except_value_error = unit_at_line(exceptions, 6)
    assert except_value_error.end_line == 8
    assert except_value_error.context == "except ValueError as e:"
    assert except_value_error.body == dedent(
        """\
        value = -1
        text = str(e)"""
    )

    finally_body = unit_at_line(exceptions, 9)
    assert finally_body.end_line == 11
    assert finally_body.context == "finally:"
    assert finally_body.body == dedent(
        """\
        text = text.strip()
        value = value + len(text)"""
    )

    first_except = unit_at_line(exceptions, 20)
    assert first_except.end_line == 22
    assert first_except.context == "except IndexError:"
    assert first_except.body == dedent(
        """\
        result = fallback
        fallback = fallback - 1"""
    )

    second_except = unit_at_line(exceptions, 23)
    assert second_except.end_line == 24
    assert second_except.context == "except TypeError:"
    assert second_except.body == "result = 0"


def test_extracts_match_cases_with_full_body_and_context():
    match = parse((FIXTURES / "Match.py").read_bytes())

    assert len(match) == 4

    quit_case = unit_at_line(match, 4)
    assert quit_case.end_line == 6
    assert quit_case.context == 'case "quit":'
    assert quit_case.body == dedent(
        """\
        result = "exiting"
        return 0"""
    )

    help_case = unit_at_line(match, 7)
    assert help_case.end_line == 9
    assert help_case.context == 'case "help":'
    assert help_case.body == dedent(
        """\
        name = "help"
        result = f"showing {name}\""""
    )

    default_case = unit_at_line(match, 10)
    assert default_case.end_line == 12
    assert default_case.context == "case _:"
    assert default_case.body == dedent(
        """\
        result = "unknown"
        return -1"""
    )


def test_extracts_with_blocks_with_full_body_and_context():
    with_units = parse((FIXTURES / "With.py").read_bytes())

    assert len(with_units) == 4

    sync_with = unit_at_line(with_units, 3)
    assert sync_with.end_line == 5
    assert sync_with.context == "with open(path) as f:"
    assert sync_with.body == dedent(
        """\
        content = f.read()
        content = content.strip()"""
    )

    async_with = unit_at_line(with_units, 11)
    assert async_with.end_line == 13
    assert async_with.context == "async with session.get(url) as resp:"
    assert async_with.body == dedent(
        """\
        data = await resp.json()
        data = data["result"]"""
    )


def test_extracts_nested_blocks_with_body_node_count():
    nesting = parse((FIXTURES / "NestedBlocks.py").read_bytes())

    for_loop = unit_at_line(nesting, 3)
    assert for_loop.end_line == 8
    assert for_loop.context == "for x in xs:"
    assert for_loop.body_node_count == 25
    assert for_loop.body == dedent(
        """\
        if x > threshold:
            try:
                total = total + 100 // x
            except ZeroDivisionError:
                total = total - 1"""
    )

    conditional = unit_at_line(nesting, 4)
    assert conditional.end_line == 8
    assert conditional.context == "if x > threshold:"
    assert conditional.body_node_count == 20
    assert conditional.body == dedent(
        """\
        try:
            total = total + 100 // x
        except ZeroDivisionError:
            total = total - 1"""
    )

    try_body = unit_at_line(nesting, 5)
    assert try_body.end_line == 6
    assert try_body.context == "try:"
    assert try_body.body_node_count == 9
    assert try_body.body == "total = total + 100 // x"

    except_body = unit_at_line(nesting, 7)
    assert except_body.end_line == 8
    assert except_body.context == "except ZeroDivisionError:"
    assert except_body.body_node_count == 7
    assert except_body.body == "total = total - 1"


def test_extracts_function_with_multiline_signature():
    formatting = parse((FIXTURES / "Formatting.py").read_bytes())

    product = unit_at_line(formatting, 1)
    assert product.end_line == 8
    assert product.context == dedent(
        """\
        def product(
            factors,
            start=1,
        ):"""
    )
    assert product.body == dedent(
        """\
        total = start
        for factor in factors:
            total = total * factor
        return total"""
    )

    register = unit_at_line(formatting, 12)
    assert register.end_line == 18
    assert register.context == dedent(
        """\
        @staticmethod
        def register(
            name,
            value,
        ):"""
    )
    assert register.body == dedent(
        """\
        entry = {name: value}
        return entry"""
    )


def test_replaces_invalid_utf8_bytes_and_extracts_surrounding_function():
    units = parse(b'def greet():\n    return "a\xffb"\n')

    greet = unit_at_line(units, 1)
    assert greet.context == "def greet():"
    assert greet.body == 'return "a�b"'
