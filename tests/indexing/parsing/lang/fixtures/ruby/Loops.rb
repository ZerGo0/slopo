class Sequences
  def countdown(start)
    log = []
    n = start
    while n > 0
      log << n * n
      n -= 1
    end
    log
  end

  def grow(seed, limit)
    value = seed
    until value >= limit
      value = value * 2 + 1
    end
    value - limit
  end

  def indexes(rows)
    seen = []
    for row in rows
      code = row * 10
      seen << code + 1
    end
    seen
  end

  def drain(stack)
    total = 0
    total += stack.pop while stack.any?
    total
  end

  def fill(buffer, size)
    buffer << buffer.length until buffer.length == size
    buffer.sum
  end
end
