export function Header() {
  return (
    <header className="site-header">
      <div className="container site-header__inner">
        <a className="brand" href="#top" aria-label="WeatherScope home">
          <span className="brand__mark" aria-hidden="true">W</span>
          <span>
            <strong>WeatherScope</strong>
            <small>Weather intelligence for practical planning</small>
          </span>
        </a>
        <nav aria-label="Primary navigation">
          <a href="#weather">Weather</a>
          <a href="#saved-searches">Saved searches</a>
          <a href="#about">About</a>
        </nav>
      </div>
    </header>
  );
}
