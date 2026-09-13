function describe(n: number): string {
  let out = "";
  switch (n) {
    case 0:
      out = "zero";
      return out;
    case 1:
    case 2:
      out = "small";
      return out + "!";
    default:
      out = "many";
      return out;
  }
}
