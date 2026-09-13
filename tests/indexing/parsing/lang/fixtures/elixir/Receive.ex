defmodule Receivers do
  def listen do
    receive do
      {:data, payload} ->
        parsed = decode(payload)
        process(parsed)
        {:ok, parsed}
      {:batch, items} ->
        results = Enum.map(items, &handle/1)
        {:ok, results}
      :stop ->
        :halted
    after
      5000 ->
        :timeout
    end
  end
end
