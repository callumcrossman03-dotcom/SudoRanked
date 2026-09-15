import { useEffect, useState } from "react";
import { api, ApiError } from "../api";

export default function Leaderboard() {
  const [mode, setMode] = useState("daily"); // "daily" | "alltime"
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    const fetcher = mode === "daily" ? api.dailyLeaderboard : api.alltimeLeaderboard;
    fetcher()
      .then(setRows)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Couldn't load the leaderboard."))
      .finally(() => setLoading(false));
  }, [mode]);

  return (
    <div>
      <h2>Leaderboard</h2>

      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1.2rem" }}>
        <button className={mode === "daily" ? "" : "secondary"} onClick={() => setMode("daily")}>
          Today
        </button>
        <button className={mode === "alltime" ? "" : "secondary"} onClick={() => setMode("alltime")}>
          All-time
        </button>
      </div>

      {loading && <p className="hint">Loading...</p>}
      {error && <div className="error-banner">{error}</div>}

      {!loading && !error && rows.length === 0 && (
        <p className="hint">
          {mode === "daily" ? "Nobody has finished today's puzzle yet -- be the first." : "No points on the board yet."}
        </p>
      )}

      {!loading && !error && rows.length > 0 && (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--rule)", textAlign: "left" }}>
              <th style={{ padding: "0.5em 0.4em", width: "3em" }}>#</th>
              <th style={{ padding: "0.5em 0.4em" }}>Player</th>
              <th style={{ padding: "0.5em 0.4em", textAlign: "right" }}>
                {mode === "daily" ? "Time" : "Days played"}
              </th>
              <th style={{ padding: "0.5em 0.4em", textAlign: "right" }}>Points</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr
                key={row.username}
                style={{
                  borderBottom: "1px solid var(--rule)",
                  borderLeft: row.rank === 1 ? "3px solid var(--gold-strong)" : "3px solid transparent",
                }}
              >
                <td className="mono" style={{ padding: "0.6em 0.4em" }}>
                  {row.rank}
                </td>
                <td style={{ padding: "0.6em 0.4em", fontWeight: 600 }}>{row.username}</td>
                <td className="mono" style={{ padding: "0.6em 0.4em", textAlign: "right" }}>
                  {mode === "daily" ? `${row.elapsed_seconds.toFixed(2)}s` : row.days_played}
                </td>
                <td className="mono" style={{ padding: "0.6em 0.4em", textAlign: "right" }}>
                  {mode === "daily" ? row.points : row.total_points}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
