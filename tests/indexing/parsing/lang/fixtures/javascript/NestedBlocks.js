function scan(xs, threshold) {
  let total = 0;
  for (const x of xs) {
    if (x > threshold) {
      switch (x % 2) {
        case 0:
          total = total + 100;
          total = total - 1;
          break;
        default:
          total = total + x;
      }
    }
  }
  return total;
}
