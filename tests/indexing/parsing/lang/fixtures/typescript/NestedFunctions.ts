function makeCounter(start: number): () => number {
  let count = start;

  function increment(): number {
    count += 1;
    return count;
  }

  return increment;
}
