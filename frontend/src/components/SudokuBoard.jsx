import "./SudokuBoard.css";

/**
 * givens: length-81 array, 0 = blank. Cells with a nonzero given are fixed.
 * value: length-81 array representing the player's current working grid.
 * onChange(index, newValue): called when an editable cell changes.
 * incorrectCells: optional array of indices to mark red (practice mode feedback).
 * locked: if true, no cell is editable (e.g. after a correct submission).
 */
export default function SudokuBoard({ givens, value, onChange, incorrectCells = [], locked = false }) {
  const incorrectSet = new Set(incorrectCells);

  function handleKeyChange(index, raw) {
    if (raw === "") {
      onChange(index, 0);
      return;
    }
    const digit = raw.replace(/[^1-9]/g, "").slice(-1);
    if (digit) onChange(index, Number(digit));
  }

  return (
    <div className="sudoku-board" role="grid" aria-label="Sudoku puzzle">
      {value.map((cellValue, index) => {
        const isGiven = givens[index] !== 0;
        const row = Math.floor(index / 9);
        const col = index % 9;
        const classes = [
          "sudoku-cell",
          isGiven ? "given" : "editable",
          incorrectSet.has(index) ? "incorrect" : "",
          col % 3 === 0 ? "box-left" : "",
          col === 8 ? "box-right" : "",
          row % 3 === 0 ? "box-top" : "",
          row === 8 ? "box-bottom" : "",
        ]
          .filter(Boolean)
          .join(" ");

        return isGiven ? (
          <div key={index} className={classes} role="gridcell" aria-readonly="true">
            {cellValue}
          </div>
        ) : (
          <input
            key={index}
            className={classes}
            role="gridcell"
            inputMode="numeric"
            pattern="[1-9]"
            maxLength={1}
            value={cellValue === 0 ? "" : String(cellValue)}
            disabled={locked}
            onChange={(e) => handleKeyChange(index, e.target.value)}
            aria-label={`Row ${row + 1}, column ${col + 1}`}
          />
        );
      })}
    </div>
  );
}
