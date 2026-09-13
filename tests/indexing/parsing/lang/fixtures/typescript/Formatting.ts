function product(
  factors: number[],
  start: number,
): number {
  let total = start;
  for (const f of factors) {
    total *= f;
  }
  return total;
}

function allman(values: number[]): number
{
  let sum = 0;
  for (const v of values)
  {
    sum += v;
  }
  return sum;
}

function wrappedHeader(count: number): number {
  let acc = 1;
  for (
    let i = 1;
    i <= count;
    i += 1
  ) {
    acc *= i;
  }
  return acc;
}
