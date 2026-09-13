from slopo.indexing.parsing.base import CodeUnit


def unit_at_line(units: list[CodeUnit], line: int) -> CodeUnit:
    matches = [u for u in units if u.start_line == line]
    if not matches:
        raise AssertionError(f"no unit starts at line {line}")
    if len(matches) > 1:
        raise AssertionError(f"multiple units start at line {line}")
    return matches[0]
