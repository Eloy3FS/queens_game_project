// File: app/views/static/js/buildBoard.js

import * as dom from "./dom.js";
import * as state from "./state.js";
import { recalcErrors, updateBoardUI } from "./utils.js";
import { resetAutoCrossCounts } from "./state.js";

export function buildBoard() {
  dom.boardEl.innerHTML = "";
  dom.boardEl.style.setProperty("--board-size", state.boardSize);

  // Reset the auto-cross counters via the state module’s helper
  resetAutoCrossCounts();

  for (let r = 0; r < state.boardSize; r++) {
    for (let c = 0; c < state.boardSize; c++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      cell.dataset.row = r;
      cell.dataset.col = c;
      const rgb = state.coloredBoard[r][c];
      if (rgb) cell.style.backgroundColor = `rgb(${rgb.join(",")})`;
      const content = document.createElement("div");
      content.className = "cell-content";
      cell.appendChild(content);
      cell.addEventListener("pointerdown", dom.onPointerDown);
      dom.boardEl.appendChild(cell);
    }
  }

  recalcErrors();
  updateBoardUI();
}
