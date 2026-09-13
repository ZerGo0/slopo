defmodule Conds do
  def classify(x) do
    cond do
      x > 100 ->
        label = "huge"
        weight = x * 10
        {label, weight}
      x > 0 ->
        label = "positive"
        weight = x
        {label, weight}
      true ->
        label = "non-positive"
        weight = 0
        {label, weight}
    end
  end
end
