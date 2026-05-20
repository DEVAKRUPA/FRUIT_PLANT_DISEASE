function Header() {
  return (
    <header className="app-header">
      <div className="brand-mark" aria-hidden="true">
        <span>{"\uD83C\uDF43"}</span>
      </div>
      <div>
        <h1>Fruit Plant Disease Detector</h1>
        <p>Detect diseases early, protect your harvest {"\uD83C\uDF43\uD83C\uDF43"}</p>
      </div>
    </header>
  );
}

export default Header;
