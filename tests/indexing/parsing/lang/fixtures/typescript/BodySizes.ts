const square = (n: number): number => n * n;

function noop(): void {}

async function loadAll(ids: number[], limit: number): Promise<Item[]> {
  const results: Item[] = [];
  for (const id of ids) {
    if (results.length >= limit) {
      break;
    }
    const item = await fetch(`/items/${id}`);
    results.push(await item.json());
  }
  return results;
}
