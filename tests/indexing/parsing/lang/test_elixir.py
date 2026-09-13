from pathlib import Path
from textwrap import dedent

from slopo.indexing.parsing.lang.elixir import parse

from .conftest import unit_at_line

FIXTURES = Path(__file__).parent / "fixtures" / "elixir"


def test_strips_line_comment_keeping_hash_in_string_and_blank_lines():
    unit = parse((FIXTURES / "Comments.ex").read_bytes())[0]

    assert unit.start_line == 3
    assert unit.end_line == 8
    assert unit.context == "def with_comments(a, b)"
    assert unit.body_node_count == 11
    assert unit.body == dedent(
        """\
        do

          sum = a + b
          url = "http://example.com#section"
          sum
        end"""
    )


def test_body_node_count_across_body_shapes():
    body_sizes = parse((FIXTURES / "BodySizes.ex").read_bytes())

    keyword = unit_at_line(body_sizes, 2)
    assert keyword.body_node_count == 1

    empty = unit_at_line(body_sizes, 4)
    assert empty.body_node_count == 1

    pipeline = unit_at_line(body_sizes, 7)
    assert pipeline.body_node_count == 28


def test_extracts_blocks_with_enclosing_function():
    units = parse((FIXTURES / "Conditionals.ex").read_bytes())

    categorize = unit_at_line(units, 2)
    assert categorize.end_line == 12
    assert categorize.kind == "function"
    assert categorize.context == "def categorize(score)"
    assert categorize.body == dedent(
        """\
        do
          if score >= 90 do
            tier = "gold"
            bonus = score - 90
            {tier, bonus}
          else
            tier = "bronze"
            penalty = 90 - score
            {tier, penalty}
          end
        end"""
    )

    if_branch = unit_at_line(units, 3)
    assert if_branch.end_line == 6
    assert if_branch.kind == "block"
    assert if_branch.context == "if score >= 90 do"
    assert if_branch.body == dedent(
        """\
        tier = "gold"
        bonus = score - 90
        {tier, bonus}"""
    )

    else_branch = unit_at_line(units, 7)
    assert else_branch.end_line == 10
    assert else_branch.kind == "block"
    assert else_branch.context == "else"
    assert else_branch.body == dedent(
        """\
        tier = "bronze"
        penalty = 90 - score
        {tier, penalty}"""
    )


def test_extracts_public_and_private_functions():
    functions = parse((FIXTURES / "Functions.ex").read_bytes())

    add = unit_at_line(functions, 4)
    assert add.end_line == 6
    assert add.context == "def add(a, b)"
    assert add.body == dedent(
        """\
        do
          a + b
        end"""
    )

    greet = unit_at_line(functions, 8)
    assert greet.end_line == 10
    assert greet.context == "def greet(name)"
    assert greet.body == dedent(
        """\
        do
          "Hello, #{name}!"
        end"""
    )

    normalize = unit_at_line(functions, 12)
    assert normalize.end_line == 16
    assert normalize.context == "defp normalize(value) when is_binary(value)"
    assert normalize.body == dedent(
        """\
        do
          value
          |> String.trim()
          |> String.downcase()
        end"""
    )

    repeat = unit_at_line(functions, 18)
    assert repeat.end_line == 18
    assert repeat.context == "def repeat(text, count), do:"
    assert repeat.body == "String.duplicate(text, count)"


def test_extracts_functions_from_outer_and_nested_module():
    nested = parse((FIXTURES / "Nested.ex").read_bytes())

    assert len(nested) == 2

    outer = unit_at_line(nested, 2)
    assert outer.end_line == 4
    assert outer.context == "def outer_fun(x)"
    assert outer.body == dedent(
        """\
        do
          x * 2
        end"""
    )

    inner = unit_at_line(nested, 7)
    assert inner.end_line == 9
    assert inner.context == "def inner_fun(y)"
    assert inner.body == dedent(
        """\
        do
          y + 1
        end"""
    )


def test_extracts_anonymous_functions_alongside_enclosing_functions():
    nested_in_body = parse((FIXTURES / "NestedInBody.ex").read_bytes())

    make_task = unit_at_line(nested_in_body, 2)
    assert make_task.end_line == 6
    assert make_task.kind == "function"
    assert make_task.context == "def make_task(label)"
    assert make_task.body == dedent(
        """\
        do
          fn ->
            IO.puts(label)
          end
        end"""
    )

    block_closure = unit_at_line(nested_in_body, 3)
    assert block_closure.end_line == 5
    assert block_closure.kind == "function"
    assert block_closure.context == "fn ->"
    assert block_closure.body == "IO.puts(label)"


def test_extracts_bound_and_callback_closures_alongside_enclosing_function():
    closures = parse((FIXTURES / "Closures.ex").read_bytes())

    assert len(closures) == 3

    build = unit_at_line(closures, 2)
    assert build.end_line == 5
    assert build.context == "def build"
    assert build.body == dedent(
        """\
        do
          doubler = fn x -> x * 2 end
          Enum.map([1, 2, 3], fn v -> doubler.(v) + 1 end)
        end"""
    )

    bound = unit_at_line(closures, 3)
    assert bound.end_line == 3
    assert bound.kind == "function"
    assert bound.context == "doubler = fn x ->"
    assert bound.body == "x * 2"

    callback = unit_at_line(closures, 4)
    assert callback.end_line == 4
    assert callback.kind == "function"
    assert callback.context == "Enum.map fn"
    assert callback.body == "doubler.(v) + 1"


def test_extracts_conditional_branches():
    conditionals = parse((FIXTURES / "Conditionals.ex").read_bytes())

    assert len(conditionals) == 6

    if_branch = unit_at_line(conditionals, 3)
    assert if_branch.end_line == 6
    assert if_branch.context == "if score >= 90 do"
    assert if_branch.body == dedent(
        """\
        tier = "gold"
        bonus = score - 90
        {tier, bonus}"""
    )

    else_branch = unit_at_line(conditionals, 7)
    assert else_branch.end_line == 10
    assert else_branch.context == "else"
    assert else_branch.body == dedent(
        """\
        tier = "bronze"
        penalty = 90 - score
        {tier, penalty}"""
    )

    if_only = unit_at_line(conditionals, 15)
    assert if_only.end_line == 18
    assert if_only.context == "if value < lo do"
    assert if_only.body == dedent(
        """\
        deficit = lo - value
        adjusted = lo + div(deficit, 2)
        adjusted"""
    )

    unless_branch = unit_at_line(conditionals, 21)
    assert unless_branch.end_line == 24
    assert unless_branch.context == "unless value > hi do"
    assert unless_branch.body == dedent(
        """\
        surplus = value - hi
        capped = hi - abs(surplus)
        capped"""
    )


def test_extracts_case_arms():
    cases = parse((FIXTURES / "Case.ex").read_bytes())

    assert len(cases) == 4

    ok_arm = unit_at_line(cases, 4)
    assert ok_arm.end_line == 7
    assert ok_arm.context == "{:ok, value} ->"
    assert ok_arm.body == dedent(
        """\
        processed = value * 2
        log(processed)
        {:success, processed}"""
    )

    error_arm = unit_at_line(cases, 8)
    assert error_arm.end_line == 11
    assert error_arm.context == "{:error, reason} ->"
    assert error_arm.body == dedent(
        """\
        msg = format_error(reason)
        notify(msg)
        {:failure, msg}"""
    )

    timeout_arm = unit_at_line(cases, 12)
    assert timeout_arm.end_line == 13
    assert timeout_arm.context == ":timeout ->"
    assert timeout_arm.body == ":retry"


def test_extracts_cond_arms():
    conds = parse((FIXTURES / "Cond.ex").read_bytes())

    assert len(conds) == 4

    big = unit_at_line(conds, 4)
    assert big.end_line == 7
    assert big.context == "x > 100 ->"
    assert big.body == dedent(
        """\
        label = "huge"
        weight = x * 10
        {label, weight}"""
    )

    positive = unit_at_line(conds, 8)
    assert positive.end_line == 11
    assert positive.context == "x > 0 ->"
    assert positive.body == dedent(
        """\
        label = "positive"
        weight = x
        {label, weight}"""
    )

    fallback = unit_at_line(conds, 12)
    assert fallback.end_line == 15
    assert fallback.context == "true ->"
    assert fallback.body == dedent(
        """\
        label = "non-positive"
        weight = 0
        {label, weight}"""
    )


def test_extracts_try_rescue_catch_after():
    tries = parse((FIXTURES / "Try.ex").read_bytes())

    assert len(tries) == 5

    try_body = unit_at_line(tries, 3)
    assert try_body.end_line == 6
    assert try_body.context == "try do"
    assert try_body.body == dedent(
        """\
        value = String.to_integer(text)
        value = value * 2
        {:ok, value}"""
    )

    rescue_arm = unit_at_line(tries, 8)
    assert rescue_arm.end_line == 11
    assert rescue_arm.context == "e in ArgumentError ->"
    assert rescue_arm.body == dedent(
        """\
        msg = Exception.message(e)
        Logger.warn(msg)
        {:error, msg}"""
    )

    catch_arm = unit_at_line(tries, 13)
    assert catch_arm.end_line == 16
    assert catch_arm.context == ":exit, reason ->"
    assert catch_arm.body == dedent(
        """\
        detail = inspect(reason)
        Logger.error(detail)
        {:crash, detail}"""
    )

    after_block = unit_at_line(tries, 17)
    assert after_block.end_line == 19
    assert after_block.context == "after"
    assert after_block.body == dedent(
        """\
        IO.puts("done")
        flush()"""
    )


def test_extracts_for_comprehension_bodies():
    fors = parse((FIXTURES / "For.ex").read_bytes())

    assert len(fors) == 3

    filtered = unit_at_line(fors, 3)
    assert filtered.end_line == 6
    assert filtered.context == "for item <- items, item > 0 do"
    assert filtered.body == dedent(
        """\
        doubled = item * 2
        label = "item_#{doubled}"
        {label, doubled}"""
    )

    destructured = unit_at_line(fors, 9)
    assert destructured.end_line == 11
    assert destructured.context == "for {k, v} <- items, v != nil do"
    assert destructured.body == dedent(
        """\
        processed = String.upcase(k)
        {processed, v + 1}"""
    )


def test_extracts_receive_arms_with():
    receives = parse((FIXTURES / "Receive.ex").read_bytes())

    assert len(receives) == 5

    data_arm = unit_at_line(receives, 4)
    assert data_arm.end_line == 7
    assert data_arm.context == "{:data, payload} ->"
    assert data_arm.body == dedent(
        """\
        parsed = decode(payload)
        process(parsed)
        {:ok, parsed}"""
    )

    batch_arm = unit_at_line(receives, 8)
    assert batch_arm.end_line == 10
    assert batch_arm.context == "{:batch, items} ->"
    assert batch_arm.body == dedent(
        """\
        results = Enum.map(items, &handle/1)
        {:ok, results}"""
    )

    stop_arm = unit_at_line(receives, 11)
    assert stop_arm.end_line == 12
    assert stop_arm.context == ":stop ->"
    assert stop_arm.body == ":halted"

    after_arm = unit_at_line(receives, 14)
    assert after_arm.end_line == 15
    assert after_arm.context == "5000 ->"
    assert after_arm.body == ":timeout"


def test_extracts_with_body_and_else_arms():
    withs = parse((FIXTURES / "With.ex").read_bytes())

    assert len(withs) == 4

    do_body = unit_at_line(withs, 3)
    assert do_body.end_line == 7
    assert do_body.context == dedent(
        """\
        with {:ok, a} <- fetch(input),
        {:ok, b} <- transform(a) do"""
    )
    assert do_body.body == dedent(
        """\
        result = a + b
        format(result)
        {:ok, result}"""
    )

    error_arm = unit_at_line(withs, 9)
    assert error_arm.end_line == 12
    assert error_arm.context == "{:error, reason} ->"
    assert error_arm.body == dedent(
        """\
        msg = format_error(reason)
        notify(msg)
        {:failure, msg}"""
    )

    not_found_arm = unit_at_line(withs, 13)
    assert not_found_arm.end_line == 14
    assert not_found_arm.context == ":not_found ->"
    assert not_found_arm.body == ":missing"


def test_extracts_nested_blocks():
    nesting = parse((FIXTURES / "NestedBlocks.ex").read_bytes())

    for_block = unit_at_line(nesting, 3)
    assert for_block.end_line == 13
    assert for_block.context == "for item <- items do"
    assert for_block.body_node_count == 43
    assert for_block.body == dedent(
        """\
        if item > 0 do
          try do
            total = 100 + div(1000, item)
            {:ok, total}
          rescue
            e in ArithmeticError ->
              Logger.warn(Exception.message(e))
              {:error, :overflow}
          end
        end"""
    )

    if_block = unit_at_line(nesting, 4)
    assert if_block.end_line == 12
    assert if_block.context == "if item > 0 do"
    assert if_block.body_node_count == 36
    assert if_block.body == dedent(
        """\
        try do
          total = 100 + div(1000, item)
          {:ok, total}
        rescue
          e in ArithmeticError ->
            Logger.warn(Exception.message(e))
            {:error, :overflow}
        end"""
    )

    try_body = unit_at_line(nesting, 5)
    assert try_body.end_line == 7
    assert try_body.context == "try do"
    assert try_body.body_node_count == 12
    assert try_body.body == dedent(
        """\
        total = 100 + div(1000, item)
        {:ok, total}"""
    )

    rescue_arm = unit_at_line(nesting, 9)
    assert rescue_arm.end_line == 11
    assert rescue_arm.context == "e in ArithmeticError ->"
    assert rescue_arm.body_node_count == 14
    assert rescue_arm.body == dedent(
        """\
        Logger.warn(Exception.message(e))
        {:error, :overflow}"""
    )


def test_replaces_invalid_utf8_bytes_and_extracts_surrounding_function():
    units = parse(b'defmodule M do\n  def greet do\n    "a\xffb"\n  end\nend\n')

    greet = unit_at_line(units, 2)
    assert greet.context == "def greet"
    assert greet.body == dedent(
        """\
        do
          "a�b"
        end"""
    )
