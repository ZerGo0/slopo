function product(
  factors,
  start,
) {
  let total = start;
  for (const f of factors) {
    total *= f;
  }
  return total;
}
