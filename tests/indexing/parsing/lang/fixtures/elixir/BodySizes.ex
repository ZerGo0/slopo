defmodule Sizes do
  def constant, do: :ok

  def empty_body do
  end

  def total(entries) do
    entries
    |> Enum.reject(&is_nil/1)
    |> Enum.reduce(0, fn amount, acc -> acc + amount end)
  end
end
