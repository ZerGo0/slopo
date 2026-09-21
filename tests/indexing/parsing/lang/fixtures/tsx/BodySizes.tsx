const Dot = () => <i />;

function Card(props: CardProps): JSX.Element {
  return (
    <article className="card">
      <header>
        <h3>{props.title}</h3>
      </header>
      <p>{props.body}</p>
    </article>
  );
}

function total(nums: number[]): number {
  let sum = 0;
  for (const n of nums) {
    sum += n;
  }
  return sum;
}
