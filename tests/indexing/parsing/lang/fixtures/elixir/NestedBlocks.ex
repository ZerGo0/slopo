defmodule Nesting do
  def process(items) do
    for item <- items do
      if item > 0 do
        try do
          total = 100 + div(1000, item)
          {:ok, total}
        rescue
          e in ArithmeticError ->
            Logger.warn(Exception.message(e))
            {:error, :overflow}
        end
      end
    end
  end
end
