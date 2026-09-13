function tier(score: number): string {
  let label = "";
  if (score >= 90) {
    label = "gold";
    return label;
  } else if (score >= 50) {
    label = "silver";
    label = label + "!";
  } else {
    label = "bronze";
  }
  return label;
}

function clamp(value: number, min: number, max: number): number {
  let adjusted = value;
  if (value < min) {
    const deficit = min - value;
    adjusted = min + deficit / 2;
  }
  if (value > max) {
    adjusted = max;
    adjusted = adjusted - 1;
  }
  return adjusted;
}
