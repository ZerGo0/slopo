def product(
    factors,
    start=1,
):
    total = start
    for factor in factors:
        total = total * factor
    return total


class Registry:
    @staticmethod
    def register(
        name,
        value,
    ):
        entry = {name: value}
        return entry
