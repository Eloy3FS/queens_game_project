// File: app/views/static/js/settings.js

import * as dom   from "./dom.js";
import * as state from "./state.js";
import { buildBoard } from "./buildBoard.js";
import {
  updateState,
  setAutoCompleteEnabled,
  setGenerationMode,
  setBoardSize
} from "./state.js";
import { applyLocalMove } from "./utils.js";

export function initSettings() {
  // Open/Close overlay
  dom.settingsBtn.addEventListener("click", () => dom.overlay.classList.add("show"));
  dom.closeSettingsBtn.addEventListener("click", () => dom.overlay.classList.remove("show"));

  // Dark mode toggle
  dom.darkSwitch.checked = window.matchMedia("(prefers-color-scheme: dark)").matches;
  dom.darkSwitch.addEventListener("change", () =>
    document.body.classList.toggle("dark-mode", dom.darkSwitch.checked)
  );

  // Auto-cross toggle
  dom.autoCrossSwitch.checked = state.autoCompleteEnabled;
  dom.autoCrossSwitch.addEventListener("change", () =>
    setAutoCompleteEnabled(dom.autoCrossSwitch.checked)
  );

  // Board size slider
  dom.sizeValue.textContent = dom.sizeInput.value;
  dom.sizeInput.addEventListener("input", () => {
    dom.sizeValue.textContent = dom.sizeInput.value;
  });

  // Apply settings: fetch new game state
  dom.applySettingsBtn.addEventListener("click", () => {
    const newSize = +dom.sizeInput.value;
    const newMode = dom.genModeSelect.value;

    // locally update boardSize/genMode before rebuild
    setBoardSize(newSize);
    setGenerationMode(newMode);

    fetch("/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ board_size: newSize, gen_mode: newMode })
    })
    .then(r => r.json())
    .then(data => {
      updateState(data.state);
      dom.overlay.classList.remove("show");
      buildBoard();
    });
  });

  // Quick Reset
  dom.resetBtn.addEventListener("click", () => {
    fetch("/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ board_size: state.boardSize, gen_mode: state.generationMode })
    })
    .then(r => r.json())
    .then(data => {
      updateState(data.state);
      buildBoard();
    });
  });

  // Clear Board: local-only
  dom.clearBtn.addEventListener("click", () => {
    for (let r = 0; r < state.boardSize; r++) {
      for (let c = 0; c < state.boardSize; c++) {
        if (state.userBoard[r][c] === "X" || state.userBoard[r][c] === "Q") {
          applyLocalMove(r, c, "clear");
        }
      }
    }
  });
}
