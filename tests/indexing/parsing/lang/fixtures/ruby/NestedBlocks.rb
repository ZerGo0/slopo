class Aggregator
  def totals(rows, divisor)
    sums = []
    rows.each do |row|
      if row > 0
        begin
          scaled = row * 100
          sums << scaled / divisor
        rescue ZeroDivisionError
          sums << row
        end
      end
    end
    sums.sum
  end
end
