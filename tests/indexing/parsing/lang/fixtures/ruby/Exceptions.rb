class Loader
  def ratio(values, index)
    result = 0
    begin
      picked = values.fetch(index)
      result = 100 / picked
    rescue IndexError
      result = -1
    rescue ZeroDivisionError => e
      offset = e.message.length
      result = offset - offset
    else
      result += 1
    ensure
      result = result.abs
    end
    result
  end

  def parse(text)
    Integer(text) rescue text.length
  end
end
