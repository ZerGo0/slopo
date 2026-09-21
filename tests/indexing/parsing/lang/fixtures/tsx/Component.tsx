export function UserPanel(props: PanelProps): JSX.Element {
  const label = props.name.trim();
  const badges = [];
  for (const role of props.roles) {
    if (role.active) {
      badges.push(role.name);
    }
  }
  return (
    <section className="user-panel">
      <h2>{label}</h2>
      <BadgeRow items={badges} />
    </section>
  );
}
