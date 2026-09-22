from pathlib import Path
from textwrap import dedent

from slopo.indexing.parsing.lang.cpp import parse

from .conftest import unit_at_line

FIXTURES = Path(__file__).parent / "fixtures" / "cpp"


def test_strips_line_block_and_doc_comments_keeping_blank_lines():
    unit = parse((FIXTURES / "Comments.cpp").read_bytes())[0]

    assert unit.start_line == 3
    assert unit.end_line == 18
    assert unit.context == "int with_comments(int a, int b)"
    assert unit.body_node_count == 32
    assert unit.body == dedent(
        """\
        {

            int sum = a + b;


            std::string url = "http://not-a-comment";

            switch (code) {
                case 1:
                    prepare();

                    dispatch();
            }

            return sum;
        }"""
    )


def test_body_node_count_across_body_shapes():
    body_sizes = parse((FIXTURES / "BodySizes.cpp").read_bytes())

    empty = unit_at_line(body_sizes, 3)
    assert empty.body_node_count == 1

    accumulate = unit_at_line(body_sizes, 5)
    assert accumulate.body_node_count == 24


def test_extracts_block_with_enclosing_function():
    units = parse((FIXTURES / "Functions.cpp").read_bytes())

    average = unit_at_line(units, 28)
    assert average.end_line == 34
    assert average.kind == "function"
    assert average.context == "double average(const std::vector<double> &values)"
    assert average.body == dedent(
        """\
        {
            double sum = 0;
            for (double value : values) {
                sum += value;
            }
            return sum / values.size();
        }"""
    )

    loop = unit_at_line(units, 30)
    assert loop.end_line == 32
    assert loop.kind == "block"
    assert loop.context == "for (double value : values)"
    assert loop.body == dedent(
        """\
        {
            sum += value;
        }"""
    )


def test_extracts_free_member_and_special_functions():
    units = parse((FIXTURES / "Functions.cpp").read_bytes())

    add = unit_at_line(units, 1)
    assert add.end_line == 3
    assert add.kind == "function"
    assert add.context == "int add(int a, int b)"
    assert add.body == dedent(
        """\
        {
            return a + b;
        }"""
    )

    constructor = unit_at_line(units, 8)
    assert constructor.end_line == 8
    assert constructor.kind == "function"
    assert constructor.context == "Accumulator(int start) : total(start)"
    assert constructor.body == "{}"

    destructor = unit_at_line(units, 10)
    assert destructor.end_line == 12
    assert destructor.kind == "function"
    assert destructor.context == "~Accumulator()"
    assert destructor.body == dedent(
        """\
        {
            total = 0;
        }"""
    )

    method = unit_at_line(units, 14)
    assert method.end_line == 18
    assert method.kind == "function"
    assert method.context == "void add_all(const std::vector<int> &values)"
    assert method.body == dedent(
        """\
        {
            for (int value : values) {
                total += value;
            }
        }"""
    )

    operator = unit_at_line(units, 20)
    assert operator.end_line == 23
    assert operator.kind == "function"
    assert operator.context == "Accumulator &operator+=(int amount)"
    assert operator.body == dedent(
        """\
        {
            total += amount;
            return *this;
        }"""
    )

    out_of_line = unit_at_line(units, 36)
    assert out_of_line.end_line == 41
    assert out_of_line.kind == "function"
    assert out_of_line.context == "std::string Accumulator::describe() const"
    assert out_of_line.body == dedent(
        """\
        {
            if (total == 0) {
                return "empty";
            }
            return "nonempty";
        }"""
    )


def test_extracts_lambda_bodies_with_binding_context():
    units = parse((FIXTURES / "Lambdas.cpp").read_bytes())

    assert len(units) == 6

    field = unit_at_line(units, 2)
    assert field.end_line == 5
    assert field.kind == "function"
    assert field.context == "std::function<void()> on_done = []()"
    assert field.body == dedent(
        """\
        {
            done = true;
            pending -= 1;
        }"""
    )

    auto_binding = unit_at_line(units, 9)
    assert auto_binding.end_line == 12
    assert auto_binding.kind == "function"
    assert auto_binding.context == "auto doubler = [](int x)"
    assert auto_binding.body == dedent(
        """\
        {
            int scaled = x * 2;
            return scaled;
        }"""
    )

    typed_binding = unit_at_line(units, 14)
    assert typed_binding.end_line == 18
    assert typed_binding.kind == "function"
    assert typed_binding.context == "std::function<int(int)> shift = [](int v)"
    assert typed_binding.body == dedent(
        """\
        {
            int base = v + 10;
            int adjusted = base - 3;
            return adjusted;
        }"""
    )

    call_argument = unit_at_line(units, 20)
    assert call_argument.end_line == 22
    assert call_argument.kind == "function"
    assert call_argument.context == "[](int a, int b)"
    assert call_argument.body == dedent(
        """\
        {
            return a > b;
        }"""
    )

    reassignment = unit_at_line(units, 24)
    assert reassignment.end_line == 27
    assert reassignment.kind == "function"
    assert reassignment.context == "doubler = [](int x)"
    assert reassignment.body == dedent(
        """\
        {
            int bumped = x + 1;
            return bumped * bumped;
        }"""
    )


def test_extracts_inline_definitions_from_header_file():
    units = parse((FIXTURES / "Header.hpp").read_bytes())

    assert len(units) == 4

    template = unit_at_line(units, 4)
    assert template.end_line == 7
    assert template.kind == "function"
    assert template.context == "T clamp(T value, T lo, T hi)"
    assert template.body == dedent(
        """\
        {
            T low_bounded = value < lo ? lo : value;
            return low_bounded > hi ? hi : low_bounded;
        }"""
    )

    constructor = unit_at_line(units, 11)
    assert constructor.end_line == 11
    assert constructor.kind == "function"
    assert constructor.context == "Counter() : count_(0)"
    assert constructor.body == "{}"

    increment = unit_at_line(units, 13)
    assert increment.end_line == 16
    assert increment.kind == "function"
    assert increment.context == "void increment()"
    assert increment.body == dedent(
        """\
        {
            count_ += 1;
            doubled_ = count_ * 2;
        }"""
    )

    value = unit_at_line(units, 18)
    assert value.end_line == 20
    assert value.kind == "function"
    assert value.context == "int value() const"
    assert value.body == dedent(
        """\
        {
            return count_;
        }"""
    )


def test_extracts_conditional_blocks():
    units = parse((FIXTURES / "Conditionals.cpp").read_bytes())

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
    units = parse((FIXTURES / "Loops.cpp").read_bytes())

    assert len(units) == 8

    counting_for = unit_at_line(units, 3)
    assert counting_for.end_line == 7
    assert counting_for.kind == "block"
    assert counting_for.context == "for (int i = 0; i < values.size(); i++)"
    assert counting_for.body == dedent(
        """\
        {
            int v = values[i];
            total += v;
            total *= 2;
        }"""
    )

    range_for = unit_at_line(units, 13)
    assert range_for.end_line == 16
    assert range_for.context == "for (int value : values)"
    assert range_for.body == dedent(
        """\
        {
            int scaled = value * 3;
            total += scaled;
        }"""
    )

    while_loop = unit_at_line(units, 22)
    assert while_loop.end_line == 25
    assert while_loop.context == "while (n > 1)"
    assert while_loop.body == dedent(
        """\
        {
            n = n % 2 == 0 ? n / 2 : 3 * n + 1;
            steps++;
        }"""
    )

    do_loop = unit_at_line(units, 31)
    assert do_loop.end_line == 34
    assert do_loop.context == "do"
    assert do_loop.body == dedent(
        """\
        {
            last = *cursor;
            cursor++;
        }"""
    )


def test_extracts_switch_blocks():
    units = parse((FIXTURES / "Switch.cpp").read_bytes())

    assert len(units) == 5

    case_zero = unit_at_line(units, 4)
    assert case_zero.end_line == 7
    assert case_zero.kind == "block"
    assert case_zero.context == "case 0:"
    assert case_zero.body == dedent(
        """\
        out = code;
        out += 10;
        break;"""
    )

    fallthrough = unit_at_line(units, 9)
    assert fallthrough.end_line == 11
    assert fallthrough.context == "case 2:"
    assert fallthrough.body == dedent(
        """\
        out = code * 2;
        break;"""
    )

    braced_case = unit_at_line(units, 12)
    assert braced_case.end_line == 16
    assert braced_case.context == "case 3:"
    assert braced_case.body == dedent(
        """\
        {
            int scaled = code * code;
            out = scaled - 1;
            break;
        }"""
    )

    default_case = unit_at_line(units, 17)
    assert default_case.end_line == 18
    assert default_case.context == "default:"
    assert default_case.body == "handled = 0;"


def test_extracts_try_and_catch_blocks():
    units = parse((FIXTURES / "Exceptions.cpp").read_bytes())

    assert len(units) == 4

    try_block = unit_at_line(units, 2)
    assert try_block.end_line == 6
    assert try_block.kind == "block"
    assert try_block.context == "try"
    assert try_block.body == dedent(
        """\
        {
            std::string raw = fetch(path);
            std::string trimmed = trim(raw);
            return trimmed;
        }"""
    )

    first_catch = unit_at_line(units, 6)
    assert first_catch.end_line == 9
    assert first_catch.context == "catch (const std::out_of_range &e)"
    assert first_catch.body == dedent(
        """\
        {
            log(e.what());
            return "";
        }"""
    )

    second_catch = unit_at_line(units, 9)
    assert second_catch.end_line == 12
    assert second_catch.context == "catch (const std::exception &e)"
    assert second_catch.body == dedent(
        """\
        {
            log(e.what());
            throw;
        }"""
    )


def test_skips_unbraced_bodies():
    units = parse((FIXTURES / "Unbraced.cpp").read_bytes())

    assert len(units) == 2

    guard = unit_at_line(units, 1)
    assert guard.end_line == 7
    assert guard.kind == "function"

    product = unit_at_line(units, 9)
    assert product.end_line == 15
    assert product.kind == "function"


def test_extracts_nested_constructs():
    units = parse((FIXTURES / "Nested.cpp").read_bytes())

    scan = unit_at_line(units, 1)
    assert scan.end_line == 17
    assert scan.context == "int scan(const std::vector<int> &data)"
    assert scan.body_node_count == 56
    assert scan.body == dedent(
        """\
        {
            int hits = 0;
            for (int value : data) {
                if (value > 0) {
                    try {
                        int remaining = probe(value);
                        while (remaining > 0) {
                            hits++;
                            remaining -= 2;
                        }
                    } catch (const std::exception &e) {
                        hits -= 1;
                    }
                }
            }
            return hits;
        }"""
    )

    range_for = unit_at_line(units, 3)
    assert range_for.end_line == 15
    assert range_for.context == "for (int value : data)"
    assert range_for.body_node_count == 44
    assert range_for.body == dedent(
        """\
        {
            if (value > 0) {
                try {
                    int remaining = probe(value);
                    while (remaining > 0) {
                        hits++;
                        remaining -= 2;
                    }
                } catch (const std::exception &e) {
                    hits -= 1;
                }
            }
        }"""
    )

    if_block = unit_at_line(units, 4)
    assert if_block.end_line == 14
    assert if_block.context == "if (value > 0)"
    assert if_block.body_node_count == 38
    assert if_block.body == dedent(
        """\
        {
            try {
                int remaining = probe(value);
                while (remaining > 0) {
                    hits++;
                    remaining -= 2;
                }
            } catch (const std::exception &e) {
                hits -= 1;
            }
        }"""
    )

    try_block = unit_at_line(units, 5)
    assert try_block.end_line == 11
    assert try_block.context == "try"
    assert try_block.body_node_count == 22
    assert try_block.body == dedent(
        """\
        {
            int remaining = probe(value);
            while (remaining > 0) {
                hits++;
                remaining -= 2;
            }
        }"""
    )

    while_loop = unit_at_line(units, 7)
    assert while_loop.end_line == 10
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
    units = parse((FIXTURES / "Formatting.cpp").read_bytes())

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
        std::string multi_line_signature(
            const std::string &first,
            const std::string &second
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
    units = parse(b'std::string greet() {\n    return std::string("a\xffb");\n}\n')

    greet = unit_at_line(units, 1)
    assert greet.context == "std::string greet()"
    assert greet.body == dedent(
        """\
        {
            return std::string("a�b");
        }"""
    )
