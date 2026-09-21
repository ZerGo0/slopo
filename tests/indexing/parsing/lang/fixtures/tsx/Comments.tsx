// A line comment
function withComments(props: Props): JSX.Element {
  /* block comment */
  const label = props.label; // trailing
  return (
    <div>
      {/* a jsx comment */}
      <span>{label}</span>
      <span>{/* only comment */}</span>
      <span>{value /* trailing comment */}</span>
      <span class="empty-expression-stays">{}</span>
    </div>
  );
}
