/**
 * Combines two values.
 * @param a
 * @param b
 */
function withComments(a: number, b: number): number {
  // a leading line comment
  const sum = a + b; // a trailing line comment
  /* a block comment
     spanning lines */
  const url = "https://not-a-comment";
  return sum;
}
