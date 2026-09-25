from pathlib import Path
from textwrap import dedent

from slopo.indexing.parsing.lang.tsx import parse

from .conftest import unit_at_line

FIXTURES = Path(__file__).parent / "fixtures" / "tsx"


def test_strips_comments_keeping_blank_lines_and_spaces():
    unit = parse((FIXTURES / "Comments.tsx").read_bytes())[0]

    assert unit.start_line == 2
    assert unit.end_line == 14
    assert unit.context == "function withComments(props: Props): JSX.Element"
    assert unit.body_node_count == 44
    assert unit.body == dedent(
        """\
        {

          const label = props.label;
          return (
            <div>

              <span>{label}</span>
              <span>                    </span>
              <span>{value                       }</span>
              <span class="empty-expression-stays">{}</span>
            </div>
          );
        }"""
    )


def test_body_node_count_across_template_and_logic_shapes():
    body_sizes = parse((FIXTURES / "BodySizes.tsx").read_bytes())

    dot = unit_at_line(body_sizes, 1)
    assert dot.body_node_count == 2

    card = unit_at_line(body_sizes, 4)
    assert card.body_node_count == 33

    total = unit_at_line(body_sizes, 14)
    assert total.body_node_count == 15


def test_extracts_component_with_its_returned_template_block():
    units = parse((FIXTURES / "Component.tsx").read_bytes())

    panel = unit_at_line(units, 1)
    assert panel.end_line == 15
    assert panel.kind == "function"
    assert panel.context == "function UserPanel(props: PanelProps): JSX.Element"
    assert panel.body == dedent(
        """\
        {
          const label = props.name.trim();
          const badges = [];
          for (const role of props.roles) {
            if (role.active) {
              badges.push(role.name);
            }
          }
          return (
            <section className="user-panel">
              <h2>{label}</h2>
              <BadgeRow items={badges} />
            </section>
          );
        }"""
    )

    template = unit_at_line(units, 9)
    assert template.end_line == 14
    assert template.kind == "block"
    assert template.context == "function UserPanel(props: PanelProps): JSX.Element"
    assert template.body == dedent(
        """\
        (
          <section className="user-panel">
            <h2>{label}</h2>
            <BadgeRow items={badges} />
          </section>
        )"""
    )


def test_extracts_loop_and_conditional_blocks_nested_in_component():
    units = parse((FIXTURES / "Component.tsx").read_bytes())

    loop = unit_at_line(units, 4)
    assert loop.end_line == 8
    assert loop.context == "for (const role of props.roles)"
    assert loop.body == dedent(
        """\
        {
          if (role.active) {
            badges.push(role.name);
          }
        }"""
    )

    branch = unit_at_line(units, 5)
    assert branch.end_line == 7
    assert branch.context == "if (role.active)"
    assert branch.body == dedent(
        """\
        {
          badges.push(role.name);
        }"""
    )


def test_extracts_switch_case_and_try_catch_blocks():
    units = parse((FIXTURES / "Blocks.tsx").read_bytes())

    increment = unit_at_line(units, 3)
    assert increment.end_line == 4
    assert increment.context == 'case "increment":'
    assert increment.body == "return { ...state, count: state.count + 1 };"

    reset = unit_at_line(units, 5)
    assert reset.end_line == 7
    assert reset.context == 'case "reset":'
    assert reset.body == dedent(
        """\
        state = initialState;
        return state;"""
    )

    try_block = unit_at_line(units, 15)
    assert try_block.end_line == 18
    assert try_block.context == "try"
    assert try_block.body == dedent(
        """\
        {
          const res = await fetch(`/users/${id}`);
          user = await res.json();
        }"""
    )

    catch_block = unit_at_line(units, 18)
    assert catch_block.end_line == 21
    assert catch_block.context == "catch (err)"
    assert catch_block.body == dedent(
        """\
        {
          log(err);
          user = guestUser();
        }"""
    )


def test_extracts_units_from_react_component_with_hooks():
    units = parse((FIXTURES / "Hooks.tsx").read_bytes())

    memo = unit_at_line(units, 4)
    assert memo.end_line == 12
    assert memo.kind == "function"
    assert memo.context == "() =>"
    assert memo.body == dedent(
        """\
        {
          const matches = [];
          for (const item of props.items) {
            if (item.name.includes(query)) {
              matches.push(item);
            }
          }
          return matches;
        }"""
    )

    callback = unit_at_line(units, 15)
    assert callback.end_line == 17
    assert callback.kind == "function"
    assert callback.context == "(event: ChangeEvent) =>"
    assert callback.body == dedent(
        """\
        {
          setQuery(event.target.value);
        }"""
    )

    template = unit_at_line(units, 21)
    assert template.end_line == 26
    assert template.kind == "block"
    assert template.context == "function SearchBox(props: SearchBoxProps): JSX.Element"
    assert template.body == dedent(
        """\
        (
          <div className="search-box">
            <input value={query} onChange={handleChange} />
            <ResultList results={results} />
          </div>
        )"""
    )


def test_extracts_returned_templates_across_syntactic_forms():
    units = parse((FIXTURES / "Templates.tsx").read_bytes())

    assert len(units) == 6

    banner = unit_at_line(units, 2)
    assert banner.end_line == 6
    assert banner.kind == "block"
    assert banner.context == "function Banner()"
    assert banner.body == dedent(
        """\
        (
          <header className="banner">
            <h1>Welcome</h1>
          </header>
        )"""
    )

    sidebar = unit_at_line(units, 10)
    assert sidebar.end_line == 14
    assert sidebar.kind == "block"
    assert sidebar.context == "Sidebar = () =>"
    assert sidebar.body == dedent(
        """\
        (
          <aside>
            <nav>{links}</nav>
          </aside>
        )"""
    )

    footer = unit_at_line(units, 17)
    assert footer.end_line == 21
    assert footer.kind == "block"
    assert footer.context == "Footer = () =>"
    assert footer.body == dedent(
        """\
        (
          <footer>
            <small>{year}</small>
          </footer>
        )"""
    )

    spacer = unit_at_line(units, 23)
    assert spacer.end_line == 23
    assert spacer.kind == "block"
    assert spacer.context == "Spacer = () =>"
    assert spacer.body == '<div className="spacer" />'

    divider = unit_at_line(units, 26)
    assert divider.end_line == 26
    assert divider.kind == "block"
    assert divider.context == "function Divider()"
    assert divider.body == '<hr className="divider" />'

    group = unit_at_line(units, 29)
    assert group.end_line == 34
    assert group.kind == "block"
    assert group.context == "Group = () =>"
    assert group.body == dedent(
        """\
        (
          <>
            <Spacer />
            <Divider />
          </>
        )"""
    )


def test_extracts_every_returned_template_when_component_keeps_logic():
    units = parse((FIXTURES / "ConditionalReturns.tsx").read_bytes())

    assert len(units) == 4

    status = unit_at_line(units, 1)
    assert status.end_line == 10
    assert status.kind == "function"
    assert status.context == "function Status(props: StatusProps): JSX.Element"
    assert status.body == dedent(
        """\
        {
          if (props.loading) {
            return <Spinner size="large" />;
          }
          return (
            <div className="status">
              <span>{props.message}</span>
            </div>
          );
        }"""
    )

    guard = unit_at_line(units, 2)
    assert guard.end_line == 4
    assert guard.kind == "block"
    assert guard.context == "if (props.loading)"
    assert guard.body == dedent(
        """\
        {
          return <Spinner size="large" />;
        }"""
    )

    guard_template = unit_at_line(units, 3)
    assert guard_template.end_line == 3
    assert guard_template.kind == "block"
    assert guard_template.context == "function Status(props: StatusProps): JSX.Element"
    assert guard_template.body == '<Spinner size="large" />'

    main_template = unit_at_line(units, 5)
    assert main_template.end_line == 9
    assert main_template.kind == "block"
    assert main_template.context == "function Status(props: StatusProps): JSX.Element"
    assert main_template.body == dedent(
        """\
        (
          <div className="status">
            <span>{props.message}</span>
          </div>
        )"""
    )


def test_skips_type_level_and_bodyless_declarations():
    units = parse((FIXTURES / "TypeLevel.tsx").read_bytes())

    assert len(units) == 2

    format_title = unit_at_line(units, 10)
    assert format_title.end_line == 13
    assert format_title.context == "function formatTitle(props: PanelProps): string"
    assert format_title.body == dedent(
        """\
        {
          const base = props.title.trim();
          return base.toUpperCase();
        }"""
    )

    noop = unit_at_line(units, 15)
    assert noop.end_line == 15
    assert noop.context == "noop = (): void =>"
    assert noop.body == "{}"


def test_nested_markup_extracts_only_control_flow_and_return_templates():
    units = parse((FIXTURES / "Nested.tsx").read_bytes())

    assert len(units) == 5

    component = unit_at_line(units, 1)
    assert component.end_line == 24
    assert component.context == "function TagList(props: TagListProps): JSX.Element"
    assert component.body_node_count == 125
    assert component.body == dedent(
        """\
        {
          if (props.tags.length > 0) {
            return (
              <ul className="tags">
                <li className="tags__header">
                  <span className="tags__title">Tags</span>
                  <span className="tags__count">{props.tags.length}</span>
                </li>
                {props.tags.map((tag) => (
                  <li key={tag.id} className="tags__item">
                    <a href={tag.url}>
                      <span className="tags__label">{tag.label}</span>
                    </a>
                  </li>
                ))}
              </ul>
            );
          }
          return (
            <div className="tags--empty">
              <p>No tags</p>
            </div>
          );
        }"""
    )

    branch = unit_at_line(units, 2)
    assert branch.end_line == 18
    assert branch.context == "if (props.tags.length > 0)"
    assert branch.body_node_count == 98
    assert branch.body == dedent(
        """\
        {
          return (
            <ul className="tags">
              <li className="tags__header">
                <span className="tags__title">Tags</span>
                <span className="tags__count">{props.tags.length}</span>
              </li>
              {props.tags.map((tag) => (
                <li key={tag.id} className="tags__item">
                  <a href={tag.url}>
                    <span className="tags__label">{tag.label}</span>
                  </a>
                </li>
              ))}
            </ul>
          );
        }"""
    )

    outer_template = unit_at_line(units, 3)
    assert outer_template.end_line == 17
    assert (
        outer_template.context == "function TagList(props: TagListProps): JSX.Element"
    )
    assert outer_template.body_node_count == 96
    assert outer_template.body == dedent(
        """\
        (
          <ul className="tags">
            <li className="tags__header">
              <span className="tags__title">Tags</span>
              <span className="tags__count">{props.tags.length}</span>
            </li>
            {props.tags.map((tag) => (
              <li key={tag.id} className="tags__item">
                <a href={tag.url}>
                  <span className="tags__label">{tag.label}</span>
                </a>
              </li>
            ))}
          </ul>
        )"""
    )

    inner_template = unit_at_line(units, 9)
    assert inner_template.end_line == 15
    assert inner_template.context == "(tag) =>"
    assert inner_template.body_node_count == 40
    assert inner_template.body == dedent(
        """\
        (
          <li key={tag.id} className="tags__item">
            <a href={tag.url}>
              <span className="tags__label">{tag.label}</span>
            </a>
          </li>
        )"""
    )

    empty_template = unit_at_line(units, 19)
    assert empty_template.end_line == 23
    assert (
        empty_template.context == "function TagList(props: TagListProps): JSX.Element"
    )
    assert empty_template.body_node_count == 16
    assert empty_template.body == dedent(
        """\
        (
          <div className="tags--empty">
            <p>No tags</p>
          </div>
        )"""
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
