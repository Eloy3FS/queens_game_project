// File: app/views/static/js/utils.js

import * as state from "./state.js";
import * as dom   from "./dom.js";

/**
 * Recalculate errorBoard: mark pairs of queens that conflict,
 * mutating the existing state.errorBoard in place to avoid
 * reassigning an exported binding.
 */
export function recalcErrors() {
  const n = state.boardSize;

  // Reset all entries to false in place
  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      state.errorBoard[r][c] = false;
    }
  }

  // Gather all queen positions
  const queens = [];
  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      if (state.userBoard[r][c] === "Q") {
        queens.push([r, c]);
      }
    }
  }

  // Helper to mark conflicts
  const mark = (a, b) => {
    state.errorBoard[a[0]][a[1]] = true;
    state.errorBoard[b[0]][b[1]] = true;
  };

  // Pairwise conflict detection
  for (let i = 0; i < queens.length; i++) {
    for (let j = i + 1; j < queens.length; j++) {
      const [r1, c1] = queens[i];
      const [r2, c2] = queens[j];

      // adjacent
      if (Math.max(Math.abs(r1 - r2), Math.abs(c1 - c2)) === 1) {
        mark([r1, c1], [r2, c2]);
      }
      // same row or column
      if (r1 === r2 || c1 === c2) {
        mark([r1, c1], [r2, c2]);
      }
      // same color region
      const col1 = state.coloredBoard[r1][c1];
      const col2 = state.coloredBoard[r2][c2];
      if (
        col1 && col2 &&
        col1[0] === col2[0] &&
        col1[1] === col2[1] &&
        col1[2] === col2[2]
      ) {
        mark([r1, c1], [r2, c2]);
      }
    }
  }
}

/**
 * Update a single cell’s DOM based on userBoard and errorBoard.
 */
export function updateCell(cellEl, r, c) {
  const content = cellEl.querySelector(".cell-content");
  content.innerHTML = "";

  const val = state.userBoard[r][c] || "";
  const err = state.errorBoard[r][c];

  if (val === "X") {
    const img = document.createElement("img");
    img.src = "/static/assets/cross.png";
    img.className = "cross-icon";
    content.appendChild(img);
  }
  if (val === "Q") {
    const img = document.createElement("img");
    img.src = "/static/assets/queen.png";
    img.className = "queen-icon";
    content.appendChild(img);
  }
  if (err) {
    const img = document.createElement("img");
    img.src = "/static/assets/error.png";
    img.className = "error-icon";
    content.appendChild(img);
  }
}

/**
 * Re-render all cells on the board.
 */
export function updateBoardUI() {
  document.querySelectorAll(".cell").forEach(cellEl => {
    const r = +cellEl.dataset.row;
    const c = +cellEl.dataset.col;
    updateCell(cellEl, r, c);
  });
}

/**
 * Show the win overlay when game completes.
 */
export function showWinOverlay() {
  if (document.getElementById("win-overlay")) return;
  clearInterval(window._timerInterval);

  const ov = document.createElement("div");
  ov.id = "win-overlay";
  ov.innerHTML = `
    <div class="win-box">
      <h2>🎉 You Win! 🎉</h2>
      <p>Time: ${dom.timerEl.textContent}</p>
      <button id="close-win" class="btn btn-primary rounded-pill">Close</button>
    </div>`;
  document.body.appendChild(ov);
  document.getElementById("close-win").addEventListener("click", () => ov.remove());
}

/**
 * Send a move to the server and update timer/status.
 */
export function sendMove(r, c, moveType) {
  fetch("/move", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ row: r, col: c, move_type: moveType })
  })
    .then(res => res.json())
    .then(data => {
      dom.timerEl.textContent       = data.state.elapsed_time;
      dom.statusMessage.textContent = data.message || "";
      if (data.state.is_complete) showWinOverlay();
    })
    .catch(() => {});
}

/**
 * Return list of conflict cells for a queen at (r0,c0).
 */
export function conflictCells(r0, c0) {
  const cells = [];
  for (let r = 0; r < state.boardSize; r++) {
    for (let c = 0; c < state.boardSize; c++) {
      if (r === r0 && c === c0) continue;
      if (Math.max(Math.abs(r - r0), Math.abs(c - c0)) === 1) {
        cells.push([r, c]);
        continue;
      }
      if (r === r0 || c === c0) {
        cells.push([r, c]);
        continue;
      }
      const col1 = state.coloredBoard[r0][c0];
      const col2 = state.coloredBoard[r][c];
      if (
        col1 && col2 &&
        col1[0] === col2[0] &&
        col1[1] === col2[1] &&
        col1[2] === col2[2]
      ) {
        cells.push([r, c]);
      }
    }
  }
  return cells;
}

/**
 * Place auto-crosses around a queen.
 */
export function addAutoCrosses(r, c) {
  conflictCells(r, c).forEach(([i, j]) => {
    if (state.userBoard[i][j] === "Q") return;
    if (state.userBoard[i][j] !== "X") {
      state.userBoard[i][j] = "X";
      state.autoCrossCounts[i][j] = 1;
    } else {
      state.autoCrossCounts[i][j]++;
    }
  });
}

/**
 * Remove auto-crosses when clearing a queen.
 */
export function removeAutoCrosses(r, c) {
  conflictCells(r, c).forEach(([i, j]) => {
    if (state.autoCrossCounts[i][j] > 0) {
      state.autoCrossCounts[i][j]--;
      if (state.autoCrossCounts[i][j] === 0 && state.userBoard[i][j] === "X") {
        state.userBoard[i][j] = "";
      }
    }
  });
}

/**
 * Apply a local move: cross, queen, or clear.
 */
export function applyLocalMove(r, c, moveType) {
  if (moveType === "cross") {
    state.userBoard[r][c] = "X";
  } else if (moveType === "queen") {
    state.userBoard[r][c] = "Q";
    if (state.autoCompleteEnabled) addAutoCrosses(r, c);
  } else if (moveType === "clear") {
    if (state.autoCompleteEnabled) removeAutoCrosses(r, c);
    state.userBoard[r][c] = "";
  }

  recalcErrors();
  updateBoardUI();
  sendMove(r, c, moveType);
}
