def running_total(values):
    total = 0
    for x in values:
        total += x
        values.append(total)
    return values


def find_max(xs):
    best = xs[0]
    for x in xs:
        best = x if x > best else best
    return best


def fibonacci(n):
    a, b = 0, 1
    while n > 0:
        a, b = b, a + b
        n = n - 1
    return a
