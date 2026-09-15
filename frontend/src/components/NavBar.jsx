import "./NavBar.css";

const TABS = [
  { id: "daily", label: "Daily" },
  { id: "practice", label: "Practice" },
  { id: "leaderboard", label: "Leaderboard" },
];

export default function NavBar({ view, onNavigate, user, onLogout }) {
  return (
    <header className="navbar">
      <div className="navbar-inner">
        <span className="wordmark">
          Sudo<span className="wordmark-accent">Rank</span>
        </span>

        <nav className="navbar-tabs">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              className={"tab" + (view === tab.id ? " active" : "")}
              onClick={() => onNavigate(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        <div className="navbar-auth">
          {user ? (
            <>
              <span className="hint">{user.username}</span>
              <button className="secondary" onClick={onLogout}>
                Log out
              </button>
            </>
          ) : (
            <button className="secondary" onClick={() => onNavigate("auth")}>
              Log in
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
