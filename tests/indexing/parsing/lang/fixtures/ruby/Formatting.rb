class Styles
  def combine(
    first,
    second
  )
    first * second + first
  end

  def label(code, count)
    case code
    when 1 then "one:#{count}"
    when 2 then "two:#{count * 2}"
    else "many:#{count}"
    end
  end
end
