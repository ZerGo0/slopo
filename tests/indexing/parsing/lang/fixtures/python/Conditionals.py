def categorize(score, bonus):
    label = ""
    if score >= 90:
        label = "excellent"
        score = score - bonus
    elif score >= 70:
        base = score - 70
        label = f"good ({base})"
    elif score >= 50:
        label = "average"
    else:
        label = "below average"
        score = 0
        bonus = 0
    return label, score


def clamp(value, lo, hi):
    adjusted = value
    if value < lo:
        deficit = lo - value
        adjusted = lo + deficit // 2
    elif value > hi:
        adjusted = hi
        return adjusted - 1
    return adjusted
