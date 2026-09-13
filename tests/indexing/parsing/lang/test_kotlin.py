from pathlib import Path
from textwrap import dedent

from slopo.indexing.parsing.lang.kotlin import parse

from .conftest import unit_at_line

FIXTURES = Path(__file__).parent / "fixtures" / "kotlin"


def test_strips_line_block_and_kdoc_comments_keeping_blank_lines():
    unit = parse((FIXTURES / "Comments.kt").read_bytes())[0]

    assert unit.start_line == 6
    assert unit.end_line == 13
    assert unit.context == "fun withComments(a: Int, b: Int): Int"
    assert unit.body_node_count == 14
    assert unit.body == dedent(
        """\
        {

            val sum = a + b


            val url = "http://not-a-comment"
            return sum
        }"""
    )


def test_body_node_count_across_body_shapes():
    body_sizes = parse((FIXTURES / "BodySizes.kt").read_bytes())

    empty = unit_at_line(body_sizes, 3)
    assert empty.body_node_count == 1

    annotated = unit_at_line(body_sizes, 5)
    assert annotated.body_node_count == 33

    for_loop = unit_at_line(body_sizes, 8)
    assert for_loop.body_node_count == 16


def test_extracts_function_with_its_nested_blocks():
    functions = parse((FIXTURES / "Functions.kt").read_bytes())

    normalize = unit_at_line(functions, 11)
    assert normalize.end_line == 18
    assert normalize.kind == "function"
    assert normalize.context == "fun normalize(values: List<Double>): List<Double>"
    assert normalize.body == dedent(
        """\
        {
            val total = values.sum()
            val scaled = mutableListOf<Double>()
            for (value in values) {
                scaled.add(value / total)
            }
            return scaled
        }"""
    )

    loop = unit_at_line(functions, 14)
    assert loop.end_line == 16
    assert loop.kind == "block"
    assert loop.context == "for (value in values)"
    assert loop.body == dedent(
        """\
        {
            scaled.add(value / total)
        }"""
    )


def test_extracts_expression_and_block_bodied_functions():
    functions = parse((FIXTURES / "Functions.kt").read_bytes())

    greet = unit_at_line(functions, 3)
    assert greet.end_line == 3
    assert greet.context == "fun greet(name: String)"
    assert greet.body == '"$prefix, $name!"'

    classify = unit_at_line(functions, 5)
    assert classify.end_line == 9
    assert classify.context == "fun classify(n: Int): String"
    assert classify.body == dedent(
        """\
        when {
            n < 0 -> "negative"
            n == 0 -> "zero"
            else -> "positive"
        }"""
    )

    sum_evens = unit_at_line(functions, 21)
    assert sum_evens.end_line == 22
    assert sum_evens.context == "fun List<Int>.sumEvens(): Int"
    assert sum_evens.body == "filter { it % 2 == 0 }.sum()"

    salute = unit_at_line(functions, 24)
    assert salute.end_line == 28
    assert salute.context == dedent(
        """\
        @Deprecated("prefer greet")
        fun salute(name: String): String"""
    )
    assert salute.body == dedent(
        """\
        {
            val trimmed = name.trim()
            return "Hi, $trimmed"
        }"""
    )


def test_extracts_functions_from_class_and_companion_object():
    nested = parse((FIXTURES / "Nested.kt").read_bytes())

    assert len(nested) == 2

    outer = unit_at_line(nested, 3)
    assert outer.end_line == 3
    assert outer.context == "fun outerMethod()"
    assert outer.body == 'println("outer")'

    inner = unit_at_line(nested, 6)
    assert inner.end_line == 6
    assert inner.context == "fun innerMethod()"
    assert inner.body == 'println("inner")'


def test_extracts_local_function_alongside_enclosing_function():
    nested_in_body = parse((FIXTURES / "NestedInBody.kt").read_bytes())

    assert len(nested_in_body) == 2

    outer = unit_at_line(nested_in_body, 1)
    assert outer.end_line == 6
    assert outer.context == "fun outerFunction(items: List<Int>): Int"
    assert outer.body == dedent(
        """\
        {
            fun localFunction(x: Int): Int {
                return x + 1
            }
            return items.get(0)
        }"""
    )

    local = unit_at_line(nested_in_body, 2)
    assert local.end_line == 4
    assert local.context == "fun localFunction(x: Int): Int"
    assert local.body == dedent(
        """\
        {
            return x + 1
        }"""
    )


def test_extracts_property_accessors_and_secondary_constructor_and_init():
    members = parse((FIXTURES / "Members.kt").read_bytes())

    assert len(members) == 4

    getter = unit_at_line(members, 4)
    assert getter.end_line == 6
    assert getter.kind == "function"
    assert getter.context == "get()"
    assert getter.body == dedent(
        """\
        {
            return field
        }"""
    )

    setter = unit_at_line(members, 7)
    assert setter.end_line == 9
    assert setter.kind == "function"
    assert setter.context == "set(value)"
    assert setter.body == dedent(
        """\
        {
            field = value.coerceAtLeast(0)
        }"""
    )

    initializer = unit_at_line(members, 11)
    assert initializer.end_line == 13
    assert initializer.kind == "function"
    assert initializer.context == "init"
    assert initializer.body == dedent(
        """\
        {
            balance = balance + initial
        }"""
    )

    constructor = unit_at_line(members, 15)
    assert constructor.end_line == 17
    assert constructor.kind == "function"
    assert (
        constructor.context == "constructor(initial: Int, bonus: Int) : this(initial)"
    )
    assert constructor.body == dedent(
        """\
        {
            balance = balance + bonus
        }"""
    )


def test_extracts_anonymous_functions_and_lambdas_with_context():
    lambdas = parse((FIXTURES / "Lambdas.kt").read_bytes())

    assert len(lambdas) == 8

    doubler = unit_at_line(lambdas, 7)
    assert doubler.end_line == 7
    assert doubler.context == "val doubler = fun(x: Int): Int"
    assert doubler.body == "{ return x * 2 }"

    filtered = unit_at_line(lambdas, 9)
    assert filtered.end_line == 9
    assert filtered.context == "filter"
    assert filtered.body == "{ it > 0 }"

    mapped = unit_at_line(lambdas, 10)
    assert mapped.end_line == 13
    assert mapped.context == "fun(v: Int): Int"
    assert mapped.body == dedent(
        """\
        {
            val scaled = doubler(v)
            return scaled + 1
        }"""
    )

    on_complete = unit_at_line(lambdas, 17)
    assert on_complete.end_line == 19
    assert on_complete.context == "this.onComplete = fun()"
    assert on_complete.body == dedent(
        """\
        {
            println("done")
        }"""
    )

    folded = unit_at_line(lambdas, 23)
    assert folded.end_line == 25
    assert folded.context == "fold acc, v ->"
    assert folded.body == dedent(
        """\
        {
            acc + v
        }"""
    )


def test_nested_lambda_extracted_alongside_enclosing_function():
    lambdas = parse((FIXTURES / "Lambdas.kt").read_bytes())

    transform = unit_at_line(lambdas, 6)
    assert transform.end_line == 14
    assert transform.context == "fun transform(values: List<Int>): List<Int>"
    assert transform.body == dedent(
        """\
        {
            val doubler = fun(x: Int): Int { return x * 2 }
            return values
                .filter { it > 0 }
                .map(fun(v: Int): Int {
                    val scaled = doubler(v)
                    return scaled + 1
                })
        }"""
    )

    nested = unit_at_line(lambdas, 10)
    assert nested.end_line == 13
    assert nested.context == "fun(v: Int): Int"
    assert nested.body == dedent(
        """\
        {
            val scaled = doubler(v)
            return scaled + 1
        }"""
    )


def test_extracts_conditional_branches():
    conditionals = parse((FIXTURES / "Conditionals.kt").read_bytes())

    assert len(conditionals) == 7

    if_branch = unit_at_line(conditionals, 5)
    assert if_branch.end_line == 8
    assert if_branch.context == "if (score >= 90)"
    assert if_branch.body == dedent(
        """\
        {
            tier = "gold"
            return tier + score
        }"""
    )

    else_if_branch = unit_at_line(conditionals, 8)
    assert else_if_branch.end_line == 10
    assert else_if_branch.context == "if (score >= 50)"
    assert else_if_branch.body == dedent(
        """\
        {
            tier = "silver"
        }"""
    )

    else_branch = unit_at_line(conditionals, 10)
    assert else_branch.end_line == 13
    assert else_branch.context == "else"
    assert else_branch.body == dedent(
        """\
        {
            tier = "bronze"
            tier = tier + "!"
        }"""
    )

    below_min = unit_at_line(conditionals, 19)
    assert below_min.end_line == 22
    assert below_min.context == "if (value < min)"
    assert below_min.body == dedent(
        """\
        {
            val deficit = min - value
            adjusted = min + deficit / 2
        }"""
    )

    above_max = unit_at_line(conditionals, 23)
    assert above_max.end_line == 26
    assert above_max.context == "if (value > max)"
    assert above_max.body == dedent(
        """\
        {
            adjusted = max
            return adjusted - 1
        }"""
    )


def test_extracts_loop_bodies():
    loops = parse((FIXTURES / "Loops.kt").read_bytes())

    assert len(loops) == 6

    for_loop = unit_at_line(loops, 5)
    assert for_loop.end_line == 8
    assert for_loop.context == "for (part in parts)"
    assert for_loop.body == dedent(
        """\
        {
            out.append(part)
            out.append(",")
        }"""
    )

    while_loop = unit_at_line(loops, 16)
    assert while_loop.end_line == 21
    assert while_loop.context == "while (count > 0)"
    assert while_loop.body == dedent(
        """\
        {
            val next = a + b
            a = b
            b = next
            count -= 1
        }"""
    )

    do_while = unit_at_line(loops, 28)
    assert do_while.end_line == 31
    assert do_while.context == "do"
    assert do_while.body == dedent(
        """\
        {
            value /= 10
            count += 1
        }"""
    )


def test_extracts_when_entries_including_braceless_multiline_arm():
    when_fixture = parse((FIXTURES / "When.kt").read_bytes())

    assert len(when_fixture) == 8

    arm_a = unit_at_line(when_fixture, 6)
    assert arm_a.end_line == 9
    assert arm_a.context == '"A" ->'
    assert arm_a.body == dedent(
        """\
        {
            score = 4
            score = score * 10
        }"""
    )

    arm_b = unit_at_line(when_fixture, 10)
    assert arm_b.end_line == 13
    assert arm_b.context == '"B" ->'
    assert arm_b.body == dedent(
        """\
        {
            score = 3
            score = score + 1
        }"""
    )

    arm_else = unit_at_line(when_fixture, 14)
    assert arm_else.end_line == 16
    assert arm_else.context == "else ->"
    assert arm_else.body == dedent(
        """\
        {
            score = 0
        }"""
    )

    subjectless_block = unit_at_line(when_fixture, 24)
    assert subjectless_block.end_line == 27
    assert subjectless_block.context == "values.sum() > 100 ->"
    assert subjectless_block.body == dedent(
        """\
        {
            val total = values.sum()
            "big:$total"
        }"""
    )

    braceless_multiline = unit_at_line(when_fixture, 28)
    assert braceless_multiline.end_line == 30
    assert braceless_multiline.context == "else ->"
    assert braceless_multiline.body == dedent(
        """\
        values
        .max()
        .toString()"""
    )


def test_extracts_exception_handling_blocks():
    exceptions = parse((FIXTURES / "Exceptions.kt").read_bytes())

    assert len(exceptions) == 8

    try_body = unit_at_line(exceptions, 5)
    assert try_body.end_line == 8
    assert try_body.context == "try"
    assert try_body.body == dedent(
        """\
        {
            value = text.toInt()
            value = value * 2
        }"""
    )

    catch_body = unit_at_line(exceptions, 8)
    assert catch_body.end_line == 11
    assert catch_body.context == "catch (e: NumberFormatException)"
    assert catch_body.body == dedent(
        """\
        {
            value = 0
            value = value - 1
        }"""
    )

    finally_body = unit_at_line(exceptions, 11)
    assert finally_body.end_line == 13
    assert finally_body.context == "finally"
    assert finally_body.body == dedent(
        """\
        {
            value = value + 1
        }"""
    )

    first_catch = unit_at_line(exceptions, 21)
    assert first_catch.end_line == 24
    assert first_catch.context == "catch (e: IndexOutOfBoundsException)"
    assert first_catch.body == dedent(
        """\
        {
            result = fallback
            result = result - 1
        }"""
    )

    second_catch = unit_at_line(exceptions, 24)
    assert second_catch.end_line == 26
    assert second_catch.context == "catch (e: NullPointerException)"
    assert second_catch.body == dedent(
        """\
        {
            result = 0
        }"""
    )


def test_extracts_nested_blocks_with_full_body_and_context():
    nesting = parse((FIXTURES / "NestedBlocks.kt").read_bytes())

    loop = unit_at_line(nesting, 5)
    assert loop.end_line == 13
    assert loop.context == "for (x in xs)"
    assert loop.body_node_count == 25
    assert loop.body == dedent(
        """\
        {
            if (x > threshold) {
                try {
                    total = total + 100 / x
                } catch (e: ArithmeticException) {
                    total = total - 1
                }
            }
        }"""
    )

    conditional = unit_at_line(nesting, 6)
    assert conditional.end_line == 12
    assert conditional.context == "if (x > threshold)"
    assert conditional.body_node_count == 20
    assert conditional.body == dedent(
        """\
        {
            try {
                total = total + 100 / x
            } catch (e: ArithmeticException) {
                total = total - 1
            }
        }"""
    )

    try_body = unit_at_line(nesting, 7)
    assert try_body.end_line == 9
    assert try_body.context == "try"
    assert try_body.body_node_count == 8
    assert try_body.body == dedent(
        """\
        {
            total = total + 100 / x
        }"""
    )

    catch_body = unit_at_line(nesting, 9)
    assert catch_body.end_line == 11
    assert catch_body.context == "catch (e: ArithmeticException)"
    assert catch_body.body_node_count == 6
    assert catch_body.body == dedent(
        """\
        {
            total = total - 1
        }"""
    )


def test_extracts_multiline_signature_and_loop_header():
    formatting = parse((FIXTURES / "Formatting.kt").read_bytes())

    product = unit_at_line(formatting, 3)
    assert product.end_line == 13
    assert product.context == dedent(
        """\
        fun product(
            factors: IntArray,
            start: Int
        ): Long"""
    )

    loop = unit_at_line(formatting, 8)
    assert loop.end_line == 11
    assert loop.context == dedent(
        """\
        for (i in
        start until factors.size)"""
    )
    assert loop.body == dedent(
        """\
        {
            total *= factors[i]
        }"""
    )


def test_extracts_allman_braced_function_and_conditional_branches():
    formatting = parse((FIXTURES / "Formatting.kt").read_bytes())

    tier = unit_at_line(formatting, 15)
    assert tier.end_line == 29
    assert tier.context == "fun tier(score: Int): String"

    if_branch = unit_at_line(formatting, 18)
    assert if_branch.end_line == 22
    assert if_branch.context == "if (score >= 90)"
    assert if_branch.body == dedent(
        """\
        {
            label = "gold"
            label.uppercase()
        }"""
    )

    else_branch = unit_at_line(formatting, 23)
    assert else_branch.end_line == 27
    assert else_branch.context == "else"
    assert else_branch.body == dedent(
        """\
        {
            label = "bronze"
            label.lowercase()
        }"""
    )


def test_replaces_invalid_utf8_bytes_and_extracts_surrounding_function():
    units = parse(b'fun greet(): String {\n    return "a\xffb"\n}\n')

    greet = unit_at_line(units, 1)
    assert greet.context == "fun greet(): String"
    assert greet.body == dedent(
        """\
        {
            return "a�b"
        }"""
    )
