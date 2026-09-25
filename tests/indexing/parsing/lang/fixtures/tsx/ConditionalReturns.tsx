export function Status(props: StatusProps): JSX.Element {
  if (props.loading) {
    return <Spinner size="large" />;
  }
  return (
    <div className="status">
      <span>{props.message}</span>
    </div>
  );
}
