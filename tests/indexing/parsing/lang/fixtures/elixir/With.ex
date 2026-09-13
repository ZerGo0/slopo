defmodule Withs do
  def process(input) do
    with {:ok, a} <- fetch(input),
         {:ok, b} <- transform(a) do
      result = a + b
      format(result)
      {:ok, result}
    else
      {:error, reason} ->
        msg = format_error(reason)
        notify(msg)
        {:failure, msg}
      :not_found ->
        :missing
    end
  end
end
