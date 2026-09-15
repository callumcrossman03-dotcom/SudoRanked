import { useEffect, useState } from "react";
import SudokuBoard from "./SudokuBoard";
import { api, ApiError } from "../api";

// Backend sends naive UTC timestamps (no trailing "Z"); make sure the
// browser parses them as UTC rather than local time.
function parseUtc(isoString) {
  if (!isoString) return null;
  return new Date(isoString.endsWith("Z") ? isoString : isoString + "Z");
}

function formatElapsed(totalSeconds) {
  const s = Math.max(0, Math.floor(totalSeconds));
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
}

export default function DailyPuzzle() {
  const [daily, setDaily] = useState(null);
  const [grid, setGrid] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [startedAt, setStartedAt] = useState(null);
  const [liveElapsed, setLiveElapsed] = useState(null);

  useEffect(() => {
    let cancelled = false;
    api
      .getDailyPuzzle()
      .then((data) => {
        if (cancelled) return;
        setDaily(data);
        setGrid([...data.grid]);
        setStartedAt(parseUtc(data.started_at));
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Couldn't load today's puzzle."))
      .finally(() => setLoading(false));
    return () => {
      cancelled = true;
    };
  }, []);

  // Drives the visible clock while a puzzle is in progress. This is purely
  // cosmetic feedback for the player -- the server independently stamps and
  // computes the authoritative elapsed time when the solution is submitted.
  useEffect(() => {
    if (!daily || daily.attempt_status !== "in_progress" || !startedAt) {
      setLiveElapsed(null);
      return;
    }
    const update = () => setLiveElapsed((Date.now() - startedAt.getTime()) / 1000);
    update();
    const id = setInterval(update, 1000);
    return () => clearInterval(id);
  }, [daily, startedAt]);

  async function handleStart() {
    setError(null);
    try {
      const data = await api.startDailyPuzzle();
      setDaily(data);
      setStartedAt(parseUtc(data.started_at) || new Date());
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't start the puzzle.");
    }
  }

  async function handleSubmit() {
    setSubmitting(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.submitDailyPuzzle(grid);
      setResult(res);
      if (res.is_correct) {
        setDaily((d) => ({ ...d, attempt_status: "completed", elapsed_seconds: res.elapsed_seconds }));
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't submit your solution.");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <p className="hint">Loading today's puzzle...</p>;
  if (error && !daily) return <div className="error-banner">{error}</div>;
  if (!daily) return null;

  return (
    <div>
      <h2>{new Date(daily.puzzle_date + "T00:00:00").toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" })}</h2>
      <p className="hint">Everyone plays the same puzzle today. Fastest correct solve wins the day.</p>

      <div style={{ display: "flex", justifyContent: "center", margin: "1rem 0 1.5rem" }}>
        <span className="mono" style={{ fontSize: "1.6rem", fontWeight: 600 }}>
          {daily.attempt_status === "completed"
            ? formatElapsed(daily.elapsed_seconds)
            : daily.attempt_status === "in_progress"
            ? formatElapsed(liveElapsed ?? 0)
            : "00:00"}
        </span>
      </div>

      <SudokuBoard
        givens={daily.grid}
        value={grid}
        onChange={(i, v) =>
          setGrid((g) => {
            const next = [...g];
            next[i] = v;
            return next;
          })
        }
        locked={daily.attempt_status !== "in_progress"}
      />

      {error && (
        <div className="error-banner" style={{ marginTop: "1.2rem" }}>
          {error}
        </div>
      )}

      {result && !result.is_correct && (
        <div className="error-banner" style={{ marginTop: "1.2rem" }}>
          {result.message}
        </div>
      )}

      {daily.attempt_status === "completed" && (
        <p style={{ marginTop: "1.2rem", color: "var(--good)", fontWeight: 600 }}>
          Solved in {formatElapsed(daily.elapsed_seconds)}. Check the leaderboard to see where you landed.
        </p>
      )}

      <div style={{ display: "flex", justifyContent: "center", marginTop: "1.5rem" }}>
        {daily.attempt_status === "not_started" && <button onClick={handleStart}>Start today's puzzle</button>}
        {daily.attempt_status === "in_progress" && (
          <button onClick={handleSubmit} disabled={submitting}>
            {submitting ? "Checking..." : "Submit solution"}
          </button>
        )}
      </div>
    </div>
  );
}
