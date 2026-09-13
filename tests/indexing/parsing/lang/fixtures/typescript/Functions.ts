export function add(a: number, b: number): number {
  return a + b;
}

async function fetchUser(id: number): Promise<User> {
  const response = await fetch(`/users/${id}`);
  return response.json();
}

function* countUp(limit: number): Generator<number> {
  let n = 0;
  while (n < limit) {
    yield n;
    n += 1;
  }
}

function sumEvens(nums: number[]): number {
  let total = 0;
  for (const n of nums) {
    if (n % 2 === 0) {
      total += n;
    }
  }
  return total;
}

class Counter {
  constructor(start: number) {
    this.value = start;
  }

  increment(step: number): number {
    this.value += step;
    return this.value;
  }

  get current(): number {
    return this.value;
  }

  static zero(): Counter {
    return new Counter(0);
  }

  async loadFrom(source: Source): Promise<void> {
    const saved = await source.read();
    this.value = saved.value;
  }
}
