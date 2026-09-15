import { useEffect, useState } from "react";
import NavBar from "./components/NavBar";
import AuthPanel from "./components/AuthPanel";
import DailyPuzzle from "./components/DailyPuzzle";
import Leaderboard from "./components/Leaderboard";
import Practice from "./components/Practice";
import { api, getToken, setToken } from "./api";

export default function App() {
  const [user, setUser] = useState(null);
  const [view, setView] = useState("daily");
  const [checkingSession, setCheckingSession] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setCheckingSession(false);
      return;
    }
    api
      .me()
      .then(setUser)
      .catch(() => setToken(null))
      .finally(() => setCheckingSession(false));
  }, []);

  function handleAuthenticated(loggedInUser) {
    setUser(loggedInUser);
    setView("daily");
  }

  function handleLogout() {
    setToken(null);
    setUser(null);
    setView("daily");
  }

  function handleNavigate(nextView) {
    if (nextView !== "auth" && !user) {
      setView("auth");
      return;
    }
    setView(nextView);
  }

  if (checkingSession) {
    return null;
  }

  return (
    <div className="app-shell">
      <NavBar view={view} onNavigate={handleNavigate} user={user} onLogout={handleLogout} />
      <main className="app-main">
        {view === "auth" && <AuthPanel onAuthenticated={handleAuthenticated} />}
        {view === "daily" && (user ? <DailyPuzzle /> : <AuthPanel onAuthenticated={handleAuthenticated} />)}
        {view === "practice" && <Practice />}
        {view === "leaderboard" && <Leaderboard />}
      </main>
    </div>
  );
}
