from pathlib import Path
from textwrap import dedent

from slopo.indexing.parsing.lang.typescript import parse

from .conftest import unit_at_line

FIXTURES = Path(__file__).parent / "fixtures" / "typescript"


def test_strips_line_block_and_doc_comments_keeping_blank_lines():
    unit = parse((FIXTURES / "Comments.ts").read_bytes())[0]

    assert unit.start_line == 6
    assert unit.end_line == 13
    assert unit.context == "function withComments(a: number, b: number): number"
    assert unit.body_node_count == 14
    assert unit.body == dedent(
        """\
        {

          const sum = a + b;


          const url = "https://not-a-comment";
          return sum;
        }"""
    )


def test_body_node_count_across_body_shapes():
    body_sizes = parse((FIXTURES / "BodySizes.ts").read_bytes())

    square = unit_at_line(body_sizes, 1)
    assert square.body_node_count == 3

    noop = unit_at_line(body_sizes, 3)
    assert noop.body_node_count == 1

    load_all = unit_at_line(body_sizes, 5)
    assert load_all.body_node_count == 46


def test_extracts_function_together_with_its_nested_blocks():
    functions = parse((FIXTURES / "Functions.ts").read_bytes())

    sum_evens = unit_at_line(functions, 18)
    assert sum_evens.end_line == 26
    assert sum_evens.kind == "function"
    assert sum_evens.context == "function sumEvens(nums: number[]): number"
    assert sum_evens.body == dedent(
        """\
        {
          let total = 0;
          for (const n of nums) {
            if (n % 2 === 0) {
              total += n;
            }
          }
          return total;
        }"""
    )

    loop = unit_at_line(functions, 20)
    assert loop.end_line == 24
    assert loop.kind == "block"
    assert loop.context == "for (const n of nums)"
    assert loop.body == dedent(
        """\
        {
          if (n % 2 === 0) {
            total += n;
          }
        }"""
    )


def test_extracts_declarations_generators_and_async():
    functions = parse((FIXTURES / "Functions.ts").read_bytes())

    add = unit_at_line(functions, 1)
    assert add.end_line == 3
    assert add.context == "function add(a: number, b: number): number"
    assert add.body == dedent(
        """\
        {
          return a + b;
        }"""
    )

    fetch_user = unit_at_line(functions, 5)
    assert fetch_user.end_line == 8
    assert fetch_user.context == "async function fetchUser(id: number): Promise<User>"
    assert fetch_user.body == dedent(
        """\
        {
          const response = await fetch(`/users/${id}`);
          return response.json();
        }"""
    )

    count_up = unit_at_line(functions, 10)
    assert count_up.end_line == 16
    assert count_up.context == "function* countUp(limit: number): Generator<number>"
    assert count_up.body == dedent(
        """\
        {
          let n = 0;
          while (n < limit) {
            yield n;
            n += 1;
          }
        }"""
    )


def test_extracts_class_method_variants():
    functions = parse((FIXTURES / "Functions.ts").read_bytes())

    constructor = unit_at_line(functions, 29)
    assert constructor.end_line == 31
    assert constructor.kind == "function"
    assert constructor.context == "constructor(start: number)"
    assert constructor.body == dedent(
        """\
        {
          this.value = start;
        }"""
    )

    getter = unit_at_line(functions, 38)
    assert getter.end_line == 40
    assert getter.kind == "function"
    assert getter.context == "get current(): number"
    assert getter.body == dedent(
        """\
        {
          return this.value;
        }"""
    )

    static_zero = unit_at_line(functions, 42)
    assert static_zero.end_line == 44
    assert static_zero.kind == "function"
    assert static_zero.context == "static zero(): Counter"
    assert static_zero.body == dedent(
        """\
        {
          return new Counter(0);
        }"""
    )

    load_from = unit_at_line(functions, 46)
    assert load_from.end_line == 49
    assert load_from.kind == "function"
    assert load_from.context == "async loadFrom(source: Source): Promise<void>"
    assert load_from.body == dedent(
        """\
        {
          const saved = await source.read();
          this.value = saved.value;
        }"""
    )


def test_labels_bound_and_unbound_anonymous_functions():
    closures = parse((FIXTURES / "Closures.ts").read_bytes())

    assert len(closures) == 5

    doubler = unit_at_line(closures, 2)
    assert doubler.end_line == 5
    assert doubler.context == "doubler = function (x: number): number"
    assert doubler.body == dedent(
        """\
        {
          const scaled = x * 2;
          return scaled;
        }"""
    )

    on_complete = unit_at_line(closures, 7)
    assert on_complete.end_line == 10
    assert on_complete.context == "worker.onComplete = (): void =>"
    assert on_complete.body == dedent(
        """\
        {
          log("done");
          log("really done");
        }"""
    )

    reset = unit_at_line(closures, 13)
    assert reset.end_line == 15
    assert reset.context == "reset: (): void =>"
    assert reset.body == dedent(
        """\
        {
          worker.value = 0;
        }"""
    )

    callback = unit_at_line(closures, 18)
    assert callback.end_line == 21
    assert callback.context == "(v: number): number =>"
    assert callback.body == dedent(
        """\
        {
          const scaled = doubler(v);
          return scaled + 1;
        }"""
    )


def test_extracts_expression_bodied_arrows():
    arrows = parse((FIXTURES / "ExpressionArrows.ts").read_bytes())

    assert len(arrows) == 2

    build_user = unit_at_line(arrows, 1)
    assert build_user.end_line == 5
    assert build_user.context == "buildUser = (raw: RawUser): User =>"
    assert build_user.body == dedent(
        """\
        ({
          id: raw.id,
          name: raw.first + " " + raw.last,
          active: raw.status === "on",
        })"""
    )

    classify = unit_at_line(arrows, 7)
    assert classify.end_line == 8
    assert classify.context == "classify = (score: number): string =>"
    assert classify.body == 'score >= 90 ? "gold" : score >= 50 ? "silver" : "bronze"'


def test_extracts_function_nested_in_function_body():
    nested = parse((FIXTURES / "NestedFunctions.ts").read_bytes())

    assert len(nested) == 2

    outer = unit_at_line(nested, 1)
    assert outer.end_line == 10
    assert outer.context == "function makeCounter(start: number): () => number"
    assert outer.body_node_count == 19
    assert outer.body == dedent(
        """\
        {
          let count = start;

          function increment(): number {
            count += 1;
            return count;
          }

          return increment;
        }"""
    )

    inner = unit_at_line(nested, 4)
    assert inner.end_line == 7
    assert inner.context == "function increment(): number"
    assert inner.body_node_count == 7
    assert inner.body == dedent(
        """\
        {
          count += 1;
          return count;
        }"""
    )


def test_skips_type_level_and_bodyless_signatures():
    type_level = parse((FIXTURES / "TypeLevel.ts").read_bytes())

    assert len(type_level) == 3

    render = unit_at_line(type_level, 17)
    assert render.end_line == 20
    assert render.context == "render(prefix: string, suffix: string): string"
    assert render.body == dedent(
        """\
        {
          const body = prefix + this.name;
          return body + suffix;
        }"""
    )

    overloaded = unit_at_line(type_level, 27)
    assert overloaded.end_line == 29
    assert overloaded.context == "function overloaded(x: unknown): unknown"
    assert overloaded.body == dedent(
        """\
        {
          return x;
        }"""
    )

    area = unit_at_line(type_level, 32)
    assert area.end_line == 34
    assert area.context == "function area(r: number): number"
    assert area.body == dedent(
        """\
        {
          return Math.PI * r * r;
        }"""
    )


def test_extracts_conditional_branches():
    conditionals = parse((FIXTURES / "Conditionals.ts").read_bytes())

    assert len(conditionals) == 7

    if_branch = unit_at_line(conditionals, 3)
    assert if_branch.end_line == 6
    assert if_branch.context == "if (score >= 90)"
    assert if_branch.body == dedent(
        """\
        {
          label = "gold";
          return label;
        }"""
    )

    else_if_branch = unit_at_line(conditionals, 6)
    assert else_if_branch.end_line == 9
    assert else_if_branch.context == "if (score >= 50)"
    assert else_if_branch.body == dedent(
        """\
        {
          label = "silver";
          label = label + "!";
        }"""
    )

    else_branch = unit_at_line(conditionals, 9)
    assert else_branch.end_line == 11
    assert else_branch.context == "else"
    assert else_branch.body == dedent(
        """\
        {
          label = "bronze";
        }"""
    )

    below_min = unit_at_line(conditionals, 17)
    assert below_min.end_line == 20
    assert below_min.context == "if (value < min)"
    assert below_min.body == dedent(
        """\
        {
          const deficit = min - value;
          adjusted = min + deficit / 2;
        }"""
    )

    above_max = unit_at_line(conditionals, 21)
    assert above_max.end_line == 24
    assert above_max.context == "if (value > max)"
    assert above_max.body == dedent(
        """\
        {
          adjusted = max;
          adjusted = adjusted - 1;
        }"""
    )


def test_extracts_loop_bodies_across_forms():
    loops = parse((FIXTURES / "Loops.ts").read_bytes())

    assert len(loops) == 8

    for_of = unit_at_line(loops, 3)
    assert for_of.end_line == 6
    assert for_of.context == "for (const part of parts)"
    assert for_of.body == dedent(
        """\
        {
          out = out + part;
          out = out + ",";
        }"""
    )

    clause_loop = unit_at_line(loops, 13)
    assert clause_loop.end_line == 17
    assert clause_loop.context == "for (let i = 0; i < count; i++)"
    assert clause_loop.body == dedent(
        """\
        {
          const next = a + b;
          a = b;
          b = next;
        }"""
    )

    while_loop = unit_at_line(loops, 23)
    assert while_loop.end_line == 26
    assert while_loop.context == "while (value > 0)"
    assert while_loop.body == dedent(
        """\
        {
          value = Math.floor(value / 10);
          steps = steps + 1;
        }"""
    )

    do_loop = unit_at_line(loops, 32)
    assert do_loop.end_line == 35
    assert do_loop.context == "do"
    assert do_loop.body == dedent(
        """\
        {
          task();
          attempts = attempts + 1;
        }"""
    )


def test_extracts_switch_case_and_default_bodies():
    switches = parse((FIXTURES / "Switches.ts").read_bytes())

    assert len(switches) == 4

    single = unit_at_line(switches, 4)
    assert single.end_line == 6
    assert single.context == "case 0:"
    assert single.body == dedent(
        """\
        out = "zero";
        return out;"""
    )

    fall_through = unit_at_line(switches, 8)
    assert fall_through.end_line == 10
    assert fall_through.context == "case 2:"
    assert fall_through.body == dedent(
        """\
        out = "small";
        return out + "!";"""
    )

    default = unit_at_line(switches, 11)
    assert default.end_line == 13
    assert default.context == "default:"
    assert default.body == dedent(
        """\
        out = "many";
        return out;"""
    )


def test_extracts_try_catch_and_finally_blocks():
    try_catch = parse((FIXTURES / "TryCatch.ts").read_bytes())

    assert len(try_catch) == 4

    try_block = unit_at_line(try_catch, 3)
    assert try_block.end_line == 6
    assert try_block.context == "try"
    assert try_block.body == dedent(
        """\
        {
          result = parse(payload);
          result.validate();
        }"""
    )

    catch_block = unit_at_line(try_catch, 6)
    assert catch_block.end_line == 9
    assert catch_block.context == "catch (err)"
    assert catch_block.body == dedent(
        """\
        {
          log(err);
          result = fallback();
        }"""
    )

    finally_block = unit_at_line(try_catch, 9)
    assert finally_block.end_line == 12
    assert finally_block.context == "finally"
    assert finally_block.body == dedent(
        """\
        {
          cleanup();
          release();
        }"""
    )


def test_extracts_nested_blocks():
    nesting = parse((FIXTURES / "NestedBlocks.ts").read_bytes())

    loop = unit_at_line(nesting, 3)
    assert loop.end_line == 14
    assert loop.context == "for (const x of xs)"
    assert loop.body_node_count == 35
    assert loop.body == dedent(
        """\
        {
          if (x > threshold) {
            switch (x % 2) {
              case 0:
                total = total + 100;
                total = total - 1;
                break;
              default:
                total = total + x;
            }
          }
        }"""
    )

    branch = unit_at_line(nesting, 4)
    assert branch.end_line == 13
    assert branch.context == "if (x > threshold)"
    assert branch.body_node_count == 29
    assert branch.body == dedent(
        """\
        {
          switch (x % 2) {
            case 0:
              total = total + 100;
              total = total - 1;
              break;
            default:
              total = total + x;
          }
        }"""
    )

    case = unit_at_line(nesting, 6)
    assert case.end_line == 9
    assert case.context == "case 0:"
    assert case.body_node_count == 13
    assert case.body == dedent(
        """\
        total = total + 100;
        total = total - 1;
        break;"""
    )


def test_splits_header_and_body_across_brace_and_wrap_styles():
    formatting = parse((FIXTURES / "Formatting.ts").read_bytes())

    product = unit_at_line(formatting, 1)
    assert product.end_line == 10
    assert product.context == dedent(
        """\
        function product(
          factors: number[],
          start: number,
        ): number"""
    )
    assert product.body == dedent(
        """\
        {
          let total = start;
          for (const f of factors) {
            total *= f;
          }
          return total;
        }"""
    )

    allman = unit_at_line(formatting, 12)
    assert allman.end_line == 20
    assert allman.context == "function allman(values: number[]): number"
    assert allman.body == dedent(
        """\
        {
          let sum = 0;
          for (const v of values)
          {
            sum += v;
          }
          return sum;
        }"""
    )

    allman_loop = unit_at_line(formatting, 15)
    assert allman_loop.end_line == 18
    assert allman_loop.context == "for (const v of values)"
    assert allman_loop.body == dedent(
        """\
        {
          sum += v;
        }"""
    )

    wrapped_loop = unit_at_line(formatting, 24)
    assert wrapped_loop.end_line == 30
    assert wrapped_loop.context == dedent(
        """\
        for (
          let i = 1;
          i <= count;
          i += 1
        )"""
    )
    assert wrapped_loop.body == dedent(
        """\
        {
          acc *= i;
        }"""
    )


def test_replaces_invalid_utf8_bytes_and_extracts_surrounding_function():
    units = parse(b'function greet(): string {\n    return "a\xffb";\n}\n')

    greet = unit_at_line(units, 1)
    assert greet.context == "function greet(): string"
    assert greet.body == dedent(
        """\
        {
            return "a�b";
        }"""
    )
