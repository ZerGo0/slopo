from pathlib import Path
from textwrap import dedent

from slopo.indexing.parsing.lang.ruby import parse

from .conftest import unit_at_line

FIXTURES = Path(__file__).parent / "fixtures" / "ruby"


def test_strips_line_and_block_comments_keeping_blank_lines():
    unit = parse((FIXTURES / "Comments.rb").read_bytes())[0]

    assert unit.start_line == 4
    assert unit.end_line == 16
    assert unit.context == "def summary(amount, rate, count)"
    assert unit.body_node_count == 21
    assert unit.body == dedent(
        """\
        scaled = amount * rate






        subtotal = (scaled * count).round

        "batch ##{count}: #{subtotal}\""""
    )


def test_body_node_count_across_body_shapes():
    body_sizes = parse((FIXTURES / "BodySizes.rb").read_bytes())

    endless = unit_at_line(body_sizes, 4)
    assert endless.body_node_count == 3

    multiline = unit_at_line(body_sizes, 6)
    assert multiline.body_node_count == 22

    large = unit_at_line(body_sizes, 12)
    assert large.body_node_count == 69


def test_extracts_blocks_with_enclosing_function():
    units = parse((FIXTURES / "Conditionals.rb").read_bytes())

    tier = unit_at_line(units, 2)
    assert tier.end_line == 16
    assert tier.kind == "function"
    assert tier.context == "def tier(score, streak)"
    assert tier.body == dedent(
        """\
        bonus = streak * 2
        if score + bonus >= 90
          grade = "gold"
          reward = score + bonus - 90
          [grade, reward]
        elsif score >= 50
          grade = "silver"
          [grade, streak]
        else
          grade = "bronze"
          penalty = 50 - score
          [grade, penalty]
        end"""
    )

    if_branch = unit_at_line(units, 4)
    assert if_branch.end_line == 7
    assert if_branch.kind == "block"
    assert if_branch.context == "if score + bonus >= 90"
    assert if_branch.body == dedent(
        """\
        grade = "gold"
        reward = score + bonus - 90
        [grade, reward]"""
    )


def test_extracts_methods_singleton_and_endless():
    functions = parse((FIXTURES / "Functions.rb").read_bytes())

    deposit = unit_at_line(functions, 2)
    assert deposit.end_line == 8
    assert deposit.context == "def deposit(balance, amount, fee_rate)"
    assert deposit.body == dedent(
        """\
        fee = amount * fee_rate
        credited = amount - fee
        updated = balance + credited
        growth = updated - balance
        [updated, credited, growth]"""
    )

    opening = unit_at_line(functions, 10)
    assert opening.end_line == 15
    assert opening.context == "def self.opening(owner, seed, tier)"
    assert opening.body == dedent(
        """\
        prefix = owner.upcase
        handle = "#{prefix}##{tier}"
        starting = seed * 100 + tier
        "#{handle}:#{starting}\""""
    )

    fee = unit_at_line(functions, 17)
    assert fee.end_line == 17
    assert fee.context == "def fee(balance) ="
    assert fee.body == "balance * 0.02"

    statement = unit_at_line(functions, 19)
    assert statement.end_line == 27
    assert statement.context == "def statement(owner, entries)"
    assert statement.body == dedent(
        """\
        header = "#{owner.capitalize} (#{entries.length})"
        total = entries.sum
        average = total / entries.length
        high = entries.max
        low = entries.min
        spread = high - low
        "#{header} total #{total} avg #{average} spread #{spread}\""""
    )


def test_extracts_closures_alongside_enclosing_method():
    closures = parse((FIXTURES / "Closures.rb").read_bytes())

    assert len(closures) == 7

    run = unit_at_line(closures, 7)
    assert run.end_line == 28
    assert run.kind == "function"

    macro = unit_at_line(closures, 2)
    assert macro.end_line == 5
    assert macro.kind == "function"
    assert macro.context == "define_method(:scale) do |value, factor|"
    assert macro.body == dedent(
        """\
        scaled = value * factor
        scaled.round"""
    )

    lambda_ = unit_at_line(closures, 8)
    assert lambda_.end_line == 8
    assert lambda_.kind == "function"
    assert lambda_.context == "shift = ->(n) {"
    assert lambda_.body == "n + offset"

    each_block = unit_at_line(closures, 10)
    assert each_block.end_line == 13
    assert each_block.kind == "function"
    assert each_block.context == "numbers.each do |n|"
    assert each_block.body == dedent(
        """\
        base = shift.call(n)
        totals << base * base"""
    )

    map_block = unit_at_line(closures, 14)
    assert map_block.end_line == 17
    assert map_block.kind == "function"
    assert map_block.context == "numbers.map do |n|"
    assert map_block.body == dedent(
        """\
        squared = n * n
        squared + offset"""
    )

    bound_lambda = unit_at_line(closures, 18)
    assert bound_lambda.end_line == 21
    assert bound_lambda.kind == "function"
    assert bound_lambda.context == "positive = lambda { |x|"
    assert bound_lambda.body == dedent(
        """\
        shifted = x.abs
        shifted + offset"""
    )

    proc_block = unit_at_line(closures, 22)
    assert proc_block.end_line == 26
    assert proc_block.kind == "function"
    assert proc_block.context == "pack = Proc.new { |a, b|"
    assert proc_block.body == dedent(
        """\
        total = a + b
        gap = a - b
        { sum: total, diff: gap }"""
    )


def test_extracts_methods_from_module_and_nested_class():
    nested = parse((FIXTURES / "Nested.rb").read_bytes())

    assert len(nested) == 2

    rate = unit_at_line(nested, 2)
    assert rate.end_line == 5
    assert rate.context == "def self.rate(tier)"
    assert rate.body == dedent(
        """\
        base = tier * 5
        base + 1"""
    )

    total = unit_at_line(nested, 8)
    assert total.end_line == 11
    assert total.context == "def total(subtotal, tax)"
    assert total.body == dedent(
        """\
        taxed = subtotal * tax
        subtotal + taxed"""
    )


def test_extracts_conditional_branches_and_guards():
    conditionals = parse((FIXTURES / "Conditionals.rb").read_bytes())

    assert len(conditionals) == 10

    if_branch = unit_at_line(conditionals, 4)
    assert if_branch.end_line == 7
    assert if_branch.context == "if score + bonus >= 90"
    assert if_branch.body == dedent(
        """\
        grade = "gold"
        reward = score + bonus - 90
        [grade, reward]"""
    )

    elsif_branch = unit_at_line(conditionals, 8)
    assert elsif_branch.end_line == 10
    assert elsif_branch.context == "elsif score >= 50"
    assert elsif_branch.body == dedent(
        """\
        grade = "silver"
        [grade, streak]"""
    )

    else_branch = unit_at_line(conditionals, 11)
    assert else_branch.end_line == 14
    assert else_branch.context == "else"
    assert else_branch.body == dedent(
        """\
        grade = "bronze"
        penalty = 50 - score
        [grade, penalty]"""
    )

    if_guard = unit_at_line(conditionals, 19)
    assert if_guard.end_line == 19
    assert if_guard.context == "if value < floor"
    assert if_guard.body == "value = floor"

    unless_guard = unit_at_line(conditionals, 20)
    assert unless_guard.end_line == 20
    assert unless_guard.context == "unless value <= ceil"
    assert unless_guard.body == "value = ceil"

    then_branch = unit_at_line(conditionals, 26)
    assert then_branch.end_line == 28
    assert then_branch.context == "if flag then"
    assert then_branch.body == dedent(
        """\
        label = "on"
        "#{label}:#{count}\""""
    )

    describe_else = unit_at_line(conditionals, 29)
    assert describe_else.end_line == 30
    assert describe_else.context == "else"
    assert describe_else.body == '"off:#{count * 0}"'


def test_extracts_loop_bodies_and_modifiers():
    loops = parse((FIXTURES / "Loops.rb").read_bytes())

    assert len(loops) == 10

    while_loop = unit_at_line(loops, 5)
    assert while_loop.end_line == 7
    assert while_loop.kind == "block"
    assert while_loop.context == "while n > 0"
    assert while_loop.body == dedent(
        """\
        log << n * n
        n -= 1"""
    )

    until_loop = unit_at_line(loops, 14)
    assert until_loop.end_line == 15
    assert until_loop.kind == "block"
    assert until_loop.context == "until value >= limit"
    assert until_loop.body == "value = value * 2 + 1"

    for_loop = unit_at_line(loops, 22)
    assert for_loop.end_line == 24
    assert for_loop.kind == "block"
    assert for_loop.context == "for row in rows"
    assert for_loop.body == dedent(
        """\
        code = row * 10
        seen << code + 1"""
    )

    while_modifier = unit_at_line(loops, 31)
    assert while_modifier.end_line == 31
    assert while_modifier.kind == "block"
    assert while_modifier.context == "while stack.any?"
    assert while_modifier.body == "total += stack.pop"

    until_modifier = unit_at_line(loops, 36)
    assert until_modifier.end_line == 36
    assert until_modifier.kind == "block"
    assert until_modifier.context == "until buffer.length == size"
    assert until_modifier.body == "buffer << buffer.length"


def test_extracts_case_when_and_case_in_arms():
    cases = parse((FIXTURES / "Case.rb").read_bytes())

    assert len(cases) == 7

    create_arm = unit_at_line(cases, 5)
    assert create_arm.end_line == 8
    assert create_arm.kind == "block"
    assert create_arm.context == "when :create"
    assert create_arm.body == dedent(
        """\
        base = weight * 10
        bonus = base + 5
        [base, bonus]"""
    )

    multi_arm = unit_at_line(cases, 9)
    assert multi_arm.end_line == 11
    assert multi_arm.kind == "block"
    assert multi_arm.context == "when :update, :patch"
    assert multi_arm.body == dedent(
        """\
        adjusted = weight - 1
        [adjusted, adjusted * 2]"""
    )

    else_arm = unit_at_line(cases, 12)
    assert else_arm.end_line == 13
    assert else_arm.kind == "block"
    assert else_arm.context == "else"
    assert else_arm.body == "[0, weight]"

    array_pattern = unit_at_line(cases, 20)
    assert array_pattern.end_line == 23
    assert array_pattern.kind == "block"
    assert array_pattern.context == "in [x, y]"
    assert array_pattern.body == dedent(
        """\
        dx = x * x
        dy = y * y
        (dx + dy) * scale"""
    )

    hash_pattern = unit_at_line(cases, 24)
    assert hash_pattern.end_line == 25
    assert hash_pattern.kind == "block"
    assert hash_pattern.context == "in {radius:}"
    assert hash_pattern.body == "radius * radius * scale"


def test_extracts_exception_handling_blocks():
    exceptions = parse((FIXTURES / "Exceptions.rb").read_bytes())

    assert len(exceptions) == 8

    begin_body = unit_at_line(exceptions, 4)
    assert begin_body.end_line == 6
    assert begin_body.context == "begin"
    assert begin_body.body == dedent(
        """\
        picked = values.fetch(index)
        result = 100 / picked"""
    )

    bare_rescue = unit_at_line(exceptions, 7)
    assert bare_rescue.end_line == 8
    assert bare_rescue.context == "rescue IndexError"
    assert bare_rescue.body == "result = -1"

    typed_rescue = unit_at_line(exceptions, 9)
    assert typed_rescue.end_line == 11
    assert typed_rescue.context == "rescue ZeroDivisionError => e"
    assert typed_rescue.body == dedent(
        """\
        offset = e.message.length
        result = offset - offset"""
    )

    else_body = unit_at_line(exceptions, 12)
    assert else_body.end_line == 13
    assert else_body.context == "else"
    assert else_body.body == "result += 1"

    ensure_body = unit_at_line(exceptions, 14)
    assert ensure_body.end_line == 15
    assert ensure_body.context == "ensure"
    assert ensure_body.body == "result = result.abs"

    rescue_modifier = unit_at_line(exceptions, 21)
    assert rescue_modifier.end_line == 21
    assert rescue_modifier.context == "rescue text.length"
    assert rescue_modifier.body == "Integer(text)"


def test_extracts_nested_blocks():
    nesting = parse((FIXTURES / "NestedBlocks.rb").read_bytes())

    each_block = unit_at_line(nesting, 4)
    assert each_block.end_line == 13
    assert each_block.kind == "function"
    assert each_block.context == "rows.each do |row|"
    assert each_block.body_node_count == 24
    assert each_block.body == dedent(
        """\
        if row > 0
          begin
            scaled = row * 100
            sums << scaled / divisor
          rescue ZeroDivisionError
            sums << row
          end
        end"""
    )

    if_block = unit_at_line(nesting, 5)
    assert if_block.end_line == 11
    assert if_block.context == "if row > 0"
    assert if_block.body_node_count == 18
    assert if_block.body == dedent(
        """\
        begin
          scaled = row * 100
          sums << scaled / divisor
        rescue ZeroDivisionError
          sums << row
        end"""
    )

    begin_block = unit_at_line(nesting, 6)
    assert begin_block.end_line == 8
    assert begin_block.context == "begin"
    assert begin_block.body_node_count == 10
    assert begin_block.body == dedent(
        """\
        scaled = row * 100
        sums << scaled / divisor"""
    )


def test_extracts_function_with_multiline_signature():
    formatting = parse((FIXTURES / "Formatting.rb").read_bytes())

    combine = unit_at_line(formatting, 2)
    assert combine.end_line == 7
    assert combine.context == dedent(
        """\
        def combine(
          first,
          second
        )"""
    )
    assert combine.body == "first * second + first"


def test_extracts_inline_when_arms_with_then():
    formatting = parse((FIXTURES / "Formatting.rb").read_bytes())

    first_arm = unit_at_line(formatting, 11)
    assert first_arm.end_line == 11
    assert first_arm.context == "when 1 then"
    assert first_arm.body == '"one:#{count}"'

    default_arm = unit_at_line(formatting, 13)
    assert default_arm.end_line == 13
    assert default_arm.context == "else"
    assert default_arm.body == '"many:#{count}"'


def test_replaces_invalid_utf8_bytes_and_extracts_surrounding_method():
    units = parse(b'class C\n  def greet\n    "a\xffb"\n  end\nend\n')

    greet = unit_at_line(units, 2)
    assert greet.context == "def greet"
    assert greet.body == '"a�b"'
