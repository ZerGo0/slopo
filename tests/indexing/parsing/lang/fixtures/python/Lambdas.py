def transform(values):
    doubler = lambda x: x * 2
    filtered = list(filter(lambda x: x > 0, values))
    ranked = sorted(filtered, key=lambda x: -x)
    return ranked


classify = lambda x: (
    "high" if x > 90
    else "mid" if x > 50
    else "low"
)

extract = lambda items: [
    x * 2
    for x in items
    if x > 0
]
