class Report
  # scale the amount by the rate

  def summary(amount, rate, count)

    scaled = amount * rate # apply the rate

=begin
The subtotal below multiplies the scaled amount
by the count and rounds to whole units.
=end

    subtotal = (scaled * count).round

    "batch ##{count}: #{subtotal}"
  end
end
