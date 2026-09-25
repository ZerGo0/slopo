export function SearchBox(props: SearchBoxProps): JSX.Element {
  const [query, setQuery] = useState("");

  const results = useMemo(() => {
    const matches = [];
    for (const item of props.items) {
      if (item.name.includes(query)) {
        matches.push(item);
      }
    }
    return matches;
  }, [props.items, query]);

  const handleChange = useCallback(
    (event: ChangeEvent) => {
      setQuery(event.target.value);
    },
    [setQuery],
  );

  return (
    <div className="search-box">
      <input value={query} onChange={handleChange} />
      <ResultList results={results} />
    </div>
  );
}
