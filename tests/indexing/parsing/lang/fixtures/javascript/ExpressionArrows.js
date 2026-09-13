const buildUser = (raw) => ({
  id: raw.id,
  name: raw.first + " " + raw.last,
  active: raw.status === "on",
});

const classify = (score) =>
  score >= 90 ? "gold" : score >= 50 ? "silver" : "bronze";
