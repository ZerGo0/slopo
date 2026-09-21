from pathlib import Path

import pytest

from slopo.indexing.parsing.lang.svelte import parse

from .conftest import unit_at_line

FIXTURES = Path(__file__).parent / "fixtures" / "svelte"


def _unit_with_context(units, context: str):
    matches = [unit for unit in units if unit.context == context]
    assert len(matches) == 1, f"expected one unit with context {context!r}"
    return matches[0]


def test_extracts_javascript_and_typescript_from_module_and_instance_scripts():
    units = parse((FIXTURES / "Component.svelte").read_bytes())

    configure = unit_at_line(units, 3)
    assert configure.kind == "function"
    assert configure.context == "function configure(value)"
    assert configure.end_line == 5
    assert "return value + 1;" in configure.body
    assert configure.language == "javascript"

    process = unit_at_line(units, 10)
    assert process.kind == "function"
    assert process.context == "function process(value: number): string"
    assert process.end_line == 15
    assert "return `value:${value}`;" in process.body
    assert process.language == "typescript"

    nested_if = unit_at_line(units, 11)
    assert nested_if.kind == "block"
    assert nested_if.context == "if (value > 0)"
    assert nested_if.end_line == 13
    assert nested_if.language == "typescript"

    decorate = unit_at_line(units, 17)
    assert decorate.kind == "function"
    assert decorate.context == "decorate = (value: string) =>"
    assert "return value.trim();" in decorate.body
    assert decorate.language == "typescript"


@pytest.mark.parametrize(
    "template",
    [
        "{#if ready}<p>Ready</p>{:else}<p>Waiting</p>{/if}",
        "{#each items as item}<li>{item}</li>{:else}<li>Empty</li>{/each}",
        "{#await request}<p>Loading</p>{:then result}<p>{result}</p>{/await}",
        "{#key selectedId}<p>{selectedId}</p>{/key}",
        "{#snippet row(item)}<li>{item}</li>{/snippet}",
    ],
)
def test_skips_template_blocks_and_snippets(template: str):
    assert parse(template.encode()) == []


def test_extracts_modern_and_legacy_inline_arrow_handlers_at_component_lines():
    units = parse((FIXTURES / "Component.svelte").read_bytes())

    save = unit_at_line(units, 32)
    assert save.kind == "function"
    assert save.context == "(event: MouseEvent) =>"
    assert save.body == "save(event, process(1))"
    assert save.language == "typescript"

    cancel = unit_at_line(units, 33)
    assert cancel.kind == "function"
    assert cancel.context == "() =>"
    assert cancel.body == "cancel()"
    assert cancel.language == "typescript"


def test_ignores_comments_and_style_content():
    units = parse((FIXTURES / "Component.svelte").read_bytes())

    process = _unit_with_context(units, "function process(value: number): string")
    assert "This comment" not in process.body
    assert not any("Template markup is not indexed." in unit.body for unit in units)
    assert not any("ignored" in (unit.context or "") for unit in units)
    assert not any("rebeccapurple" in unit.body for unit in units)


def test_skips_scripts_with_an_unsupported_language():
    assert parse((FIXTURES / "UnsupportedLanguage.svelte").read_bytes()) == []


def test_nested_template_blocks_only_extract_callback_at_original_line():
    units = parse(
        b"""{#if ready}
  <ul>
    {#each items as item}
      <li onclick={() => select(item)}>{item}</li>
    {/each}
  </ul>
{/if}
"""
    )

    callback = unit_at_line(units, 4)
    assert len(units) == 1
    assert callback.context == "() =>"
    assert callback.body == "select(item)"
    assert callback.language == "javascript"
