defmodule Cases do
  def handle(event) do
    case event do
      {:ok, value} ->
        processed = value * 2
        log(processed)
        {:success, processed}
      {:error, reason} ->
        msg = format_error(reason)
        notify(msg)
        {:failure, msg}
      :timeout ->
        :retry
    end
  end
end
