class Account
  def deposit(balance, amount, fee_rate)
    fee = amount * fee_rate
    credited = amount - fee
    updated = balance + credited
    growth = updated - balance
    [updated, credited, growth]
  end

  def self.opening(owner, seed, tier)
    prefix = owner.upcase
    handle = "#{prefix}##{tier}"
    starting = seed * 100 + tier
    "#{handle}:#{starting}"
  end

  def fee(balance) = balance * 0.02

  def statement(owner, entries)
    header = "#{owner.capitalize} (#{entries.length})"
    total = entries.sum
    average = total / entries.length
    high = entries.max
    low = entries.min
    spread = high - low
    "#{header} total #{total} avg #{average} spread #{spread}"
  end
end
