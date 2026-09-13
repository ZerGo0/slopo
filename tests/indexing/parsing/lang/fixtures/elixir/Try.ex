defmodule Tries do
  def safe_parse(text) do
    try do
      value = String.to_integer(text)
      value = value * 2
      {:ok, value}
    rescue
      e in ArgumentError ->
        msg = Exception.message(e)
        Logger.warn(msg)
        {:error, msg}
    catch
      :exit, reason ->
        detail = inspect(reason)
        Logger.error(detail)
        {:crash, detail}
    after
      IO.puts("done")
      flush()
    end
  end
end
