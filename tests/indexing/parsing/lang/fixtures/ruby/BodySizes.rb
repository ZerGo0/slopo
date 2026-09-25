module Sizes
  def noop; end

  def double(x) = x * 2

  def blend(a, b, c)
    weighted = a * 3 + b * 2 + c
    average = weighted / 6.0
    average.round(2)
  end

  def score(a, b, c, d)
    base = a * 100 + b * 10 + c
    scaled = base * d
    adjusted = scaled - (a + b + c + d)
    ratio = adjusted / (d + 1)
    parts = [base, scaled, adjusted, ratio]
    total = parts.sum
    average = total / parts.length
    spread = parts.max - parts.min
    [average, spread, total]
  end
end
