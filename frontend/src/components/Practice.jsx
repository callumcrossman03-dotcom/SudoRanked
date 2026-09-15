import { useState } from "react";
import SudokuBoard from "./SudokuBoard";
import { api, ApiError } from "../api";

const DIFFICULTIES = ["easy", "medium", "hard"];

export default function Practice() {
  const [difficulty, setDifficulty] = useState("medium");
  const [puzzle, setPuzzle] = useState(null); // { id, difficulty, grid }
  const [grid, setGrid] = useState(null);
  const [incorrectCells, setIncorrectCells] = useState([]);
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleNewPuzzle() {
    setLoading(true);
    setError(null);
    setMessage(null);
    setIncorrectCells([]);
    try {
      const data = await api.newPractice(difficulty);
      setPuzzle(data);
      setGrid([...data.grid]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't generate a puzzle.");
    } finally {
      setLoading(false);
    }
  }

  async function handleCheck() {
    if (!puzzle) return;
    setError(null);
    try {
      const res = await api.checkPractice(puzzle.id, grid);
      setIncorrectCells(res.incorrect_cells);
      setMessage(res.is_correct ? "Correct -- nice work." : "Not quite yet -- red cells don't match the solution.");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't check your solution.");
    }
  }

  return (
    <div>
      <h2>Practice</h2>
      <p className="hint">Unlimited puzzles, no ranking. Good for warming up before the daily.</p>

      <div style={{ display: "flex", gap: "0.5rem", margin: "1rem 0 1.5rem", flexWrap: "wrap" }}>
        {DIFFICULTIES.map((d) => (
          <button key={d} className={difficulty === d ? "" : "secondary"} onClick={() => setDifficulty(d)}>
            {d[0].toUpperCase() + d.slice(1)}
          </button>
        ))}
        <button className="secondary" onClick={handleNewPuzzle} disabled={loading}>
          {loading ? "Generating..." : puzzle ? "New puzzle" : "Start"}
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {puzzle && (
        <>
          <SudokuBoard
            givens={puzzle.grid}
            value={grid}
            incorrectCells={incorrectCells}
            onChange={(i, v) =>
              setGrid((g) => {
                const next = [...g];
                next[i] = v;
                return next;
              })
            }
          />

          {message && (
            <p style={{ marginTop: "1.2rem", textAlign: "center", fontWeight: 600, color: incorrectCells.length ? "var(--bad)" : "var(--good)" }}>
              {message}
            </p>
          )}

          <div style={{ display: "flex", justifyContent: "center", marginTop: "1.5rem" }}>
            <button onClick={handleCheck}>Check solution</button>
          </div>
        </>
      )}
    </div>
  );
}
