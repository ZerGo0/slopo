module Billing
  def self.rate(tier)
    base = tier * 5
    base + 1
  end

  class Invoice
    def total(subtotal, tax)
      taxed = subtotal * tax
      subtotal + taxed
    end
  end
end
