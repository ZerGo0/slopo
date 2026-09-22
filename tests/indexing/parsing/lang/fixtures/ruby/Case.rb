class Router
  def score(event, weight)
    weight = weight.abs
    case event
    when :create
      base = weight * 10
      bonus = base + 5
      [base, bonus]
    when :update, :patch
      adjusted = weight - 1
      [adjusted, adjusted * 2]
    else
      [0, weight]
    end
  end

  def measure(shape)
    scale = 2
    case shape
    in [x, y]
      dx = x * x
      dy = y * y
      (dx + dy) * scale
    in {radius:}
      radius * radius * scale
    end
  end
end
