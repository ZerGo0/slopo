from pathlib import Path
from textwrap import dedent

from slopo.indexing.parsing.lang.csharp import parse

from .conftest import unit_at_line

FIXTURES = Path(__file__).parent / "fixtures" / "csharp"


def test_strips_line_block_and_doc_comments_keeping_blank_lines():
    unit = parse((FIXTURES / "Comments.cs").read_bytes())[0]

    assert unit.start_line == 6
    assert unit.end_line == 13
    assert unit.context == "public string BuildPath(string resource, int id)"
    assert unit.body == dedent(
        """\
        {

            string path = resource + "/" + id;

            string endpoint = "https://api.example.com // v1";
            return endpoint + "/" + path;
        }"""
    )


def test_body_node_count_across_body_shapes():
    body_sizes = parse((FIXTURES / "BodySizes.cs").read_bytes())

    empty = unit_at_line(body_sizes, 12)
    assert empty.body_node_count == 1

    expression = unit_at_line(body_sizes, 16)
    assert expression.body_node_count == 1

    block = unit_at_line(body_sizes, 18)
    assert block.body_node_count == 29


def test_extracts_function_together_with_its_nested_blocks():
    units = parse((FIXTURES / "Conditionals.cs").read_bytes())

    classify = unit_at_line(units, 5)
    assert classify.end_line == 21
    assert classify.kind == "function"
    assert classify.context == "public string Classify(int score)"
    assert classify.body == dedent(
        """\
        {
            if (score >= 90)
            {
                return "A";
            }

            if (score >= 60)
            {
                return "pass";
            }
            else
            {
                string note = "retake recommended";
                return note;
            }
        }"""
    )

    else_block = unit_at_line(units, 16)
    assert else_block.end_line == 20
    assert else_block.kind == "block"
    assert else_block.context == "else"
    assert else_block.body == dedent(
        """\
        {
            string note = "retake recommended";
            return note;
        }"""
    )


def test_extracts_constructor_methods_and_expression_bodied_member():
    functions = parse((FIXTURES / "Functions.cs").read_bytes())

    constructor = unit_at_line(functions, 8)
    assert constructor.end_line == 12
    assert constructor.context == "public Rectangle(double width, double height)"
    assert constructor.body == dedent(
        """\
        {
            _width = width;
            _height = height;
        }"""
    )

    area = unit_at_line(functions, 14)
    assert area.end_line == 17
    assert area.context == "public double Area()"
    assert area.body == dedent(
        """\
        {
            return _width * _height;
        }"""
    )

    to_string = unit_at_line(functions, 26)
    assert to_string.end_line == 26
    assert to_string.context == "public override string ToString() =>"
    assert to_string.body == '$"Rectangle({_width}x{_height})"'


def test_extracts_property_accessors_with_block_and_expression_bodies():
    properties = parse((FIXTURES / "Properties.cs").read_bytes())

    assert len(properties) == 4

    getter = unit_at_line(properties, 10)
    assert getter.end_line == 13
    assert getter.context == "get"
    assert getter.body == dedent(
        """\
        {
            return _balance;
        }"""
    )

    setter = unit_at_line(properties, 14)
    assert setter.end_line == 18
    assert setter.context == "set"
    assert setter.body == dedent(
        """\
        {
            decimal rounded = decimal.Round(value, 2);
            _balance = rounded;
        }"""
    )

    expression_getter = unit_at_line(properties, 23)
    assert expression_getter.end_line == 23
    assert expression_getter.context == "get =>"
    assert expression_getter.body == "_owner"

    expression_setter = unit_at_line(properties, 24)
    assert expression_setter.end_line == 24
    assert expression_setter.context == "set =>"
    assert expression_setter.body == "_owner = value.Trim()"


def test_extracts_local_function_alongside_enclosing_method():
    local = parse((FIXTURES / "LocalFunctions.cs").read_bytes())

    assert len(local) == 2

    indent = unit_at_line(local, 5)
    assert indent.end_line == 12
    assert indent.context == "public string Indent(string[] lines, int spaces)"

    pad = unit_at_line(local, 7)
    assert pad.end_line == 7
    assert pad.context == "string Pad(string line) =>"
    assert pad.body == "new string(' ', spaces) + line"


def test_extracts_lambda_and_anonymous_method_bodies():
    lambdas = parse((FIXTURES / "Lambdas.cs").read_bytes())

    assert len(lambdas) == 6

    doubler = unit_at_line(lambdas, 10)
    assert doubler.end_line == 10
    assert doubler.context == "Func<int, int> doubler = x =>"
    assert doubler.body == "x * 2"

    predicate = unit_at_line(lambdas, 12)
    assert predicate.end_line == 12
    assert predicate.context == "v =>"
    assert predicate.body == "v > 0"

    block_lambda = unit_at_line(lambdas, 13)
    assert block_lambda.end_line == 17
    assert block_lambda.context == "v =>"
    assert block_lambda.body == dedent(
        """\
        {
            int scaled = doubler(v);
            return scaled + 1;
        }"""
    )

    anonymous = unit_at_line(lambdas, 23)
    assert anonymous.end_line == 26
    assert anonymous.context == "OnError = delegate(Exception ex)"
    assert anonymous.body == dedent(
        """\
        {
            Console.WriteLine(ex.Message);
        }"""
    )


def test_extracts_conditional_blocks():
    units = parse((FIXTURES / "Conditionals.cs").read_bytes())

    assert len(units) == 4

    first_if = unit_at_line(units, 7)
    assert first_if.end_line == 10
    assert first_if.context == "if (score >= 90)"
    assert first_if.body == dedent(
        """\
        {
            return "A";
        }"""
    )

    second_if = unit_at_line(units, 12)
    assert second_if.end_line == 15
    assert second_if.context == "if (score >= 60)"
    assert second_if.body == dedent(
        """\
        {
            return "pass";
        }"""
    )

    else_block = unit_at_line(units, 16)
    assert else_block.end_line == 20
    assert else_block.context == "else"
    assert else_block.body == dedent(
        """\
        {
            string note = "retake recommended";
            return note;
        }"""
    )


def test_extracts_loop_blocks():
    units = parse((FIXTURES / "Loops.cs").read_bytes())

    assert len(units) == 5

    for_block = unit_at_line(units, 10)
    assert for_block.end_line == 15
    assert for_block.context == "for (int i = 0; i < values.Length; i++)"
    assert for_block.body == dedent(
        """\
        {
            int value = values[i];
            total += value * i;
            steps += 1;
        }"""
    )

    foreach_block = unit_at_line(units, 17)
    assert foreach_block.end_line == 21
    assert foreach_block.context == "foreach (var value in values)"
    assert foreach_block.body == dedent(
        """\
        {
            int weighted = value * 3;
            total += weighted - steps;
        }"""
    )

    while_block = unit_at_line(units, 23)
    assert while_block.end_line == 27
    assert while_block.context == "while (total > limit)"
    assert while_block.body == dedent(
        """\
        {
            total -= limit;
            total = total / 2;
        }"""
    )

    do_block = unit_at_line(units, 29)
    assert do_block.end_line == 32
    assert do_block.context == "do"
    assert do_block.body == dedent(
        """\
        {
            total += steps;
        }"""
    )


def test_extracts_exception_blocks():
    units = parse((FIXTURES / "Exceptions.cs").read_bytes())

    assert len(units) == 5

    try_block = unit_at_line(units, 9)
    assert try_block.end_line == 13
    assert try_block.context == "try"
    assert try_block.body == dedent(
        """\
        {
            string raw = Fetch(path);
            return raw.Trim();
        }"""
    )

    catch_block = unit_at_line(units, 14)
    assert catch_block.end_line == 18
    assert catch_block.context == "catch (FileNotFoundException e)"
    assert catch_block.body == dedent(
        """\
        {
            Log(e);
            return "";
        }"""
    )

    filtered_catch = unit_at_line(units, 19)
    assert filtered_catch.end_line == 23
    assert filtered_catch.context == (
        "catch (IOException e) when (e.InnerException != null)"
    )
    assert filtered_catch.body == dedent(
        """\
        {
            Log(e.InnerException);
            throw;
        }"""
    )

    finally_block = unit_at_line(units, 24)
    assert finally_block.end_line == 27
    assert finally_block.context == "finally"
    assert finally_block.body == dedent(
        """\
        {
            Cleanup();
        }"""
    )


def test_extracts_switch_section_blocks():
    units = parse((FIXTURES / "Switch.cs").read_bytes())

    assert len(units) == 4

    first = unit_at_line(units, 9)
    assert first.end_line == 11
    assert first.context == "case 1:"
    assert first.body == dedent(
        """\
        string first = "home";
        return first;"""
    )

    fall_through = unit_at_line(units, 13)
    assert fall_through.end_line == 15
    assert fall_through.context == "case 3:"
    assert fall_through.body == dedent(
        """\
        Log(code);
        return "section";"""
    )

    default = unit_at_line(units, 16)
    assert default.end_line == 17
    assert default.context == "default:"
    assert default.body == 'return "not found";'


def test_extracts_using_and_lock_blocks():
    units = parse((FIXTURES / "Scopes.cs").read_bytes())

    assert len(units) == 3

    using_block = unit_at_line(units, 11)
    assert using_block.end_line == 15
    assert using_block.kind == "block"
    assert using_block.context == "using (var stream = Open(path))"
    assert using_block.body == dedent(
        """\
        {
            stream.Write(data);
            stream.Flush();
        }"""
    )

    lock_block = unit_at_line(units, 17)
    assert lock_block.end_line == 21
    assert lock_block.kind == "block"
    assert lock_block.context == "lock (_gate)"
    assert lock_block.body == dedent(
        """\
        {
            _pending += 1;
            Commit();
        }"""
    )


def test_nested_blocks_carry_only_their_own_body_node_count():
    units = parse((FIXTURES / "Nested.cs").read_bytes())

    foreach_block = unit_at_line(units, 8)
    assert foreach_block.end_line == 17
    assert foreach_block.context == "foreach (var row in rows)"
    assert foreach_block.body_node_count == 28
    assert foreach_block.body == dedent(
        """\
        {
            for (int i = 0; i < row.Length; i++)
            {
                if (row[i] > threshold)
                {
                    hits += 1;
                }
            }
        }"""
    )

    for_block = unit_at_line(units, 10)
    assert for_block.end_line == 16
    assert for_block.context == "for (int i = 0; i < row.Length; i++)"
    assert for_block.body_node_count == 14
    assert for_block.body == dedent(
        """\
        {
            if (row[i] > threshold)
            {
                hits += 1;
            }
        }"""
    )

    if_block = unit_at_line(units, 12)
    assert if_block.end_line == 15
    assert if_block.context == "if (row[i] > threshold)"
    assert if_block.body_node_count == 5
    assert if_block.body == dedent(
        """\
        {
            hits += 1;
        }"""
    )


def test_header_body_boundary_survives_formatting_variation():
    units = parse((FIXTURES / "Formatting.cs").read_bytes())

    k_and_r = unit_at_line(units, 4)
    assert k_and_r.end_line == 9
    assert k_and_r.context == "public int KAndR(int a, int b)"
    assert k_and_r.body == dedent(
        """\
        {
            if (a > b) {
                return a;
            }
            return b;
        }"""
    )

    same_line_if = unit_at_line(units, 5)
    assert same_line_if.end_line == 7
    assert same_line_if.context == "if (a > b)"
    assert same_line_if.body == dedent(
        """\
        {
            return a;
        }"""
    )

    multi_line = unit_at_line(units, 11)
    assert multi_line.end_line == 16
    assert multi_line.context == dedent(
        """\
        public int MultiLineSignature(
            int first,
            int second
        )"""
    )
    assert multi_line.body == dedent(
        """\
        {
            return first + second;
        }"""
    )

    multi_line_header = unit_at_line(units, 20)
    assert multi_line_header.end_line == 25
    assert multi_line_header.context == dedent(
        """\
        while (a > 0
        && b > 0
        && c > 0)"""
    )
    assert multi_line_header.body == dedent(
        """\
        {
            total += a;
            a -= 1;
        }"""
    )


def test_replaces_invalid_utf8_bytes_and_extracts_surrounding_function():
    units = parse(
        b'class C {\n    string Greet() {\n        return "a\xffb";\n    }\n}\n'
    )

    greet = unit_at_line(units, 2)
    assert greet.context == "string Greet()"
    assert greet.body == dedent(
        """\
        {
            return "a�b";
        }"""
    )
