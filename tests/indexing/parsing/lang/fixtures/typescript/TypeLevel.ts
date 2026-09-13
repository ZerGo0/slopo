interface Repo {
  find(id: number): User;
  save(u: User): Promise<void>;
}

type Handler = (e: Event) => void;

enum Color {
  Red,
  Green,
  Blue,
}

abstract class Base {
  abstract compute(x: number): number;

  render(prefix: string, suffix: string): string {
    const body = prefix + this.name;
    return body + suffix;
  }
}

declare function ambient(x: number): void;

function overloaded(x: number): number;
function overloaded(x: string): string;
function overloaded(x: unknown): unknown {
  return x;
}

namespace Geometry {
  export function area(r: number): number {
    return Math.PI * r * r;
  }
}
