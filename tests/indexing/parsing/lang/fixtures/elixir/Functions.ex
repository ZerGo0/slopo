defmodule Calculator do
  @moduledoc "Arithmetic helpers."

  def add(a, b) do
    a + b
  end

  def greet(name) do
    "Hello, #{name}!"
  end

  defp normalize(value) when is_binary(value) do
    value
    |> String.trim()
    |> String.downcase()
  end

  def repeat(text, count), do: String.duplicate(text, count)
end
