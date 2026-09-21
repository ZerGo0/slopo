export function TagList(props: TagListProps): JSX.Element {
  if (props.tags.length > 0) {
    return (
      <ul className="tags">
        <li className="tags__header">
          <span className="tags__title">Tags</span>
          <span className="tags__count">{props.tags.length}</span>
        </li>
        {props.tags.map((tag) => (
          <li key={tag.id} className="tags__item">
            <a href={tag.url}>
              <span className="tags__label">{tag.label}</span>
            </a>
          </li>
        ))}
      </ul>
    );
  }
  return (
    <div className="tags--empty">
      <p>No tags</p>
    </div>
  );
}
