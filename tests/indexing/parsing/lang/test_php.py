from pathlib import Path
from textwrap import dedent

from slopo.indexing.parsing.lang.php import parse

from .conftest import unit_at_line

FIXTURES = Path(__file__).parent / "fixtures" / "php"


def test_strips_line_hash_block_and_doc_comments_keeping_blank_lines():
    unit = parse((FIXTURES / "Comments.php").read_bytes())[0]

    assert unit.start_line == 8
    assert unit.end_line == 15
    assert unit.context == "public function withComments(int $a, int $b): int"
    assert unit.body_node_count == 19
    assert unit.body == dedent(
        """\
        {

            $sum = $a + $b;

            $url = "http://not-a-comment";
            return $sum;
        }"""
    )


def test_body_node_count_across_body_shapes():
    body_sizes = parse((FIXTURES / "BodySizes.php").read_bytes())

    empty = unit_at_line(body_sizes, 7)
    assert empty.body_node_count == 1

    with_logic = unit_at_line(body_sizes, 11)
    assert with_logic.body_node_count == 28


def test_extracts_blocks_with_enclosing_function():
    loops = parse((FIXTURES / "Loops.php").read_bytes())

    join_parts = unit_at_line(loops, 3)
    assert join_parts.end_line == 11
    assert join_parts.kind == "function"
    assert join_parts.context == "function joinParts(array $parts): string"
    assert join_parts.body == dedent(
        """\
        {
            $out = "";
            for ($i = 0; $i < count($parts); $i++) {
                $out .= $parts[$i];
                $out .= ",";
            }
            return $out;
        }"""
    )

    index_for = unit_at_line(loops, 6)
    assert index_for.end_line == 9
    assert index_for.kind == "block"
    assert index_for.context == "for ($i = 0; $i < count($parts); $i++)"
    assert index_for.body == dedent(
        """\
        {
            $out .= $parts[$i];
            $out .= ",";
        }"""
    )


def test_extracts_methods_and_top_level_functions():
    functions = parse((FIXTURES / "Functions.php").read_bytes())

    add = unit_at_line(functions, 7)
    assert add.end_line == 10
    assert add.context == "public function add(int $a, int $b): int"
    assert add.body == dedent(
        """\
        {
            return $a + $b;
        }"""
    )

    greet = unit_at_line(functions, 12)
    assert greet.end_line == 15
    assert greet.context == "public static function greet(string $name): string"
    assert greet.body == dedent(
        """\
        {
            return "Hello, {$name}!";
        }"""
    )

    normalize = unit_at_line(functions, 18)
    assert normalize.end_line == 21
    assert normalize.context == "function normalize(string $text): string"
    assert normalize.body == dedent(
        """\
        {
            return strtolower(trim($text));
        }"""
    )

    repeat = unit_at_line(functions, 23)
    assert repeat.end_line == 26
    assert repeat.context == "function repeat(string $text, int $times): string"
    assert repeat.body == dedent(
        """\
        {
            return str_repeat($text, $times);
        }"""
    )


def test_extracts_method_from_anonymous_class_alongside_enclosing_method():
    nested = parse((FIXTURES / "Nested.php").read_bytes())

    assert len(nested) == 2

    make_inner = unit_at_line(nested, 5)
    assert make_inner.end_line == 13
    assert make_inner.context == "private function makeInner(): object"
    assert make_inner.body == dedent(
        """\
        {
            return new class {
                public function innerMethod(): string
                {
                    return "inner";
                }
            };
        }"""
    )

    inner = unit_at_line(nested, 8)
    assert inner.end_line == 11
    assert inner.context == "public function innerMethod(): string"
    assert inner.body == dedent(
        """\
        {
            return "inner";
        }"""
    )


def test_extracts_closure_alongside_enclosing_method():
    nested_in_body = parse((FIXTURES / "NestedInBody.php").read_bytes())

    assert len(nested_in_body) == 2

    make_task = unit_at_line(nested_in_body, 5)
    assert make_task.end_line == 11
    assert make_task.context == "public function makeTask(string $label): callable"
    assert make_task.body == dedent(
        """\
        {
            $run = function () use ($label) {
                echo $label;
            };
            return $run;
        }"""
    )

    run = unit_at_line(nested_in_body, 7)
    assert run.end_line == 9
    assert run.context == "$run = function () use ($label)"
    assert run.body == dedent(
        """\
        {
            echo $label;
        }"""
    )


def test_extracts_arrow_and_closure_with_context():
    closures = parse((FIXTURES / "Closures.php").read_bytes())

    assert len(closures) == 4

    doubler = unit_at_line(closures, 7)
    assert doubler.end_line == 7
    assert doubler.kind == "function"
    assert doubler.context == "$doubler = fn(int $x) =>"
    assert doubler.body == "$x * 2"

    on_complete = unit_at_line(closures, 9)
    assert on_complete.end_line == 11
    assert on_complete.kind == "function"
    assert on_complete.context == "$this->onComplete = function ()"
    assert on_complete.body == dedent(
        """\
        {
            echo "done";
        }"""
    )

    callback = unit_at_line(closures, 13)
    assert callback.end_line == 13
    assert callback.kind == "function"
    assert callback.context == "array_map fn(int $v) =>"
    assert callback.body == "$v + 1"


def test_extracts_conditional_branches_with_full_body_and_context():
    conditionals = parse((FIXTURES / "Conditionals.php").read_bytes())

    assert len(conditionals) == 7

    if_branch = unit_at_line(conditionals, 6)
    assert if_branch.end_line == 9
    assert if_branch.context == "if ($score >= 90)"
    assert if_branch.body == dedent(
        """\
        {
            $tier = "gold";
            $score = $score - 90;
        }"""
    )

    elseif_branch = unit_at_line(conditionals, 9)
    assert elseif_branch.end_line == 11
    assert elseif_branch.context == "elseif ($score >= 50)"
    assert elseif_branch.body == dedent(
        """\
        {
            $tier = "silver";
        }"""
    )

    else_branch = unit_at_line(conditionals, 11)
    assert else_branch.end_line == 14
    assert else_branch.context == "else"
    assert else_branch.body == dedent(
        """\
        {
            $tier = "bronze";
            $score = 0;
        }"""
    )

    below_min = unit_at_line(conditionals, 21)
    assert below_min.end_line == 24
    assert below_min.context == "if ($value < $min)"
    assert below_min.body == dedent(
        """\
        {
            $deficit = $min - $value;
            $adjusted = $min + intdiv($deficit, 2);
        }"""
    )

    above_max = unit_at_line(conditionals, 25)
    assert above_max.end_line == 28
    assert above_max.context == "if ($value > $max)"
    assert above_max.body == dedent(
        """\
        {
            $adjusted = $max;
            return $adjusted - 1;
        }"""
    )


def test_extracts_loop_bodies_with_full_body_and_context():
    loops = parse((FIXTURES / "Loops.php").read_bytes())

    assert len(loops) == 8

    index_for = unit_at_line(loops, 6)
    assert index_for.end_line == 9
    assert index_for.context == "for ($i = 0; $i < count($parts); $i++)"
    assert index_for.body == dedent(
        """\
        {
            $out .= $parts[$i];
            $out .= ",";
        }"""
    )

    foreach_loop = unit_at_line(loops, 16)
    assert foreach_loop.end_line == 18
    assert foreach_loop.context == "foreach ($xs as $x)"
    assert foreach_loop.body == dedent(
        """\
        {
            $max = $x > $max ? $x : $max;
        }"""
    )

    while_loop = unit_at_line(loops, 26)
    assert while_loop.end_line == 31
    assert while_loop.context == "while ($n > 0)"
    assert while_loop.body == dedent(
        """\
        {
            $next = $a + $b;
            $a = $b;
            $b = $next;
            $n = $n - 1;
        }"""
    )

    do_while = unit_at_line(loops, 38)
    assert do_while.end_line == 41
    assert do_while.context == "do"
    assert do_while.body == dedent(
        """\
        {
            $n = intdiv($n, 10);
            $count = $count + 1;
        }"""
    )


def test_extracts_exception_handling_blocks_with_full_body_and_context():
    exceptions = parse((FIXTURES / "Exceptions.php").read_bytes())

    assert len(exceptions) == 8

    try_body = unit_at_line(exceptions, 6)
    assert try_body.end_line == 9
    assert try_body.context == "try"
    assert try_body.body == dedent(
        """\
        {
            $value = intval($text);
            $value = $value * 2;
        }"""
    )

    catch_body = unit_at_line(exceptions, 9)
    assert catch_body.end_line == 12
    assert catch_body.context == "catch (InvalidArgumentException $e)"
    assert catch_body.body == dedent(
        """\
        {
            $value = 0;
            $text = $e->getMessage();
        }"""
    )

    finally_body = unit_at_line(exceptions, 12)
    assert finally_body.end_line == 15
    assert finally_body.context == "finally"
    assert finally_body.body == dedent(
        """\
        {
            $text = trim($text);
            $value = $value + strlen($text);
        }"""
    )

    first_catch = unit_at_line(exceptions, 25)
    assert first_catch.end_line == 28
    assert first_catch.context == "catch (OutOfRangeException $e)"
    assert first_catch.body == dedent(
        """\
        {
            $result = $fallback;
            $fallback = $fallback - 1;
        }"""
    )

    second_catch = unit_at_line(exceptions, 28)
    assert second_catch.end_line == 30
    assert second_catch.context == "catch (TypeError $e)"
    assert second_catch.body == dedent(
        """\
        {
            $result = 0;
        }"""
    )


def test_extracts_switch_cases_with_full_body_and_context():
    switch = parse((FIXTURES / "Switch.php").read_bytes())

    assert len(switch) == 4

    first_case = unit_at_line(switch, 7)
    assert first_case.end_line == 10
    assert first_case.context == "case 1:"
    assert first_case.body == dedent(
        """\
        $name = "red";
        $name = strtoupper($name);
        break;"""
    )

    second_case = unit_at_line(switch, 11)
    assert second_case.end_line == 14
    assert second_case.context == "case 2:"
    assert second_case.body == dedent(
        """\
        $name = "green";
        $name = $name . "!";
        break;"""
    )

    default_case = unit_at_line(switch, 15)
    assert default_case.end_line == 17
    assert default_case.context == "default:"
    assert default_case.body == dedent(
        """\
        $name = "unknown";
        $name = substr($name, 0, 3);"""
    )


def test_extracts_nested_blocks_with_body_node_counts():
    nesting = parse((FIXTURES / "NestedBlocks.php").read_bytes())

    loop = unit_at_line(nesting, 6)
    assert loop.end_line == 14
    assert loop.context == "foreach ($xs as $x)"
    assert loop.body_node_count == 41
    assert loop.body == dedent(
        """\
        {
            if ($x > $threshold) {
                try {
                    $total = $total + intdiv(100, $x);
                } catch (DivisionByZeroError $e) {
                    $total = $total - 1;
                }
            }
        }"""
    )

    conditional = unit_at_line(nesting, 7)
    assert conditional.end_line == 13
    assert conditional.context == "if ($x > $threshold)"
    assert conditional.body_node_count == 33
    assert conditional.body == dedent(
        """\
        {
            try {
                $total = $total + intdiv(100, $x);
            } catch (DivisionByZeroError $e) {
                $total = $total - 1;
            }
        }"""
    )

    try_body = unit_at_line(nesting, 8)
    assert try_body.end_line == 10
    assert try_body.context == "try"
    assert try_body.body_node_count == 16
    assert try_body.body == dedent(
        """\
        {
            $total = $total + intdiv(100, $x);
        }"""
    )

    catch_body = unit_at_line(nesting, 10)
    assert catch_body.end_line == 12
    assert catch_body.context == "catch (DivisionByZeroError $e)"
    assert catch_body.body_node_count == 9
    assert catch_body.body == dedent(
        """\
        {
            $total = $total - 1;
        }"""
    )


def test_extracts_allman_braced_conditional_branches():
    formatting = parse((FIXTURES / "Formatting.php").read_bytes())

    if_branch = unit_at_line(formatting, 6)
    assert if_branch.end_line == 10
    assert if_branch.context == "if ($score >= 90)"
    assert if_branch.body == dedent(
        """\
        {
            $label = "gold";
            $score -= 90;
        }"""
    )

    elseif_branch = unit_at_line(formatting, 11)
    assert elseif_branch.end_line == 14
    assert elseif_branch.context == "elseif ($score >= 50)"
    assert elseif_branch.body == dedent(
        """\
        {
            $label = "silver";
        }"""
    )

    else_branch = unit_at_line(formatting, 15)
    assert else_branch.end_line == 19
    assert else_branch.context == "else"
    assert else_branch.body == dedent(
        """\
        {
            $label = "bronze";
            $score = 0;
        }"""
    )


def test_extracts_function_and_loop_with_multiline_headers():
    formatting = parse((FIXTURES / "Formatting.php").read_bytes())

    product = unit_at_line(formatting, 23)
    assert product.end_line == 36
    assert product.context == dedent(
        """\
        function product(
            array $factors,
            int $start
        ): int"""
    )

    loop = unit_at_line(formatting, 28)
    assert loop.end_line == 34
    assert loop.context == dedent(
        """\
        for (
            $i = $start;
            $i < count($factors);
            $i++
        )"""
    )
    assert loop.body == dedent(
        """\
        {
            $total *= $factors[$i];
        }"""
    )


def test_replaces_invalid_utf8_bytes_and_extracts_surrounding_function():
    units = parse(b'<?php\nfunction greet() {\n    return "a\xffb";\n}\n')

    greet = unit_at_line(units, 2)
    assert greet.context == "function greet()"
    assert greet.body == dedent(
        """\
        {
            return "a�b";
        }"""
    )
