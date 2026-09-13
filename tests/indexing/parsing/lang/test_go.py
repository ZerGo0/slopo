from pathlib import Path
from textwrap import dedent

from slopo.indexing.parsing.lang.go import parse

from .conftest import unit_at_line

FIXTURES = Path(__file__).parent / "fixtures" / "go"


def test_strips_line_and_block_comments_keeping_blank_lines():
    unit = parse((FIXTURES / "Comments.go").read_bytes())[0]

    assert unit.start_line == 5
    assert unit.end_line == 11
    assert unit.context == "func WithComments(a, b int) int"
    assert unit.body_node_count == 23
    assert unit.body == dedent(
        """\
        {

                sum := a + b
                url := "http://not-a-comment"
                _ = url
                return sum
        }"""
    )


def test_body_node_count_across_body_shapes():
    body_sizes = parse((FIXTURES / "BodySizes.go").read_bytes())

    empty = unit_at_line(body_sizes, 3)
    assert empty.body_node_count == 1

    with_logic = unit_at_line(body_sizes, 5)
    assert with_logic.body_node_count == 47


def test_extracts_function_together_with_its_nested_blocks():
    functions = parse((FIXTURES / "Functions.go").read_bytes())

    sum_evens = unit_at_line(functions, 18)
    assert sum_evens.end_line == 26
    assert sum_evens.kind == "function"
    assert sum_evens.context == "func SumEvens(nums []int) int"
    assert sum_evens.body == dedent(
        """\
        {
                total := 0
                for _, n := range nums {
                        if n%2 == 0 {
                                total += n
                        }
                }
                return total
        }"""
    )

    loop = unit_at_line(functions, 20)
    assert loop.end_line == 24
    assert loop.kind == "block"
    assert loop.context == "for _, n := range nums"
    assert loop.body == dedent(
        """\
        {
                if n%2 == 0 {
                        total += n
                }
        }"""
    )

    branch = unit_at_line(functions, 21)
    assert branch.end_line == 23
    assert branch.kind == "block"
    assert branch.context == "if n%2 == 0"
    assert branch.body == dedent(
        """\
        {
                total += n
        }"""
    )


def test_extracts_method_and_top_level_functions_with_full_body():
    functions = parse((FIXTURES / "Functions.go").read_bytes())

    greet = unit_at_line(functions, 9)
    assert greet.end_line == 16
    assert greet.context == "func (g Greeter) Greet(name string, loud bool) string"
    assert greet.body == dedent(
        """\
        {
                greeting := g.prefix + ", " + name
                if loud {
                        greeting = strings.ToUpper(greeting)
                        greeting = greeting + "!"
                }
                return greeting
        }"""
    )

    normalize = unit_at_line(functions, 28)
    assert normalize.end_line == 31
    assert normalize.context == "func Normalize(s string) string"
    assert normalize.body == dedent(
        """\
        {
                trimmed := strings.TrimSpace(s)
                return strings.ToLower(trimmed)
        }"""
    )


def test_labels_func_literal_with_binding_and_signature():
    closures = parse((FIXTURES / "Closures.go").read_bytes())

    assert len(closures) == 5

    doubler = unit_at_line(closures, 8)
    assert doubler.end_line == 11
    assert doubler.context == "doubler := func(x int) int"
    assert doubler.body == dedent(
        """\
        {
                scaled := x * 2
                return scaled
        }"""
    )

    on_complete = unit_at_line(closures, 14)
    assert on_complete.end_line == 17
    assert on_complete.context == "w.onComplete = func()"
    assert on_complete.body == dedent(
        """\
        {
                println("done")
                println("really done")
        }"""
    )

    callback = unit_at_line(closures, 19)
    assert callback.end_line == 22
    assert callback.context == "func(v int) int"
    assert callback.body == dedent(
        """\
        {
                scaled := doubler(v)
                return scaled + 1
        }"""
    )


def test_extracts_local_func_literal_alongside_enclosing_function():
    nested_in_body = parse((FIXTURES / "NestedInBody.go").read_bytes())

    assert len(nested_in_body) == 2

    outer = unit_at_line(nested_in_body, 3)
    assert outer.end_line == 9
    assert outer.context == "func OuterFunction(x int) int"
    assert outer.body == dedent(
        """\
        {
                increment := func(n int) int {
                        doubled := n * 2
                        return doubled + 1
                }
                return increment(x)
        }"""
    )

    increment = unit_at_line(nested_in_body, 4)
    assert increment.end_line == 7
    assert increment.context == "increment := func(n int) int"
    assert increment.body == dedent(
        """\
        {
                doubled := n * 2
                return doubled + 1
        }"""
    )


def test_extracts_conditional_branches():
    conditionals = parse((FIXTURES / "Conditionals.go").read_bytes())

    assert len(conditionals) == 7

    if_branch = unit_at_line(conditionals, 5)
    assert if_branch.end_line == 8
    assert if_branch.context == "if score >= 90"
    assert if_branch.body == dedent(
        """\
        {
                tier = "gold"
                return tier
        }"""
    )

    else_if_branch = unit_at_line(conditionals, 8)
    assert else_if_branch.end_line == 11
    assert else_if_branch.context == "if score >= 50"
    assert else_if_branch.body == dedent(
        """\
        {
                tier = "silver"
                tier = tier + "!"
        }"""
    )

    else_branch = unit_at_line(conditionals, 11)
    assert else_branch.end_line == 13
    assert else_branch.context == "else"
    assert else_branch.body == dedent(
        """\
        {
                tier = "bronze"
        }"""
    )

    below_min = unit_at_line(conditionals, 19)
    assert below_min.end_line == 22
    assert below_min.context == "if value < min"
    assert below_min.body == dedent(
        """\
        {
                deficit := min - value
                adjusted = min + deficit/2
        }"""
    )

    above_max = unit_at_line(conditionals, 23)
    assert above_max.end_line == 26
    assert above_max.context == "if value > max"
    assert above_max.body == dedent(
        """\
        {
                adjusted = max
                adjusted = adjusted - 1
        }"""
    )


def test_extracts_loop_bodies_across_for_forms():
    loops = parse((FIXTURES / "Loops.go").read_bytes())

    assert len(loops) == 6

    range_loop = unit_at_line(loops, 5)
    assert range_loop.end_line == 8
    assert range_loop.context == "for _, part := range parts"
    assert range_loop.body == dedent(
        """\
        {
                out = out + part
                out = out + ","
        }"""
    )

    clause_loop = unit_at_line(loops, 14)
    assert clause_loop.end_line == 18
    assert clause_loop.context == "for i := 0; i < count; i++"
    assert clause_loop.body == dedent(
        """\
        {
                next := a + b
                a = b
                b = next
        }"""
    )

    condition_loop = unit_at_line(loops, 24)
    assert condition_loop.end_line == 27
    assert condition_loop.context == "for value > 0"
    assert condition_loop.body == dedent(
        """\
        {
                value = value / 10
                steps = steps + 1
        }"""
    )


def test_extracts_expression_and_type_switch_cases():
    switches = parse((FIXTURES / "Switches.go").read_bytes())

    assert len(switches) == 8

    single = unit_at_line(switches, 5)
    assert single.end_line == 8
    assert single.context == "case 0:"
    assert single.body == dedent(
        """\
        out := "zero"
        return out"""
    )

    multi_value = unit_at_line(switches, 8)
    assert multi_value.end_line == 11
    assert multi_value.context == "case 1, 2:"
    assert multi_value.body == dedent(
        """\
        out := "small"
        return out + "!\""""
    )

    default = unit_at_line(switches, 11)
    assert default.end_line == 14
    assert default.context == "default:"
    assert default.body == dedent(
        """\
        out := "many"
        return out"""
    )

    typed = unit_at_line(switches, 19)
    assert typed.end_line == 22
    assert typed.context == "case int:"
    assert typed.body == dedent(
        """\
        doubled := x * 2
        return itoa(doubled)"""
    )

    typed_default = unit_at_line(switches, 25)
    assert typed_default.end_line == 27
    assert typed_default.context == "default:"
    assert typed_default.body == 'return "unknown"'


def test_extracts_select_communication_cases():
    select = parse((FIXTURES / "Select.go").read_bytes())

    assert len(select) == 4

    receive = unit_at_line(select, 6)
    assert receive.end_line == 9
    assert receive.context == "case v := <-ch:"
    assert receive.body == dedent(
        """\
        total = total + v
        total = total * 2"""
    )

    signal = unit_at_line(select, 9)
    assert signal.end_line == 12
    assert signal.context == "case <-done:"
    assert signal.body == dedent(
        """\
        total = -1
        return total"""
    )

    default = unit_at_line(select, 12)
    assert default.end_line == 14
    assert default.context == "default:"
    assert default.body == "total = 0"


def test_extracts_nested_blocks_with_full_body():
    nesting = parse((FIXTURES / "NestedBlocks.go").read_bytes())

    loop = unit_at_line(nesting, 5)
    assert loop.end_line == 15
    assert loop.context == "for _, x := range xs"
    assert loop.body_node_count == 38
    assert loop.body == dedent(
        """\
        {
                if x > threshold {
                        switch {
                        case x > 100:
                                total = total + 100
                                total = total - 1
                        default:
                                total = total + x
                        }
                }
        }"""
    )

    branch = unit_at_line(nesting, 6)
    assert branch.end_line == 14
    assert branch.context == "if x > threshold"
    assert branch.body_node_count == 32
    assert branch.body == dedent(
        """\
        {
                switch {
                case x > 100:
                        total = total + 100
                        total = total - 1
                default:
                        total = total + x
                }
        }"""
    )

    case = unit_at_line(nesting, 8)
    assert case.end_line == 11
    assert case.context == "case x > 100:"
    assert case.body_node_count == 15
    assert case.body == dedent(
        """\
        total = total + 100
        total = total - 1"""
    )


def test_extracts_multiline_signature():
    formatting = parse((FIXTURES / "Formatting.go").read_bytes())

    product = unit_at_line(formatting, 3)
    assert product.end_line == 12
    assert product.context == dedent(
        """\
        func product(
                factors []int,
                start int,
        ) int"""
    )
    assert product.body == dedent(
        """\
        {
                total := 1
                for i := start; i < len(factors); i++ {
                        total *= factors[i]
                }
                return total
        }"""
    )


def test_replaces_invalid_utf8_bytes_and_extracts_surrounding_function():
    units = parse(b'package main\n\nfunc greet() string {\n\treturn "a\xffb"\n}\n')

    greet = unit_at_line(units, 3)
    assert greet.context == "func greet() string"
    assert greet.body == dedent(
        """\
        {
                return "a�b"
        }"""
    )
