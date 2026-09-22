class Pipeline
  define_method(:scale) do |value, factor|
    scaled = value * factor
    scaled.round
  end

  def run(numbers, offset)
    shift = ->(n) { n + offset }
    totals = []
    numbers.each do |n|
      base = shift.call(n)
      totals << base * base
    end
    doubled = numbers.map do |n|
      squared = n * n
      squared + offset
    end
    positive = lambda { |x|
      shifted = x.abs
      shifted + offset
    }
    pack = Proc.new { |a, b|
      total = a + b
      gap = a - b
      { sum: total, diff: gap }
    }
    totals.sum + doubled.sum + positive.call(-5) + pack.call(1, 2)[:sum]
  end
end
