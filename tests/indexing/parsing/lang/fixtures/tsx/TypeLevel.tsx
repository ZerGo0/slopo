interface PanelProps {
  title: string;
  onClose(): void;
}

type Variant = "primary" | "secondary";

declare function translate(key: string): string;

export function formatTitle(props: PanelProps): string {
  const base = props.title.trim();
  return base.toUpperCase();
}

const noop = (): void => {};
