import { useState } from "react";
import { api, setToken, ApiError } from "../api";

export default function AuthPanel({ onAuthenticated }) {
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      if (mode === "register") {
        await api.register(username, password);
      }
      const { access_token } = await api.login(username, password);
      setToken(access_token);
      const user = await api.me();
      onAuthenticated(user);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h2>{mode === "login" ? "Log in" : "Create an account"}</h2>
      <p className="hint">
        {mode === "login"
          ? "Log in to play today's puzzle and appear on the leaderboard."
          : "Pick a username -- this is what other players will see on the leaderboard."}
      </p>

      {error && <div className="error-banner">{error}</div>}

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "0.8rem", maxWidth: 320 }}>
        <label>
          <div className="hint" style={{ marginBottom: "0.3em" }}>
            Username
          </div>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            minLength={3}
            maxLength={32}
            autoComplete="username"
            style={{ width: "100%" }}
          />
        </label>

        <label>
          <div className="hint" style={{ marginBottom: "0.3em" }}>
            Password
          </div>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            maxLength={72}
            autoComplete={mode === "login" ? "current-password" : "new-password"}
            style={{ width: "100%" }}
          />
        </label>

        <button type="submit" disabled={busy}>
          {busy ? "Please wait..." : mode === "login" ? "Log in" : "Create account"}
        </button>
      </form>

      <p className="hint" style={{ marginTop: "1rem" }}>
        {mode === "login" ? "New here? " : "Already have an account? "}
        <button
          className="secondary"
          style={{ padding: "0.2em 0.5em", fontSize: "0.9rem" }}
          onClick={() => {
            setMode(mode === "login" ? "register" : "login");
            setError(null);
          }}
        >
          {mode === "login" ? "Create an account" : "Log in"}
        </button>
      </p>
    </div>
  );
}
