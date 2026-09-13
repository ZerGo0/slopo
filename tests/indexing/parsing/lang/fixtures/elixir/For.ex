defmodule Fors do
  def transform(items) do
    for item <- items, item > 0 do
      doubled = item * 2
      label = "item_#{doubled}"
      {label, doubled}
    end

    for {k, v} <- items, v != nil do
      processed = String.upcase(k)
      {processed, v + 1}
    end
  end
end
