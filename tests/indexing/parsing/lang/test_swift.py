from pathlib import Path
from textwrap import dedent

from slopo.indexing.parsing.lang.swift import parse

from .conftest import unit_at_line

FIXTURES = Path(__file__).parent / "fixtures" / "swift"


def test_strips_comments_and_preserves_blank_lines():
    unit = parse((FIXTURES / "Comments.swift").read_bytes())[0]

    assert unit.start_line == 6
    assert unit.end_line == 24
    assert unit.context == "func normalize(readings: [Int], offset: Int) -> Int"
    assert unit.body == dedent(
        """\
        var total = 0

        for value in readings {
            total += value - offset
        }





        if total < 0 {
            total = -total
        }

        let note = "sep // not a comment /* still text */"
        return total + note.count"""
    )


def test_counts_body_nodes_across_function_sizes():
    units = parse((FIXTURES / "BodySizes.swift").read_bytes())

    square = unit_at_line(units, 1)
    assert square.body_node_count == 5

    sum_values = unit_at_line(units, 5)
    assert sum_values.body_node_count == 17

    count_hits = unit_at_line(units, 13)
    assert count_hits.body_node_count == 27


def test_extracts_function_together_with_a_nested_conditional_block():
    units = parse((FIXTURES / "Conditionals.swift").read_bytes())

    classify = unit_at_line(units, 1)
    assert classify.end_line == 15
    assert classify.kind == "function"
    assert classify.context == "func classify(score: Int, bonus: Int) -> String"
    assert classify.body == dedent(
        """\
        if score >= 90 {
            let total = score + bonus
            return "top \\(total)"
        }

        if score >= 50 {
            return "pass"
        } else if score >= 30 {
            let gap = 50 - score
            return "near \\(gap)"
        } else {
            return "fail"
        }"""
    )

    top_branch = unit_at_line(units, 2)
    assert top_branch.end_line == 5
    assert top_branch.kind == "block"
    assert top_branch.context == "if score >= 90"
    assert top_branch.body == dedent(
        """\
        let total = score + bonus
        return "top \\(total)\""""
    )


def test_extracts_function_declaration_variants():
    units = parse((FIXTURES / "Functions.swift").read_bytes())

    distance = unit_at_line(units, 1)
    assert distance.end_line == 4
    assert distance.context == "func distance(x: Double, y: Double) -> Double"
    assert distance.body == dedent(
        """\
        let squared = x * x + y * y
        return squared.squareRoot()"""
    )

    load_all = unit_at_line(units, 6)
    assert load_all.end_line == 10
    assert load_all.context == "func loadAll(ids: [Int]) async throws -> [Int]"
    assert load_all.body == dedent(
        """\
        let head = try await fetch(ids[0])
        let rest = try await fetchMany(ids)
        return [head] + rest"""
    )

    init_start = unit_at_line(units, 15)
    assert init_start.end_line == 17
    assert init_start.context == "init(start: Int)"
    assert init_start.body == "value = start * 2"

    init_label = unit_at_line(units, 19)
    assert init_label.end_line == 24
    assert init_label.context == "init?(label: String)"
    assert init_label.body == dedent(
        """\
        guard let parsed = Int(label) else {
            return nil
        }
        value = parsed"""
    )

    deinitializer = unit_at_line(units, 26)
    assert deinitializer.end_line == 29
    assert deinitializer.context == "deinit"
    assert deinitializer.body == dedent(
        """\
        value = 0
        log(value)"""
    )

    zero = unit_at_line(units, 31)
    assert zero.end_line == 34
    assert zero.context == "static func zero() -> Counter"
    assert zero.body == dedent(
        """\
        let created = Counter(start: 0)
        return created"""
    )

    advance = unit_at_line(units, 36)
    assert advance.end_line == 39
    assert advance.context == "func advance(by step: Int) -> Int"
    assert advance.body == dedent(
        """\
        value += step
        return value"""
    )


def test_extracts_function_nested_in_another_function():
    units = parse((FIXTURES / "NestedFunctions.swift").read_bytes())

    outer = unit_at_line(units, 1)
    assert outer.end_line == 8
    assert outer.kind == "function"
    assert outer.context == "func outer(values: [Int]) -> Int"
    assert outer.body == dedent(
        """\
        func increment(n: Int) -> Int {
            let bumped = n + 1
            return bumped
        }

        return increment(n: values.count)"""
    )

    increment = unit_at_line(units, 2)
    assert increment.end_line == 5
    assert increment.kind == "function"
    assert increment.context == "func increment(n: Int) -> Int"
    assert increment.body == dedent(
        """\
        let bumped = n + 1
        return bumped"""
    )


def test_extracts_functions_declared_in_nested_types():
    units = parse((FIXTURES / "NestedTypes.swift").read_bytes())

    assert len(units) == 3

    inside = unit_at_line(units, 3)
    assert inside.end_line == 5
    assert inside.context == "func inside(a: Int) -> Int"
    assert inside.body == "return a + 1"

    norm = unit_at_line(units, 9)
    assert norm.end_line == 11
    assert norm.context == "func norm() -> Int"
    assert norm.body == "return 0"

    outer_method = unit_at_line(units, 14)
    assert outer_method.end_line == 16
    assert outer_method.context == "func outerMethod() -> Int"
    assert outer_method.body == "return 42"


def test_labels_closures_by_binding_or_enclosing_call():
    units = parse((FIXTURES / "Closures.swift").read_bytes())

    assert len(units) == 6

    mapped = unit_at_line(units, 2)
    assert mapped.end_line == 5
    assert mapped.kind == "function"
    assert mapped.context == "map { value in"
    assert mapped.body == dedent(
        """\
        let boosted = value * factor
        return boosted + 1"""
    )

    filtered = unit_at_line(units, 7)
    assert filtered.end_line == 7
    assert filtered.kind == "function"
    assert filtered.context == "filter {"
    assert filtered.body == "$0 > 0"

    combine = unit_at_line(units, 9)
    assert combine.end_line == 12
    assert combine.kind == "function"
    assert combine.context == "let combine: (Int, Int) -> Int = { left, right in"
    assert combine.body == dedent(
        """\
        let merged = left + right
        return merged * 2"""
    )

    applied = unit_at_line(units, 14)
    assert applied.end_line == 17
    assert applied.kind == "function"
    assert applied.context == "apply { item in"
    assert applied.body == dedent(
        """\
        let shifted = item - factor
        return shifted"""
    )

    reduced = unit_at_line(units, 19)
    assert reduced.end_line == 21
    assert reduced.kind == "function"
    assert reduced.context == "applied.reduce(0) { acc, item in"
    assert reduced.body == "return combine(acc, item)"


def test_extracts_property_and_subscript_accessors():
    units = parse((FIXTURES / "Accessors.swift").read_bytes())

    assert len(units) == 7

    scaled_get = unit_at_line(units, 6)
    assert scaled_get.end_line == 9
    assert scaled_get.context == "get"
    assert scaled_get.body == dedent(
        """\
        let base = stored * multiplier
        return base + 1"""
    )

    scaled_set = unit_at_line(units, 10)
    assert scaled_set.end_line == 12
    assert scaled_set.context == "set"
    assert scaled_set.body == "stored = newValue / multiplier"

    summary = unit_at_line(units, 15)
    assert summary.end_line == 18
    assert summary.context == "var summary: Int"
    assert summary.body == dedent(
        """\
        let doubled = stored * 2
        return doubled + multiplier"""
    )

    will_set = unit_at_line(units, 21)
    assert will_set.end_line == 23
    assert will_set.context == "willSet"
    assert will_set.body == "log(newValue - tracked)"

    did_set = unit_at_line(units, 24)
    assert did_set.end_line == 26
    assert did_set.context == "didSet"
    assert did_set.body == "log(tracked - oldValue)"

    subscript_get = unit_at_line(units, 30)
    assert subscript_get.end_line == 33
    assert subscript_get.context == "get"
    assert subscript_get.body == dedent(
        """\
        let shifted = index + stored
        return shifted * multiplier"""
    )

    subscript_set = unit_at_line(units, 34)
    assert subscript_set.end_line == 36
    assert subscript_set.context == "set"
    assert subscript_set.body == "stored = newValue - index"


def test_ignores_protocol_requirements_and_empty_bodies():
    units = parse((FIXTURES / "NotExtracted.swift").read_bytes())

    assert len(units) == 1

    anchor = unit_at_line(units, 11)
    assert anchor.end_line == 17
    assert anchor.context == "func anchor(values: [Int]) -> Int"


def test_extracts_conditional_and_guard_blocks():
    units = parse((FIXTURES / "Conditionals.swift").read_bytes())

    assert len(units) == 11

    if_branch = unit_at_line(units, 2)
    assert if_branch.end_line == 5
    assert if_branch.context == "if score >= 90"
    assert if_branch.body == dedent(
        """\
        let total = score + bonus
        return "top \\(total)\""""
    )

    pass_branch = unit_at_line(units, 7)
    assert pass_branch.end_line == 9
    assert pass_branch.context == "if score >= 50"
    assert pass_branch.body == 'return "pass"'

    else_if_branch = unit_at_line(units, 9)
    assert else_if_branch.end_line == 12
    assert else_if_branch.context == "if score >= 30"
    assert else_if_branch.body == dedent(
        """\
        let gap = 50 - score
        return "near \\(gap)\""""
    )

    else_branch = unit_at_line(units, 12)
    assert else_branch.end_line == 14
    assert else_branch.context == "else"
    assert else_branch.body == 'return "fail"'

    guard_branch = unit_at_line(units, 18)
    assert guard_branch.end_line == 21
    assert guard_branch.context == "guard let head = values.first else"
    assert guard_branch.body == dedent(
        """\
        let fallback = values.count
        return -fallback"""
    )

    positive_branch = unit_at_line(units, 23)
    assert positive_branch.end_line == 25
    assert positive_branch.context == "if head > 0"
    assert positive_branch.body == "return head"

    if_let_branch = unit_at_line(units, 30)
    assert if_let_branch.end_line == 33
    assert if_let_branch.context == "if let value = value"
    assert if_let_branch.body == dedent(
        """\
        let doubled = value * 2
        return "some \\(doubled)\""""
    )

    none_branch = unit_at_line(units, 33)
    assert none_branch.end_line == 35
    assert none_branch.context == "else"
    assert none_branch.body == 'return "none"'


def test_extracts_loop_blocks():
    units = parse((FIXTURES / "Loops.swift").read_bytes())

    assert len(units) == 7

    for_block = unit_at_line(units, 4)
    assert for_block.end_line == 7
    assert for_block.context == "for row in rows"
    assert for_block.body == dedent(
        """\
        let head = row[0]
        total += head * 2"""
    )

    while_block = unit_at_line(units, 9)
    assert while_block.end_line == 12
    assert while_block.context == "while total > limit"
    assert while_block.body == dedent(
        """\
        total -= limit
        total /= 2"""
    )

    repeat_block = unit_at_line(units, 15)
    assert repeat_block.end_line == 18
    assert repeat_block.context == "repeat"
    assert repeat_block.body == dedent(
        """\
        countdown -= 1
        total += countdown"""
    )

    while_let_block = unit_at_line(units, 27)
    assert while_let_block.end_line == 29
    assert while_let_block.context == "while let top = stack.popLast()"
    assert while_let_block.body == "total += top"

    for_where_block = unit_at_line(units, 31)
    assert for_where_block.end_line == 33
    assert for_where_block.context == "for value in values where value > 0"
    assert for_where_block.body == "total += value"


def test_extracts_switch_case_blocks():
    units = parse((FIXTURES / "Switch.swift").read_bytes())

    assert len(units) == 8

    single = unit_at_line(units, 3)
    assert single.end_line == 4
    assert single.context == "case 0:"
    assert single.body == 'return "zero"'

    multi_pattern = unit_at_line(units, 5)
    assert multi_pattern.end_line == 7
    assert multi_pattern.context == "case 1, 2, 3:"
    assert multi_pattern.body == dedent(
        """\
        let doubled = code * 2
        return "small \\(doubled)\""""
    )

    guarded = unit_at_line(units, 8)
    assert guarded.end_line == 9
    assert guarded.context == "case let n where n < 0:"
    assert guarded.body == 'return "negative \\(n)"'

    default_case = unit_at_line(units, 10)
    assert default_case.end_line == 12
    assert default_case.context == "default:"
    assert default_case.body == dedent(
        """\
        let capped = min(code, 100)
        return "big \\(capped)\""""
    )

    associated = unit_at_line(units, 18)
    assert associated.end_line == 20
    assert associated.context == "case .tap(let x, let y):"
    assert associated.body == dedent(
        """\
        let sum = x + y
        return sum"""
    )

    bare_case = unit_at_line(units, 21)
    assert bare_case.end_line == 22
    assert bare_case.context == "case .scroll:"
    assert bare_case.body == "return -1"


def test_extracts_do_catch_blocks():
    units = parse((FIXTURES / "DoCatch.swift").read_bytes())

    assert len(units) == 6

    do_block = unit_at_line(units, 4)
    assert do_block.end_line == 7
    assert do_block.context == "do"
    assert do_block.body == dedent(
        """\
        let parsed = try parse(inputs)
        total += parsed"""
    )

    typed_catch = unit_at_line(units, 7)
    assert typed_catch.end_line == 9
    assert typed_catch.context == "catch let error as FormatError"
    assert typed_catch.body == "total = error.code"

    bound_catch = unit_at_line(units, 9)
    assert bound_catch.end_line == 12
    assert bound_catch.context == "catch let error"
    assert bound_catch.body == dedent(
        """\
        log(error)
        total = -1"""
    )

    second_do = unit_at_line(units, 14)
    assert second_do.end_line == 16
    assert second_do.context == "do"
    assert second_do.body == "total += try compute(total)"

    bare_catch = unit_at_line(units, 16)
    assert bare_catch.end_line == 18
    assert bare_catch.context == "catch"
    assert bare_catch.body == "total = 0"


def test_counts_nodes_at_each_level_of_nested_constructs():
    units = parse((FIXTURES / "NestedBlocks.swift").read_bytes())

    scan = unit_at_line(units, 1)
    assert scan.end_line == 16
    assert scan.body_node_count == 50
    assert scan.context == "func scan(rows: [[Int]], limit: Int) -> Int"
    assert scan.body == dedent(
        """\
        var hits = 0
        for row in rows {
            if row.count > limit {
                for cell in row {
                    switch cell.signum() {
                    case 1:
                        hits += cell
                    default:
                        hits -= 1
                    }
                }
            }
        }
        return hits"""
    )

    for_rows = unit_at_line(units, 3)
    assert for_rows.end_line == 14
    assert for_rows.body_node_count == 38
    assert for_rows.context == "for row in rows"
    assert for_rows.body == dedent(
        """\
        if row.count > limit {
            for cell in row {
                switch cell.signum() {
                case 1:
                    hits += cell
                default:
                    hits -= 1
                }
            }
        }"""
    )

    if_block = unit_at_line(units, 4)
    assert if_block.end_line == 13
    assert if_block.body_node_count == 30
    assert if_block.context == "if row.count > limit"
    assert if_block.body == dedent(
        """\
        for cell in row {
            switch cell.signum() {
            case 1:
                hits += cell
            default:
                hits -= 1
            }
        }"""
    )

    for_cells = unit_at_line(units, 5)
    assert for_cells.end_line == 12
    assert for_cells.body_node_count == 25
    assert for_cells.context == "for cell in row"
    assert for_cells.body == dedent(
        """\
        switch cell.signum() {
        case 1:
            hits += cell
        default:
            hits -= 1
        }"""
    )

    case_one = unit_at_line(units, 7)
    assert case_one.end_line == 8
    assert case_one.body_node_count == 5
    assert case_one.context == "case 1:"
    assert case_one.body == "hits += cell"


def test_splits_header_from_body_across_formatting_styles():
    units = parse((FIXTURES / "Formatting.swift").read_bytes())

    within = unit_at_line(units, 1)
    assert within.end_line == 14
    assert within.context == dedent(
        """\
        func within(
            values: [Int],
            lower: Int,
            upper: Int
        ) -> [Int]"""
    )
    assert within.body == dedent(
        """\
        var kept: [Int] = []
        for value in values {
            if value >= lower
                && value <= upper {
                kept.append(value)
            }
        }
        return kept"""
    )

    wrapped_condition = unit_at_line(units, 8)
    assert wrapped_condition.end_line == 11
    assert wrapped_condition.context == dedent(
        """\
        if value >= lower
        && value <= upper"""
    )
    assert wrapped_condition.body == "kept.append(value)"

    wrapped_case = unit_at_line(units, 18)
    assert wrapped_case.end_line == 22
    assert wrapped_case.context == dedent(
        """\
        case 1,
        2,
        3:"""
    )
    assert wrapped_case.body == dedent(
        """\
        let mapped = code * 10
        return "low \\(mapped)\""""
    )


def test_replaces_invalid_utf8_bytes_and_extracts_surrounding_function():
    units = parse(b'func greet() -> String {\n    return "a\xffb"\n}\n')

    greet = unit_at_line(units, 1)
    assert greet.context == "func greet() -> String"
    assert greet.body == 'return "a�b"'
