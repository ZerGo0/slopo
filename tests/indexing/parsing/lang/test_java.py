from pathlib import Path
from textwrap import dedent

from slopo.indexing.parsing.lang.java import parse

from .conftest import unit_at_line

FIXTURES = Path(__file__).parent / "fixtures" / "java"


def test_strip_comments_preserving_blank_lines():
    unit = parse((FIXTURES / "Comments.java").read_bytes())[0]

    assert unit.start_line == 6
    assert unit.end_line == 21
    assert unit.context == "public int withComments(int a, int b)"
    assert unit.body_node_count == 31  # 35 with comments
    assert unit.body == dedent(
        """\
        {

            int sum = a + b;


            String url = "http://not-a-comment";

            switch (code) {
                case 1:
                    prepare();

                    dispatch();
            }

            return sum;
        }"""
    )


def test_body_node_count_across_body_shapes():
    body_sizes = parse((FIXTURES / "BodySizes.java").read_bytes())

    empty = unit_at_line(body_sizes, 5)
    assert empty.body_node_count == 1

    annotated = unit_at_line(body_sizes, 7)
    assert annotated.body_node_count == 36


def test_extracts_blocks_with_enclosing_function():
    functions = parse((FIXTURES / "Functions.java").read_bytes())

    normalize = unit_at_line(functions, 11)
    assert normalize.end_line == 21
    assert normalize.kind == "function"
    assert normalize.context == "public static double[] normalize(double[] values)"
    assert normalize.body == dedent(
        """\
        {
            double sum = 0;
            for (double v : values) {
                sum += v;
            }
            double[] result = new double[values.length];
            for (int i = 0; i < values.length; i++) {
                result[i] = values[i] / sum;
            }
            return result;
        }"""
    )

    first_loop = unit_at_line(functions, 13)
    assert first_loop.end_line == 15
    assert first_loop.kind == "block"
    assert first_loop.context == "for (double v : values)"
    assert first_loop.body == dedent(
        """\
        {
            sum += v;
        }"""
    )

    second_loop = unit_at_line(functions, 17)
    assert second_loop.end_line == 19
    assert second_loop.kind == "block"
    assert second_loop.context == "for (int i = 0; i < values.length; i++)"
    assert second_loop.body == dedent(
        """\
        {
            result[i] = values[i] / sum;
        }"""
    )


def test_extracts_each_function_with_full_body():
    functions = parse((FIXTURES / "Functions.java").read_bytes())

    add = unit_at_line(functions, 3)
    assert add.end_line == 5
    assert add.context == "public static int add(int a, int b)"
    assert add.body == dedent(
        """\
        {
            return a + b;
        }"""
    )

    greet = unit_at_line(functions, 7)
    assert greet.end_line == 9
    assert greet.context == "private String greet(String name)"
    assert greet.body == dedent(
        """\
        {
            return "Hello, " + name + "!";
        }"""
    )

    normalize = unit_at_line(functions, 11)
    assert normalize.end_line == 21

    repeat = unit_at_line(functions, 23)
    assert repeat.end_line == 30
    assert repeat.context == dedent(
        """\
        @Deprecated
        public <T> List<T> repeat(T item, int times)"""
    )
    assert repeat.body == dedent(
        """\
        {
            List<T> list = new ArrayList<>();
            for (int i = 0; i < times; i++) {
                list.add(item);
            }
            return list;
        }"""
    )


def test_extracts_nested_class_methods_with_full_body():
    nested = parse((FIXTURES / "Nested.java").read_bytes())

    assert len(nested) == 2

    outer = unit_at_line(nested, 3)
    assert outer.end_line == 5
    assert outer.context == "public void outerMethod()"
    assert outer.body == dedent(
        """\
        {
            System.out.println("outer");
        }"""
    )

    inner = unit_at_line(nested, 8)
    assert inner.end_line == 10
    assert inner.context == "public void innerMethod()"
    assert inner.body == dedent(
        """\
        {
            System.out.println("inner");
        }"""
    )


def test_extracts_anonymous_class_method_alongside_enclosing_method():
    nested_in_body = parse((FIXTURES / "NestedInBody.java").read_bytes())

    assert len(nested_in_body) == 2

    make_task = unit_at_line(nested_in_body, 3)
    assert make_task.end_line == 9
    assert make_task.context == "public Runnable makeTask(String label)"
    assert make_task.body == dedent(
        """\
        {
            return new Runnable() {
                public void run() {
                    System.out.println(label);
                }
            };
        }"""
    )

    run = unit_at_line(nested_in_body, 5)
    assert run.end_line == 7
    assert run.context == "public void run()"
    assert run.body == dedent(
        """\
        {
            System.out.println(label);
        }"""
    )


def test_extracts_lambdas_with_full_body_and_context():
    lambdas = parse((FIXTURES / "Lambdas.java").read_bytes())

    assert len(lambdas) == 8

    doubler = unit_at_line(lambdas, 11)
    assert doubler.end_line == 11
    assert doubler.context == "Function<Integer, Integer> doubler = x ->"
    assert doubler.body == "x * 2"

    expression = unit_at_line(lambdas, 13)
    assert expression.end_line == 13
    assert expression.context == "filter v ->"
    assert expression.body == "v > 0"

    on_complete = unit_at_line(lambdas, 22)
    assert on_complete.end_line == 24
    assert on_complete.context == "this.onComplete = () ->"
    assert on_complete.body == dedent(
        """\
        {
            System.out.println("done");
        }"""
    )

    returned = unit_at_line(lambdas, 28)
    assert returned.end_line == 28
    assert returned.context == "text ->"
    assert returned.body == "text.trim()"


def test_nested_lambda_extracted_alongside_enclosing_method():
    lambdas = parse((FIXTURES / "Lambdas.java").read_bytes())

    transform = unit_at_line(lambdas, 10)
    assert transform.end_line == 19
    assert transform.context == "public List<Integer> transform(List<Integer> values)"
    assert transform.body == dedent(
        """\
        {
            Function<Integer, Integer> doubler = x -> x * 2;
            return values.stream()
                    .filter(v -> v > 0)
                    .map(v -> {
                        int scaled = doubler.apply(v);
                        return scaled + 1;
                    })
                    .collect(Collectors.toList());
        }"""
    )

    nested = unit_at_line(lambdas, 14)
    assert nested.end_line == 17
    assert nested.context == "map v ->"
    assert nested.body == dedent(
        """\
        {
            int scaled = doubler.apply(v);
            return scaled + 1;
        }"""
    )


def test_extracts_conditional_branches_with_full_body_and_context():
    conditionals = parse((FIXTURES / "Conditionals.java").read_bytes())

    assert len(conditionals) == 7

    if_branch = unit_at_line(conditionals, 5)
    assert if_branch.end_line == 8
    assert if_branch.context == "if (score >= 90)"
    assert if_branch.body == dedent(
        """\
        {
            tier = "gold";
            score = score - 90;
        }"""
    )

    else_if_branch = unit_at_line(conditionals, 8)
    assert else_if_branch.end_line == 10
    assert else_if_branch.context == "if (score >= 50)"
    assert else_if_branch.body == dedent(
        """\
        {
            tier = "silver";
        }"""
    )

    else_branch = unit_at_line(conditionals, 10)
    assert else_branch.end_line == 13
    assert else_branch.context == "else"
    assert else_branch.body == dedent(
        """\
        {
            tier = "bronze";
            score = 0;
        }"""
    )

    below_min = unit_at_line(conditionals, 19)
    assert below_min.end_line == 22
    assert below_min.context == "if (value < min)"
    assert below_min.body == dedent(
        """\
        {
            int deficit = min - value;
            adjusted = min + deficit / 2;
        }"""
    )

    above_max = unit_at_line(conditionals, 23)
    assert above_max.end_line == 26
    assert above_max.context == "if (value > max)"
    assert above_max.body == dedent(
        """\
        {
            adjusted = max;
            return adjusted - 1;
        }"""
    )


def test_extracts_loop_bodies_with_full_body_and_context():
    loops = parse((FIXTURES / "Loops.java").read_bytes())

    assert len(loops) == 8

    index_for = unit_at_line(loops, 5)
    assert index_for.end_line == 8
    assert index_for.context == "for (int i = 0; i < parts.length; i++)"
    assert index_for.body == dedent(
        """\
        {
            out.append(parts[i]);
            out.append(",");
        }"""
    )

    enhanced_for = unit_at_line(loops, 14)
    assert enhanced_for.end_line == 16
    assert enhanced_for.context == "for (int x : xs)"
    assert enhanced_for.body == dedent(
        """\
        {
            max = x > max ? x : max;
        }"""
    )

    while_loop = unit_at_line(loops, 23)
    assert while_loop.end_line == 28
    assert while_loop.context == "while (n > 0)"
    assert while_loop.body == dedent(
        """\
        {
            long next = a + b;
            a = b;
            b = next;
            n = n - 1;
        }"""
    )

    do_while = unit_at_line(loops, 34)
    assert do_while.end_line == 37
    assert do_while.context == "do"
    assert do_while.body == dedent(
        """\
        {
            n = n / 10;
            count = count + 1;
        }"""
    )


def test_extracts_exception_handling_blocks_with_full_body_and_context():
    exceptions = parse((FIXTURES / "Exceptions.java").read_bytes())

    assert len(exceptions) == 11

    try_body = unit_at_line(exceptions, 5)
    assert try_body.end_line == 8
    assert try_body.context == "try"
    assert try_body.body == dedent(
        """\
        {
            value = Integer.parseInt(text);
            value = value * 2;
        }"""
    )

    catch_body = unit_at_line(exceptions, 8)
    assert catch_body.end_line == 11
    assert catch_body.context == "catch (NumberFormatException e)"
    assert catch_body.body == dedent(
        """\
        {
            value = 0;
            text = e.getMessage();
        }"""
    )

    finally_body = unit_at_line(exceptions, 11)
    assert finally_body.end_line == 14
    assert finally_body.context == "finally"
    assert finally_body.body == dedent(
        """\
        {
            text = text.trim();
            value = value + text.length();
        }"""
    )

    first_catch = unit_at_line(exceptions, 23)
    assert first_catch.end_line == 26
    assert first_catch.context == "catch (ArrayIndexOutOfBoundsException e)"
    assert first_catch.body == dedent(
        """\
        {
            result = fallback;
            fallback = fallback - 1;
        }"""
    )

    second_catch = unit_at_line(exceptions, 26)
    assert second_catch.end_line == 28
    assert second_catch.context == "catch (NullPointerException e)"
    assert second_catch.body == dedent(
        """\
        {
            result = 0;
        }"""
    )

    resource_try = unit_at_line(exceptions, 34)
    assert resource_try.end_line == 37
    assert (
        resource_try.context
        == "try (BufferedReader reader = new BufferedReader(source))"
    )
    assert resource_try.body == dedent(
        """\
        {
            line = reader.readLine();
            line = line.trim();
        }"""
    )

    resource_catch = unit_at_line(exceptions, 37)
    assert resource_catch.end_line == 39
    assert resource_catch.context == "catch (IOException e)"
    assert resource_catch.body == dedent(
        """\
        {
            line = "";
        }"""
    )


def test_extracts_switch_cases_with_full_body_and_context():
    switch = parse((FIXTURES / "Switch.java").read_bytes())

    assert len(switch) == 8

    first_case = unit_at_line(switch, 6)
    assert first_case.end_line == 9
    assert first_case.context == "case 1:"
    assert first_case.body == dedent(
        """\
        name = "red";
        name = name.toUpperCase();
        break;"""
    )

    second_case = unit_at_line(switch, 10)
    assert second_case.end_line == 13
    assert second_case.context == "case 2:"
    assert second_case.body == dedent(
        """\
        name = "green";
        name = name + "!";
        break;"""
    )

    default_case = unit_at_line(switch, 14)
    assert default_case.end_line == 16
    assert default_case.context == "default:"
    assert default_case.body == dedent(
        """\
        name = "unknown";
        name = name.substring(0, 3);"""
    )

    arrow_a = unit_at_line(switch, 24)
    assert arrow_a.end_line == 27
    assert arrow_a.context == 'case "A" ->'
    assert arrow_a.body == dedent(
        """\
        {
            score = 4;
            score = score * 10;
        }"""
    )

    arrow_b = unit_at_line(switch, 28)
    assert arrow_b.end_line == 31
    assert arrow_b.context == 'case "B" ->'
    assert arrow_b.body == dedent(
        """\
        {
            score = 3;
            score = score + 1;
        }"""
    )

    arrow_default = unit_at_line(switch, 32)
    assert arrow_default.end_line == 34
    assert arrow_default.context == "default ->"
    assert arrow_default.body == dedent(
        """\
        {
            score = 0;
        }"""
    )


def test_extracts_nested_blocks_with_full_body_and_context():
    nesting = parse((FIXTURES / "NestedBlocks.java").read_bytes())

    loop = unit_at_line(nesting, 5)
    assert loop.end_line == 13
    assert loop.context == "for (int x : xs)"
    assert loop.body_node_count == 29
    assert loop.body == dedent(
        """\
        {
            if (x > threshold) {
                try {
                    total = total + 100 / x;
                } catch (ArithmeticException e) {
                    total = total - 1;
                }
            }
        }"""
    )

    conditional = unit_at_line(nesting, 6)
    assert conditional.end_line == 12
    assert conditional.context == "if (x > threshold)"
    assert conditional.body_node_count == 23
    assert conditional.body == dedent(
        """\
        {
            try {
                total = total + 100 / x;
            } catch (ArithmeticException e) {
                total = total - 1;
            }
        }"""
    )

    try_body = unit_at_line(nesting, 7)
    assert try_body.end_line == 9
    assert try_body.context == "try"
    assert try_body.body_node_count == 9
    assert try_body.body == dedent(
        """\
        {
            total = total + 100 / x;
        }"""
    )

    catch_body = unit_at_line(nesting, 9)
    assert catch_body.end_line == 11
    assert catch_body.context == "catch (ArithmeticException e)"
    assert catch_body.body_node_count == 7
    assert catch_body.body == dedent(
        """\
        {
            total = total - 1;
        }"""
    )


def test_extracts_allman_braced_conditional_branches():
    formatting = parse((FIXTURES / "Formatting.java").read_bytes())

    tier = unit_at_line(formatting, 3)
    assert tier.end_line == 21
    assert tier.kind == "function"
    assert tier.context == "String tier(int score)"

    if_branch = unit_at_line(formatting, 6)
    assert if_branch.end_line == 10
    assert if_branch.context == "if (score >= 90)"
    assert if_branch.body == dedent(
        """\
        {
            label = "gold";
            score -= 90;
        }"""
    )

    else_if_branch = unit_at_line(formatting, 11)
    assert else_if_branch.end_line == 14
    assert else_if_branch.context == "if (score >= 50)"
    assert else_if_branch.body == dedent(
        """\
        {
            label = "silver";
        }"""
    )

    else_branch = unit_at_line(formatting, 15)
    assert else_branch.end_line == 19
    assert else_branch.context == "else"
    assert else_branch.body == dedent(
        """\
        {
            label = "bronze";
            score = 0;
        }"""
    )


def test_extracts_function_and_loop_with_multiline_headers():
    formatting = parse((FIXTURES / "Formatting.java").read_bytes())

    product = unit_at_line(formatting, 23)
    assert product.end_line == 34
    assert product.kind == "function"
    assert product.context == dedent(
        """\
        long product(
                int[] factors,
                int start
        )"""
    )

    loop = unit_at_line(formatting, 28)
    assert loop.end_line == 32
    assert loop.context == dedent(
        """\
        for (int i = start;
        i < factors.length;
        i++)"""
    )
    assert loop.body == dedent(
        """\
        {
            total *= factors[i];
        }"""
    )


def test_extracts_exception_blocks_with_multiline_headers():
    formatting = parse((FIXTURES / "Formatting.java").read_bytes())

    try_body = unit_at_line(formatting, 39)
    assert try_body.end_line == 45
    assert try_body.context == dedent(
        """\
        try (
                BufferedReader reader = source;
                Closeable guard = source
        )"""
    )
    assert try_body.body == dedent(
        """\
        {
            value = Integer.parseInt(reader.readLine());
            value = value * 2;
        }"""
    )

    catch_body = unit_at_line(formatting, 46)
    assert catch_body.end_line == 50
    assert catch_body.context == dedent(
        """\
        catch (IOException
        | NumberFormatException e)"""
    )
    assert catch_body.body == dedent(
        """\
        {
            value = fallback;
        }"""
    )


def test_replaces_invalid_utf8_bytes_and_extracts_surrounding_function():
    units = parse(
        b'class C {\n    String greet() {\n        return "a\xffb";\n    }\n}\n'
    )

    greet = unit_at_line(units, 2)
    assert greet.context == "String greet()"
    assert greet.body == dedent(
        """\
        {
            return "a�b";
        }"""
    )
