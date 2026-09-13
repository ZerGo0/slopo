def process(xs, threshold):
    total = 0
    for x in xs:
        if x > threshold:
            try:
                total = total + 100 // x
            except ZeroDivisionError:
                total = total - 1
    return total
