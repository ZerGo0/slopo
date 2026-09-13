defmodule Tasks do
  def make_task(label) do
    fn ->
      IO.puts(label)
    end
  end
end
