prefix = "Hello"


def greet(name):
    return f"{prefix}, {name}!"


def classify(n):
    if n < 0:
        return "negative"
    elif n == 0:
        return "zero"
    else:
        return "positive"


def sum_evens(numbers):
    return sum(x for x in numbers if x % 2 == 0)


def _identity(f):
    return f


@_identity
def decorated(items):
    total = sum(items)
    return total * 2


class Counter:
    def __init__(self, start=0):
        self.value = start

    def increment(self, by=1):
        self.value += by
        return self.value
