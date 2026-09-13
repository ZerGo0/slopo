defmodule Conditionals do
  def categorize(score) do
    if score >= 90 do
      tier = "gold"
      bonus = score - 90
      {tier, bonus}
    else
      tier = "bronze"
      penalty = 90 - score
      {tier, penalty}
    end
  end

  def clamp(value, lo, hi) do
    if value < lo do
      deficit = lo - value
      adjusted = lo + div(deficit, 2)
      adjusted
    end

    unless value > hi do
      surplus = value - hi
      capped = hi - abs(surplus)
      capped
    end
  end
end
