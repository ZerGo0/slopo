class Grader
  def tier(score, streak)
    bonus = streak * 2
    if score + bonus >= 90
      grade = "gold"
      reward = score + bonus - 90
      [grade, reward]
    elsif score >= 50
      grade = "silver"
      [grade, streak]
    else
      grade = "bronze"
      penalty = 50 - score
      [grade, penalty]
    end
  end

  def clamp(value, floor, ceil)
    value = floor if value < floor
    value = ceil unless value <= ceil
    span = ceil - floor
    [value, span]
  end

  def describe(flag, count)
    if flag then
      label = "on"
      "#{label}:#{count}"
    else
      "off:#{count * 0}"
    end
  end
end
