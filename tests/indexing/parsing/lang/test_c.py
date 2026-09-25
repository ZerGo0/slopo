from pathlib import Path
from textwrap import dedent

from slopo.indexing.parsing.lang.c import parse

from .conftest import unit_at_line

FIXTURES = Path(__file__).parent / "fixtures" / "c"


def test_strips_comments_preserving_blank_lines():
    unit = parse((FIXTURES / "Comments.c").read_bytes())[0]

    assert unit.start_line == 4
    assert unit.end_line == 19
    assert unit.context == "int with_comments(int a, int b)"
    assert unit.body_node_count == 32
    assert unit.body == dedent(
        """\
        {

            int sum = a + b;


            const char *url = "http://not-a-comment";

            switch (code) {
                case 1:
                    prepare();

                    dispatch();
            }

            return sum;
        }"""
    )


def test_body_node_count_across_body_shapes():
    body_sizes = parse((FIXTURES / "BodySizes.c").read_bytes())

    empty = unit_at_line(body_sizes, 3)
    assert empty.body_node_count == 1

    accumulate = unit_at_line(body_sizes, 5)
    assert accumulate.body_node_count == 33


def test_extracts_block_with_enclosing_function():
    functions = parse((FIXTURES / "Functions.c").read_bytes())

    average = unit_at_line(functions, 12)
    assert average.end_line == 18
    assert average.kind == "function"
    assert average.context == "double average(const double *values, int count)"
    assert average.body == dedent(
        """\
        {
            double sum = 0;
            for (int i = 0; i < count; i++) {
                sum += values[i];
            }
            return sum / count;
        }"""
    )

    loop = unit_at_line(functions, 14)
    assert loop.end_line == 16
    assert loop.kind == "block"
    assert loop.context == "for (int i = 0; i < count; i++)"
    assert loop.body == dedent(
        """\
        {
            sum += values[i];
        }"""
    )


def test_extracts_each_function_with_full_body():
    functions = parse((FIXTURES / "Functions.c").read_bytes())

    add = unit_at_line(functions, 1)
    assert add.end_line == 3
    assert add.context == "int add(int a, int b)"
    assert add.body == dedent(
        """\
        {
            return a + b;
        }"""
    )

    pick = unit_at_line(functions, 5)
    assert pick.end_line == 10
    assert pick.context == "const char *pick(const char *primary, const char *fallback)"
    assert pick.body == dedent(
        """\
        {
            if (primary != 0) {
                return primary;
            }
            return fallback;
        }"""
    )

    clamp = unit_at_line(functions, 20)
    assert clamp.end_line == 28
    assert clamp.context == "void clamp_in_place(int *value, int lo, int hi)"
    assert clamp.body == dedent(
        """\
        {
            if (*value < lo) {
                *value = lo;
                return;
            }
            if (*value > hi) {
                *value = hi;
            }
        }"""
    )


def test_extracts_conditional_blocks():
    units = parse((FIXTURES / "Conditionals.c").read_bytes())

    assert len(units) == 8

    if_block = unit_at_line(units, 3)
    assert if_block.end_line == 7
    assert if_block.context == "if (n < 0)"
    assert if_block.body == dedent(
        """\
        {
            score = -n;
            score += 1;
            return score;
        }"""
    )

    if_of_else = unit_at_line(units, 8)
    assert if_of_else.end_line == 11
    assert if_of_else.context == "if (n == 0)"
    assert if_of_else.body == dedent(
        """\
        {
            score = 100;
            score /= 2;
        }"""
    )

    else_block = unit_at_line(units, 11)
    assert else_block.end_line == 14
    assert else_block.context == "else"
    assert else_block.body == dedent(
        """\
        {
            score = n * 3;
            score -= 4;
        }"""
    )

    first_if = unit_at_line(units, 19)
    assert first_if.end_line == 22
    assert first_if.context == "if (marks + bonus >= 90)"
    assert first_if.body == dedent(
        """\
        {
            int total = marks + bonus;
            return total > 95 ? "A+" : "A";
        }"""
    )

    else_if = unit_at_line(units, 22)
    assert else_if.end_line == 25
    assert else_if.context == "if (marks >= 50)"
    assert else_if.body == dedent(
        """\
        {
            int deficit = 70 - marks;
            return deficit > 0 ? "C" : "B";
        }"""
    )

    final_else = unit_at_line(units, 25)
    assert final_else.end_line == 27
    assert final_else.context == "else"
    assert final_else.body == dedent(
        """\
        {
            return "F";
        }"""
    )


def test_extracts_loop_blocks():
    units = parse((FIXTURES / "Loops.c").read_bytes())

    assert len(units) == 6

    for_loop = unit_at_line(units, 3)
    assert for_loop.end_line == 7
    assert for_loop.context == "for (int i = 0; i < count; i++)"
    assert for_loop.body == dedent(
        """\
        {
            int v = values[i];
            total += v;
            total *= 2;
        }"""
    )

    while_loop = unit_at_line(units, 17)
    assert while_loop.end_line == 20
    assert while_loop.context == "while (n > 1)"
    assert while_loop.body == dedent(
        """\
        {
            n = n % 2 == 0 ? n / 2 : 3 * n + 1;
            steps++;
        }"""
    )

    do_loop = unit_at_line(units, 26)
    assert do_loop.end_line == 29
    assert do_loop.context == "do"
    assert do_loop.body == dedent(
        """\
        {
            last = *cursor;
            cursor++;
        }"""
    )


def test_extracts_switch_blocks():
    units = parse((FIXTURES / "Switch.c").read_bytes())

    assert len(units) == 5

    case_zero = unit_at_line(units, 4)
    assert case_zero.end_line == 7
    assert case_zero.context == "case 0:"
    assert case_zero.body == dedent(
        """\
        *out = code;
        *out += 10;
        break;"""
    )

    case_two = unit_at_line(units, 9)
    assert case_two.end_line == 11
    assert case_two.context == "case 2:"
    assert case_two.body == dedent(
        """\
        *out = code * 2;
        break;"""
    )

    case_three = unit_at_line(units, 12)
    assert case_three.end_line == 16
    assert case_three.context == "case 3:"
    assert case_three.body == dedent(
        """\
        {
            int scaled = code * code;
            *out = scaled - 1;
            break;
        }"""
    )

    default_case = unit_at_line(units, 17)
    assert default_case.end_line == 18
    assert default_case.context == "default:"
    assert default_case.body == "handled = 0;"


def test_skips_unbraced_bodies():
    units = parse((FIXTURES / "Unbraced.c").read_bytes())

    assert len(units) == 2

    guard = unit_at_line(units, 1)
    assert guard.end_line == 6
    assert guard.kind == "function"

    product = unit_at_line(units, 8)
    assert product.end_line == 13
    assert product.kind == "function"


def test_extracts_nested_constructs():
    units = parse((FIXTURES / "Nested.c").read_bytes())

    scan = unit_at_line(units, 1)
    assert scan.end_line == 13
    assert scan.context == "int scan(const int *data, int count)"
    assert scan.body_node_count == 48
    assert scan.body == dedent(
        """\
        {
            int hits = 0;
            for (int i = 0; i < count; i++) {
                if (data[i] > 0) {
                    int remaining = data[i];
                    while (remaining > 0) {
                        hits++;
                        remaining -= 2;
                    }
                }
            }
            return hits;
        }"""
    )

    for_loop = unit_at_line(units, 3)
    assert for_loop.end_line == 11
    assert for_loop.context == "for (int i = 0; i < count; i++)"
    assert for_loop.body_node_count == 29
    assert for_loop.body == dedent(
        """\
        {
            if (data[i] > 0) {
                int remaining = data[i];
                while (remaining > 0) {
                    hits++;
                    remaining -= 2;
                }
            }
        }"""
    )

    if_block = unit_at_line(units, 4)
    assert if_block.end_line == 10
    assert if_block.context == "if (data[i] > 0)"
    assert if_block.body_node_count == 21
    assert if_block.body == dedent(
        """\
        {
            int remaining = data[i];
            while (remaining > 0) {
                hits++;
                remaining -= 2;
            }
        }"""
    )

    while_loop = unit_at_line(units, 6)
    assert while_loop.end_line == 9
    assert while_loop.context == "while (remaining > 0)"
    assert while_loop.body_node_count == 8
    assert while_loop.body == dedent(
        """\
        {
            hits++;
            remaining -= 2;
        }"""
    )


def test_header_body_boundary_survives_formatting_variation():
    units = parse((FIXTURES / "Formatting.c").read_bytes())

    allman = unit_at_line(units, 1)
    assert allman.end_line == 8
    assert allman.context == "int allman(int a, int b)"
    assert allman.body == dedent(
        """\
        {
            if (a > b)
            {
                return a;
            }
            return b;
        }"""
    )

    allman_if = unit_at_line(units, 3)
    assert allman_if.end_line == 6
    assert allman_if.context == "if (a > b)"
    assert allman_if.body == dedent(
        """\
        {
            return a;
        }"""
    )

    signature = unit_at_line(units, 10)
    assert signature.end_line == 15
    assert signature.context == dedent(
        """\
        int multi_line_signature(
            int first,
            int second
        )"""
    )
    assert signature.body == dedent(
        """\
        {
            return first + second;
        }"""
    )

    header = unit_at_line(units, 19)
    assert header.end_line == 24
    assert header.context == dedent(
        """\
        while (a > 0
        && b > 0
        && c > 0)"""
    )
    assert header.body == dedent(
        """\
        {
            total += a;
            a -= 1;
        }"""
    )


def test_replaces_invalid_utf8_bytes_and_extracts_surrounding_function():
    units = parse(b'const char *greet(void) {\n    return "a\xffb";\n}\n')

    greet = unit_at_line(units, 1)
    assert greet.context == "const char *greet(void)"
    assert greet.body == dedent(
        """\
        {
            return "a�b";
        }"""
    )
