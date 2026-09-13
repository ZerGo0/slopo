export function add(a, b) {
  return a + b;
}

async function fetchUser(id) {
  const response = await fetch(`/users/${id}`);
  return response.json();
}

function* countUp(limit) {
  let n = 0;
  while (n < limit) {
    yield n;
    n += 1;
  }
}

function sumEvens(nums) {
  let total = 0;
  for (const n of nums) {
    if (n % 2 === 0) {
      total += n;
    }
  }
  return total;
}

class Counter {
  constructor(start) {
    this.value = start;
  }

  increment(step) {
    this.value += step;
    return this.value;
  }

  get current() {
    return this.value;
  }

  static zero() {
    return new Counter(0);
  }

  async loadFrom(source) {
    const saved = await source.read();
    this.value = saved.value;
  }
}
