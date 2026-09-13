def parse_int(text):
    value = 0
    try:
        value = int(text)
        value = value * 2
    except ValueError as e:
        value = -1
        text = str(e)
    finally:
        text = text.strip()
        value = value + len(text)
    return value


def element_at(xs, i, fallback):
    result = 0
    try:
        result = xs[i]
        result = result + i
    except IndexError:
        result = fallback
        fallback = fallback - 1
    except TypeError:
        result = 0
    return result
