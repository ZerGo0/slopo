const buildUser = (raw: RawUser): User => ({
  id: raw.id,
  name: raw.first + " " + raw.last,
  active: raw.status === "on",
});

const classify = (score: number): string =>
  score >= 90 ? "gold" : score >= 50 ? "silver" : "bronze";
