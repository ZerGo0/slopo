function joinParts(parts) {
  let out = "";
  for (const part of parts) {
    out = out + part;
    out = out + ",";
  }
  return out;
}

function fib(count) {
  let a = 0;
  let b = 1;
  for (let i = 0; i < count; i++) {
    const next = a + b;
    a = b;
    b = next;
  }
  return a;
}

function digits(value) {
  let steps = 0;
  while (value > 0) {
    value = Math.floor(value / 10);
    steps = steps + 1;
  }
  return steps;
}

function retry(task) {
  let attempts = 0;
  do {
    task();
    attempts = attempts + 1;
  } while (attempts < 3);
  return attempts;
}
