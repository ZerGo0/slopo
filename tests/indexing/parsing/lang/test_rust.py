from pathlib import Path
from textwrap import dedent

from slopo.indexing.parsing.lang.rust import parse

from .conftest import unit_at_line

FIXTURES = Path(__file__).parent / "fixtures" / "rust"


def test_strips_line_block_and_doc_comments_keeping_blank_lines():
    unit = parse((FIXTURES / "Comments.rs").read_bytes())[0]

    assert unit.start_line == 3
    assert unit.end_line == 9
    assert unit.context == "pub fn with_comments(a: i32, b: i32) -> i32"
    assert unit.body == dedent(
        """\
        {

            let sum = a + b;
            let url = "http://not-a-comment";
            let _ = url;
            sum
        }"""
    )


def test_body_node_count_across_body_shapes():
    body_sizes = parse((FIXTURES / "BodySizes.rs").read_bytes())

    empty = unit_at_line(body_sizes, 1)
    assert empty.body_node_count == 1

    block = unit_at_line(body_sizes, 3)
    assert block.body_node_count == 29


def test_extracts_function_together_with_its_nested_blocks():
    units = parse((FIXTURES / "Conditionals.rs").read_bytes())

    classify = unit_at_line(units, 6)
    assert classify.end_line == 20
    assert classify.kind == "function"
    assert classify.context == "pub fn classify(&self, score: i32) -> String"
    assert classify.body == dedent(
        """\
        {
            if score >= 90 {
                let bonus = self.curve / 2;
                return format!("A+{}", bonus);
            }

            if score >= 60 {
                String::from("pass")
            } else if score >= 40 {
                let note = score + self.curve;
                format!("borderline {}", note)
            } else {
                String::from("fail")
            }
        }"""
    )

    first_if = unit_at_line(units, 7)
    assert first_if.end_line == 10
    assert first_if.kind == "block"
    assert first_if.context == "if score >= 90"
    assert first_if.body == dedent(
        """\
        {
            let bonus = self.curve / 2;
            return format!("A+{}", bonus);
        }"""
    )


def test_extracts_free_function_method_and_trait_default_body():
    functions = parse((FIXTURES / "Functions.rs").read_bytes())

    assert len(functions) == 4

    describe = unit_at_line(functions, 4)
    assert describe.end_line == 7
    assert describe.context == "fn describe(&self) -> String"
    assert describe.body == dedent(
        """\
        {
            let area = self.area();
            format!("shape of {:.2}", area)
        }"""
    )

    area = unit_at_line(functions, 15)
    assert area.end_line == 17
    assert area.context == "fn area(&self) -> f64"
    assert area.body == dedent(
        """\
        {
            std::f64::consts::PI * self.radius * self.radius
        }"""
    )

    load_all = unit_at_line(functions, 20)
    assert load_all.end_line == 24
    assert load_all.context == "pub async fn load_all(ids: &[u32]) -> Vec<Data>"
    assert load_all.body == dedent(
        """\
        {
            let first = fetch(ids[0]).await;
            let rest = fetch_many(&ids[1..]).await;
            merge(first, rest)
        }"""
    )

    diagonal = unit_at_line(functions, 27)
    assert diagonal.end_line == 29
    assert diagonal.context == "pub fn diagonal(width: f64, height: f64) -> f64"
    assert diagonal.body == dedent(
        """\
        {
            (width * width + height * height).sqrt()
        }"""
    )


def test_extracts_local_function_and_closure_alongside_enclosing_function():
    nested_in_body = parse((FIXTURES / "NestedInBody.rs").read_bytes())

    assert len(nested_in_body) == 3

    outer = unit_at_line(nested_in_body, 1)
    assert outer.end_line == 7
    assert outer.context == "pub fn outer_function(values: &[i32]) -> i32"
    assert outer.body == dedent(
        """\
        {
            fn increment(n: i32) -> i32 {
                n + 1
            }

            values.iter().map(|v| increment(*v)).sum()
        }"""
    )

    increment = unit_at_line(nested_in_body, 2)
    assert increment.end_line == 4
    assert increment.context == "fn increment(n: i32) -> i32"
    assert increment.body == dedent(
        """\
        {
            n + 1
        }"""
    )

    closure = unit_at_line(nested_in_body, 6)
    assert closure.end_line == 6
    assert closure.context == "map |v|"
    assert closure.body == "increment(*v)"


def test_labels_closures_by_their_binding_or_the_call_they_are_passed_to():
    closures = parse((FIXTURES / "Closures.rs").read_bytes())

    assert len(closures) == 8

    doubler = unit_at_line(closures, 6)
    assert doubler.end_line == 6
    assert doubler.kind == "function"
    assert doubler.context == "let doubler = |x: i32|"
    assert doubler.body == "x * factor"

    record = unit_at_line(closures, 9)
    assert record.end_line == 12
    assert record.kind == "function"
    assert record.context == "let mut record = move |x: i32|"
    assert record.body == dedent(
        """\
        {
            seen += x;
            seen
        }"""
    )

    boxed = unit_at_line(closures, 15)
    assert boxed.end_line == 15
    assert boxed.kind == "function"
    assert boxed.context == "Box::new ||"
    assert boxed.body == "{}"

    assigned = unit_at_line(closures, 17)
    assert assigned.end_line == 19
    assert assigned.kind == "function"
    assert assigned.context == "worker.on_complete = ||"
    assert assigned.body == dedent(
        """\
        {
            println!("done");
        }"""
    )

    refresh = unit_at_line(closures, 21)
    assert refresh.end_line == 24
    assert refresh.kind == "function"
    assert refresh.context == "let refresh = async move"
    assert refresh.body == dedent(
        """\
        {
            let fresh = fetch(factor).await;
            cache(fresh);
        }"""
    )

    mapper = unit_at_line(closures, 29)
    assert mapper.end_line == 32
    assert mapper.kind == "function"
    assert mapper.context == "map |v|"
    assert mapper.body == dedent(
        """\
        {
            let scaled = doubler(*v);
            scaled + record(scaled)
        }"""
    )

    predicate = unit_at_line(closures, 33)
    assert predicate.end_line == 33
    assert predicate.kind == "function"
    assert predicate.context == "filter |v|"
    assert predicate.body == "*v > 0"


def test_extracts_conditional_blocks():
    units = parse((FIXTURES / "Conditionals.rs").read_bytes())

    assert len(units) == 8

    early_return = unit_at_line(units, 7)
    assert early_return.end_line == 10
    assert early_return.context == "if score >= 90"
    assert early_return.body == dedent(
        """\
        {
            let bonus = self.curve / 2;
            return format!("A+{}", bonus);
        }"""
    )

    pass_branch = unit_at_line(units, 12)
    assert pass_branch.end_line == 14
    assert pass_branch.context == "if score >= 60"
    assert pass_branch.body == dedent(
        """\
        {
            String::from("pass")
        }"""
    )

    else_if_branch = unit_at_line(units, 14)
    assert else_if_branch.end_line == 17
    assert else_if_branch.context == "if score >= 40"
    assert else_if_branch.body == dedent(
        """\
        {
            let note = score + self.curve;
            format!("borderline {}", note)
        }"""
    )

    else_branch = unit_at_line(units, 17)
    assert else_branch.end_line == 19
    assert else_branch.context == "else"
    assert else_branch.body == dedent(
        """\
        {
            String::from("fail")
        }"""
    )

    if_let_branch = unit_at_line(units, 23)
    assert if_let_branch.end_line == 26
    assert if_let_branch.context == "if let Some(value) = score"
    assert if_let_branch.body == dedent(
        """\
        {
            let curved = value + self.curve;
            curved.min(100)
        }"""
    )

    if_let_else = unit_at_line(units, 26)
    assert if_let_else.end_line == 28
    assert if_let_else.context == "else"
    assert if_let_else.body == dedent(
        """\
        {
            0
        }"""
    )


def test_extracts_loop_blocks():
    units = parse((FIXTURES / "Loops.rs").read_bytes())

    assert len(units) == 8

    for_block = unit_at_line(units, 4)
    assert for_block.end_line == 7
    assert for_block.context == "for row in rows"
    assert for_block.body == dedent(
        """\
        {
            let head = row[0];
            total += head * 2;
        }"""
    )

    while_block = unit_at_line(units, 9)
    assert while_block.end_line == 12
    assert while_block.context == "while total > limit"
    assert while_block.body == dedent(
        """\
        {
            total -= limit;
            total /= 2;
        }"""
    )

    while_let_block = unit_at_line(units, 15)
    assert while_let_block.end_line == 17
    assert while_let_block.context == "while let Some(top) = stack.pop()"
    assert while_let_block.body == dedent(
        """\
        {
            total += top;
        }"""
    )

    loop_block = unit_at_line(units, 19)
    assert loop_block.end_line == 24
    assert loop_block.context == "loop"
    assert loop_block.body == dedent(
        """\
        {
            total += 1;
            if total % 7 == 0 {
                break;
            }
        }"""
    )

    labelled_block = unit_at_line(units, 26)
    assert labelled_block.end_line == 32
    assert labelled_block.context == "'search: loop"
    assert labelled_block.body == dedent(
        """\
        {
            let next = total * 2;
            if next > limit {
                break 'search limit;
            }
            total = next;
        }"""
    )


def test_extracts_match_arm_blocks():
    units = parse((FIXTURES / "Match.rs").read_bytes())

    assert len(units) == 7

    braced_arm = unit_at_line(units, 10)
    assert braced_arm.end_line == 13
    assert braced_arm.kind == "block"
    assert braced_arm.context == "Event::Click { x, y } =>"
    assert braced_arm.body == dedent(
        """\
        {
            let distance = x * x + y * y;
            state + distance
        }"""
    )

    guarded_arm = unit_at_line(units, 14)
    assert guarded_arm.end_line == 14
    assert guarded_arm.kind == "block"
    assert guarded_arm.context == "Event::Key(c) if c.is_ascii_digit() =>"
    assert guarded_arm.body == "state + c as i32"

    inner_arm = unit_at_line(units, 16)
    assert inner_arm.end_line == 16
    assert inner_arm.kind == "block"
    assert inner_arm.context == "1 =>"
    assert inner_arm.body == "state + delta"

    second_inner_arm = unit_at_line(units, 17)
    assert second_inner_arm.end_line == 17
    assert second_inner_arm.kind == "block"
    assert second_inner_arm.context == "-1 =>"
    assert second_inner_arm.body == "state - delta"

    inner_default_arm = unit_at_line(units, 18)
    assert inner_default_arm.end_line == 18
    assert inner_default_arm.kind == "block"
    assert inner_default_arm.context == "_ =>"
    assert inner_default_arm.body == "state"

    last_arm = unit_at_line(units, 20)
    assert last_arm.end_line == 20
    assert last_arm.kind == "block"
    assert last_arm.context == "Event::Close =>"
    assert last_arm.body == "0"


def test_extracts_standalone_blocks():
    units = parse((FIXTURES / "StandaloneBlocks.rs").read_bytes())

    assert len(units) == 6

    bound_block = unit_at_line(units, 2)
    assert bound_block.end_line == 8
    assert bound_block.kind == "block"
    assert bound_block.context == "let gross ="
    assert bound_block.body == dedent(
        """\
        {
            let mut sum = 0;
            for row in rows {
                sum += row.amount;
            }
            sum
        }"""
    )

    unsafe_block = unit_at_line(units, 10)
    assert unsafe_block.end_line == 13
    assert unsafe_block.kind == "block"
    assert unsafe_block.context == "unsafe"
    assert unsafe_block.body == dedent(
        """\
        {
            let first = *raw;
            record(first);
        }"""
    )

    bail_out_block = unit_at_line(units, 15)
    assert bail_out_block.end_line == 19
    assert bail_out_block.kind == "block"
    assert bail_out_block.context == "let Some(rate) = lookup() else"
    assert bail_out_block.body == dedent(
        """\
        {
            let fallback = gross / 2;
            record(fallback as u8);
            return fallback;
        }"""
    )

    bare_block = unit_at_line(units, 21)
    assert bare_block.end_line == 24
    assert bare_block.kind == "block"
    assert bare_block.context is None
    assert bare_block.body == dedent(
        """\
        {
            let scaled = gross * rate;
            record(scaled as u8);
        }"""
    )


def test_extracts_each_nested_construct_with_only_its_own_body():
    units = parse((FIXTURES / "Nested.rs").read_bytes())

    outer_loop = unit_at_line(units, 3)
    assert outer_loop.end_line == 9
    assert outer_loop.body_node_count == 17
    assert outer_loop.context == "for row in rows"
    assert outer_loop.body == dedent(
        """\
        {
            for cell in row {
                if *cell > threshold {
                    hits += 1;
                }
            }
        }"""
    )

    inner_loop = unit_at_line(units, 4)
    assert inner_loop.end_line == 8
    assert inner_loop.body_node_count == 12
    assert inner_loop.context == "for cell in row"
    assert inner_loop.body == dedent(
        """\
        {
            if *cell > threshold {
                hits += 1;
            }
        }"""
    )

    condition = unit_at_line(units, 5)
    assert condition.end_line == 7
    assert condition.body_node_count == 5
    assert condition.context == "if *cell > threshold"
    assert condition.body == dedent(
        """\
        {
            hits += 1;
        }"""
    )


def test_splits_header_from_body_across_formatting_styles():
    units = parse((FIXTURES / "Formatting.rs").read_bytes())

    wrapped_signature = unit_at_line(units, 1)
    assert wrapped_signature.end_line == 18
    assert wrapped_signature.context == dedent(
        """\
        pub fn within<'a, T>(
            items: &'a [T],
            lower: &T,
            upper: &T,
        ) -> Vec<&'a T>
        where
            T: PartialOrd,"""
    )

    wrapped_condition = unit_at_line(units, 11)
    assert wrapped_condition.end_line == 15
    assert wrapped_condition.context == dedent(
        """\
        if item >= lower
        && item <= upper"""
    )
    assert wrapped_condition.body == dedent(
        """\
        {
            kept.push(item);
        }"""
    )

    describe = unit_at_line(units, 20)
    assert describe.end_line == 30
    assert describe.context == "pub fn describe(kind: &Kind) -> &'static str"

    wrapped_pattern_arm = unit_at_line(units, 22)
    assert wrapped_pattern_arm.end_line == 24
    assert wrapped_pattern_arm.context == dedent(
        """\
        Kind::Alpha
        | Kind::Beta
        | Kind::Gamma =>"""
    )
    assert wrapped_pattern_arm.body == '"early"'

    guarded_arm = unit_at_line(units, 25)
    assert guarded_arm.end_line == 27
    assert guarded_arm.context == "Kind::Delta if kind.is_late() =>"
    assert guarded_arm.body == dedent(
        """\
        {
            "late delta"
        }"""
    )


def test_replaces_invalid_utf8_bytes_and_extracts_surrounding_function():
    units = parse(b'fn greet() -> String {\n    return "a\xffb".to_string();\n}\n')

    greet = unit_at_line(units, 1)
    assert greet.context == "fn greet() -> String"
    assert greet.body == dedent(
        """\
        {
            return "a�b".to_string();
        }"""
    )
