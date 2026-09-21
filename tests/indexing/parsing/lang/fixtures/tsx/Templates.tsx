function Banner() {
  return (
    <header className="banner">
      <h1>Welcome</h1>
    </header>
  );
}

const Sidebar = () => {
  return (
    <aside>
      <nav>{links}</nav>
    </aside>
  );
};

const Footer = () => (
  <footer>
    <small>{year}</small>
  </footer>
);

const Spacer = () => <div className="spacer" />;

function Divider() {
  return <hr className="divider" />;
}

const Group = () => (
  <>
    <Spacer />
    <Divider />
  </>
);
