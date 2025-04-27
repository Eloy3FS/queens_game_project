// app/views/static/js/main.js

document.addEventListener("DOMContentLoaded", () => {
  // ----- Initial State & Local Model -----
  const INITIAL = INITIAL_STATE;
  let boardSize    = INITIAL_BOARD_SIZE;
  let userBoard    = INITIAL.user_board.map(row => row.slice());
  let coloredBoard = INITIAL.colored_board.map(row => row.map(cell => cell ? [...cell] : null));
  let errorBoard   = INITIAL.error_board.map(row => row.slice());
  let autoCrossCounts = Array.from({ length: boardSize }, () =>
    Array(boardSize).fill(0)
  );

  // ----- Drag & Action Flags -----
  let isDragging   = false;
  let hasDragged   = false;
  let dragAction   = null;      // "cross" | "clear" | null
  let startCell    = null;      // { r, c }
  let startState   = null;      // "" | "X" | "Q"
  let visitedCells = new Set();

  // ----- Settings Flags -----
  let autoCompleteEnabled = true;

  // ----- DOM References -----
  const boardEl           = document.getElementById("board");
  const timerEl           = document.getElementById("timer");
  const statusMessage     = document.getElementById("status-message");
  const settingsBtn       = document.getElementById("settings-btn");
  const overlay           = document.getElementById("settings-overlay");
  const closeSettingsBtn  = document.getElementById("close-settings-btn");
  const darkSwitch        = document.getElementById("dark-mode-switch");
  const autoCrossSwitch   = document.getElementById("auto-cross-switch");
  const sizeInput         = document.getElementById("settings-board-size");
  const sizeValue         = document.getElementById("settings-size-value");
  const applySettingsBtn  = document.getElementById("apply-settings-btn");
  const resetBtn          = document.getElementById("reset-btn");
  const clearBtn          = document.getElementById("clear-btn");

  // ----- Recalculate Errors (client-side) -----
  function recalcErrors() {
    const n = boardSize;
    errorBoard = Array.from({ length: n }, () => Array(n).fill(false));

    const queens = [];
    for (let r = 0; r < n; r++) {
      for (let c = 0; c < n; c++) {
        if (userBoard[r][c] === "Q") queens.push([r, c]);
      }
    }

    function mark(a, b) {
      errorBoard[a[0]][a[1]] = true;
      errorBoard[b[0]][b[1]] = true;
    }

    for (let i = 0; i < queens.length; i++) {
      for (let j = i + 1; j < queens.length; j++) {
        const [r1, c1] = queens[i];
        const [r2, c2] = queens[j];
        // adjacent
        if (Math.max(Math.abs(r1 - r2), Math.abs(c1 - c2)) === 1) {
          mark([r1, c1], [r2, c2]);
        }
        // same row/col
        if (r1 === r2 || c1 === c2) {
          mark([r1, c1], [r2, c2]);
        }
        // same color region
        const col1 = coloredBoard[r1][c1];
        const col2 = coloredBoard[r2][c2];
        if (col1 && col2 &&
            col1[0] === col2[0] &&
            col1[1] === col2[1] &&
            col1[2] === col2[2]) {
          mark([r1, c1], [r2, c2]);
        }
      }
    }
  }

  // ----- UI Rendering -----
  function updateCell(cell, r, c) {
    const content = cell.firstChild;
    content.innerHTML = "";
    const val = userBoard[r][c] || "";
    const err = errorBoard[r][c];

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

  function updateBoardUI() {
    document.querySelectorAll(".cell").forEach(cell => {
      const r = +cell.dataset.row;
      const c = +cell.dataset.col;
      updateCell(cell, r, c);
    });
  }

  // ----- Win Overlay -----
  function showWinOverlay() {
    if (document.getElementById("win-overlay")) return;
    clearInterval(window._timerInterval);
    const ov = document.createElement("div");
    ov.id = "win-overlay";
    ov.innerHTML = `
      <div class="win-box">
        <h2>🎉 You Win! 🎉</h2>
        <p>Time: ${timerEl.textContent}</p>
        <button id="close-win" class="btn btn-primary rounded-pill">Close</button>
      </div>`;
    document.body.appendChild(ov);
    document.getElementById("close-win")
      .addEventListener("click", () => ov.remove());
  }

  // ----- Server Sync (optimistic) -----
  function sendMove(r, c, moveType) {
    fetch("/move", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ row: r, col: c, move_type: moveType })
    })
    .then(res => res.json())
    .then(data => {
      timerEl.textContent = data.state.elapsed_time;
      statusMessage.textContent = data.message || "";
      if (data.state.is_complete) {
        showWinOverlay();
      }
    })
    .catch(() => {
      // ignore errors
    });
  }

  // ----- Auto-Cross Helpers -----
  function conflictCells(r0, c0) {
    const cells = [];
    for (let r = 0; r < boardSize; r++) {
      for (let c = 0; c < boardSize; c++) {
        if (r === r0 && c === c0) continue;
        // adjacent
        if (Math.max(Math.abs(r - r0), Math.abs(c - c0)) === 1) {
          cells.push([r, c]); continue;
        }
        // same row/col
        if (r === r0 || c === c0) {
          cells.push([r, c]); continue;
        }
        // same color region
        const col1 = coloredBoard[r0][c0];
        const col2 = coloredBoard[r][c];
        if (col1 && col2 &&
            col1[0] === col2[0] &&
            col1[1] === col2[1] &&
            col1[2] === col2[2]) {
          cells.push([r, c]);
        }
      }
    }
    return cells;
  }

  function addAutoCrosses(r, c) {
    for (let [i, j] of conflictCells(r, c)) {
      if (userBoard[i][j] === "Q") continue;
      if (userBoard[i][j] !== "X") {
        userBoard[i][j] = "X";
        autoCrossCounts[i][j] = 1;
      } else if (autoCrossCounts[i][j] > 0) {
        autoCrossCounts[i][j]++;
      }
    }
  }

  function removeAutoCrosses(r, c) {
    for (let [i, j] of conflictCells(r, c)) {
      if (autoCrossCounts[i][j] > 0) {
        autoCrossCounts[i][j]--;
        if (autoCrossCounts[i][j] === 0 && userBoard[i][j] === "X") {
          userBoard[i][j] = "";
        }
      }
    }
  }

  // ----- Apply Local Move -----
  function applyLocalMove(r, c, moveType) {
    if (moveType === "cross") {
      userBoard[r][c] = "X";
    } else if (moveType === "queen") {
      userBoard[r][c] = "Q";
      if (autoCompleteEnabled) addAutoCrosses(r, c);
    } else if (moveType === "clear") {
      if (startState === "Q" && autoCompleteEnabled) {
        removeAutoCrosses(r, c);
      }
      userBoard[r][c] = "";
    }
    recalcErrors();
    updateBoardUI();
    sendMove(r, c, moveType);
  }

  // ----- Drag & Click via PointerEvents -----
  function onPointerDown(e) {
    const cell = e.target.closest(".cell");
    if (!cell) return;
    e.preventDefault();
    isDragging   = true;
    hasDragged   = false;
    visitedCells.clear();
    const r = +cell.dataset.row;
    const c = +cell.dataset.col;
    startCell    = { r, c };
    startState   = userBoard[r][c] || "";
    dragAction   = null;
  }

  function onPointerMove(e) {
    if (!isDragging) return;
    const el = document.elementFromPoint(e.clientX, e.clientY)?.closest(".cell");
    if (!el) return;
    const r = +el.dataset.row;
    const c = +el.dataset.col;

    if (!hasDragged) {
      if (r === startCell.r && c === startCell.c) return;
      hasDragged  = true;
      dragAction  = startState === ""  ? "cross"
                  : startState === "X" ? "clear"
                  : null;
      if (!dragAction) return;
      applyLocalMove(startCell.r, startCell.c, dragAction);
      visitedCells.add(`${startCell.r}_${startCell.c}`);
      applyLocalMove(r, c, dragAction);
      visitedCells.add(`${r}_${c}`);
    } else {
      const key = `${r}_${c}`;
      if (!dragAction || visitedCells.has(key)) return;
      applyLocalMove(r, c, dragAction);
      visitedCells.add(key);
    }
  }

  function onPointerUp(e) {
    if (!isDragging) return;
    if (!hasDragged && startCell) {
      const { r, c } = startCell;
      const prev    = startState;
      let moveType;
      if (prev === "")       moveType = "cross";
      else if (prev === "X") moveType = "queen";
      else                    moveType = "clear";
      applyLocalMove(r, c, moveType);
    }
    isDragging   = false;
    hasDragged   = false;
    dragAction   = null;
    startCell    = null;
    startState   = null;
    visitedCells.clear();
  }

  document.addEventListener("pointermove",   onPointerMove,   { passive: false });
  document.addEventListener("pointerup",     onPointerUp);
  document.addEventListener("pointercancel", onPointerUp);

  // ----- Build Board -----
  function buildBoard() {
    boardEl.innerHTML = "";
    boardEl.style.setProperty("--board-size", boardSize);
    autoCrossCounts = Array.from({ length: boardSize }, () =>
      Array(boardSize).fill(0)
    );
    for (let r = 0; r < boardSize; r++) {
      for (let c = 0; c < boardSize; c++) {
        const cell = document.createElement("div");
        cell.className   = "cell";
        cell.dataset.row = r;
        cell.dataset.col = c;
        const rgb = coloredBoard[r][c];
        if (rgb) cell.style.backgroundColor = `rgb(${rgb.join(",")})`;
        const content = document.createElement("div");
        content.className = "cell-content";
        cell.appendChild(content);
        cell.addEventListener("pointerdown", onPointerDown);
        boardEl.appendChild(cell);
      }
    }
    recalcErrors();
    updateBoardUI();
  }

  // ----- Settings & Controls -----
  darkSwitch.checked      = window.matchMedia("(prefers-color-scheme: dark)").matches;
  autoCrossSwitch.checked = true;

  darkSwitch.addEventListener("change", () => {
    document.body.classList.toggle("dark-mode", darkSwitch.checked);
  });
  autoCrossSwitch.addEventListener("change", () => {
    autoCompleteEnabled = autoCrossSwitch.checked;
  });

  settingsBtn.addEventListener("click",      () => overlay.classList.add("show"));
  closeSettingsBtn.addEventListener("click", () => overlay.classList.remove("show"));

  sizeValue.textContent = sizeInput.value;
  sizeInput.addEventListener("input", () => {
    sizeValue.textContent = sizeInput.value;
  });

  applySettingsBtn.addEventListener("click", () => {
    boardSize = +sizeInput.value;
    fetch("/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ board_size: boardSize })
    })
    .then(res => res.json())
    .then(data => {
      userBoard    = data.state.user_board.map(row => row.slice());
      coloredBoard = data.state.colored_board.map(row => row.map(cell => cell ? [...cell] : null));
      errorBoard   = data.state.error_board.map(row => row.slice());
      overlay.classList.remove("show");
      buildBoard();
    });
  });

  resetBtn.addEventListener("click", () => {
    fetch("/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ board_size: boardSize })
    })
    .then(res => res.json())
    .then(data => {
      userBoard    = data.state.user_board.map(row => row.slice());
      coloredBoard = data.state.colored_board.map(row => row.map(cell => cell ? [...cell] : null));
      errorBoard   = data.state.error_board.map(row => row.slice());
      buildBoard();
    });
  });

  clearBtn.addEventListener("click", () => {
    const toClear = [];
    for (let r = 0; r < boardSize; r++) {
      for (let c = 0; c < boardSize; c++) {
        if (userBoard[r][c] === "X" || userBoard[r][c] === "Q") {
          toClear.push({ r, c });
        }
      }
    }
    toClear.forEach(({ r, c }) => {
      applyLocalMove(r, c, "clear");
    });
  });

  // ----- Timer Helpers -----
  function parseTimeToSeconds(str) {
    const [m, s] = str.split(":").map(Number);
    return m * 60 + s;
  }
  function startTimer() {
    clearInterval(window._timerInterval);
    fetch("/get_time")
      .then(res => res.json())
      .then(data => {
        timerEl.textContent = data.elapsed_time;
        const base = parseTimeToSeconds(data.elapsed_time), t0 = Date.now();
        window._timerInterval = setInterval(() => {
          const d   = Math.floor((Date.now() - t0) / 1000);
          const tot = base + d;
          const mm  = Math.floor(tot / 60);
          const ss  = tot % 60;
          timerEl.textContent = `${String(mm).padStart(2,"0")}:${String(ss).padStart("0")}`;
        }, 1000);
      });
  }

  // ----- Init -----
  buildBoard();
  startTimer();
});
