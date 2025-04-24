// app/views/static/js/main.js

document.addEventListener("DOMContentLoaded", () => {
  // ----- State & Flags -----
  let boardSize    = INITIAL_BOARD_SIZE;
  let gameState    = INITIAL_STATE || {};

  let isDragging   = false;
  let hasDragged   = false;
  let dragAction   = null;      // "cross" | "clear" | null
  let startCell    = null;      // { r, c }
  let startState   = null;      // "" | "X" | "Q"
  let visitedCells = new Set(); // avoid repeats

  // ----- DOM Refs -----
  const boardEl          = document.getElementById("board");
  const timerEl          = document.getElementById("timer");
  const statusMessage    = document.getElementById("status-message");
  const settingsBtn      = document.getElementById("settings-btn");
  const overlay          = document.getElementById("settings-overlay");
  const closeSettingsBtn = document.getElementById("close-settings-btn");
  const darkSwitch       = document.getElementById("dark-mode-switch");
  const sizeInput        = document.getElementById("settings-board-size");
  const sizeValue        = document.getElementById("settings-size-value");
  const applySettingsBtn = document.getElementById("apply-settings-btn");
  const resetBtn         = document.getElementById("reset-btn");
  const clearBtn         = document.getElementById("clear-btn");

  // ----- Timer Helpers -----
  function parseTimeToSeconds(str) {
    const [m, s] = str.split(":").map(Number);
    return m * 60 + s;
  }
  function startTimer() {
    clearInterval(window._timerInterval);
    fetch("/get_time")
      .then(r => r.json())
      .then(data => {
        timerEl.textContent = data.elapsed_time;
        const base = parseTimeToSeconds(data.elapsed_time),
              t0   = Date.now();
        window._timerInterval = setInterval(() => {
          const d   = Math.floor((Date.now() - t0) / 1000),
                tot = base + d,
                mm  = Math.floor(tot / 60),
                ss  = tot % 60;
          timerEl.textContent = `${String(mm).padStart(2,"0")}:${String(ss).padStart(2,"0")}`;
        }, 1000);
      });
  }

  // ----- AJAX -----
  function doMove(r, c, moveType) {
    return fetch("/move", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ row: r, col: c, move_type: moveType })
    })
    .then(r => r.json())
    .then(data => {
      gameState = data.state;
      timerEl.textContent = gameState.elapsed_time;
      statusMessage.textContent = data.message || "";
      // re-render all cells
      document.querySelectorAll(".cell").forEach(cell => {
        updateCell(cell,
          gameState,
          +cell.dataset.row,
          +cell.dataset.col
        );
      });
      if (gameState.is_complete) showWinOverlay();
    });
  }

  function doReset(size) {
    fetch("/reset", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ board_size: size })
    })
    .then(r => r.json())
    .then(data => {
      gameState = data.state;
      buildBoard(gameState);
      timerEl.textContent = gameState.elapsed_time;
      statusMessage.textContent = "";
      document.getElementById("win-overlay")?.remove();
      startTimer();
    });
  }

  // ----- Rendering Helpers -----
  function updateCell(cell, state, r, c) {
    const content = cell.firstChild;
    content.innerHTML = "";
    const val = state.user_board[r][c] || "";
    const err = state.error_board[r][c];
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

  function showWinOverlay() {
    if (document.getElementById("win-overlay")) return;
    clearInterval(window._timerInterval);
    const ov = document.createElement("div");
    ov.id = "win-overlay";
    ov.innerHTML = `
      <div class="win-box">
        <h2>🎉 You Win! 🎉</h2>
        <p>Time: ${gameState.elapsed_time}</p>
        <button id="close-win" class="btn btn-primary rounded-pill">Close</button>
      </div>`;
    document.body.appendChild(ov);
    document.getElementById("close-win")
      .addEventListener("click", () => ov.remove());
  }

  // ----- Drag Logic via Pointer Events -----
  function applyAction(r, c, action) {
    const curr = gameState.user_board[r][c] || "";
    if (action === "cross" && curr === "") {
      doMove(r, c, "cross");
    } else if (action === "clear" && curr === "X") {
      doMove(r, c, "clear");
    }
  }

  function onPointerDown(e) {
    const cell = e.target.closest(".cell");
    if (!cell) return;
    e.preventDefault();
    isDragging  = true;
    hasDragged  = false;
    const r = +cell.dataset.row, c = +cell.dataset.col;
    startCell   = { r, c };
    startState  = gameState.user_board[r][c] || "";
    dragAction  = null;
    visitedCells.clear();
  }

  function onPointerMove(e) {
    if (!isDragging) return;
    const el = document.elementFromPoint(e.clientX, e.clientY)?.closest(".cell");
    if (!el) return;
    const r = +el.dataset.row, c = +el.dataset.col;
    if (startState === "Q") return;  // never touch queens

    const key = `${r}_${c}`;
    if (!hasDragged) {
      hasDragged = true;
      dragAction = startState === ""  ? "cross"
                 : startState === "X" ? "clear"
                 : null;
      if (!dragAction) return;
      // apply to startCell + this cell
      applyAction(startCell.r, startCell.c, dragAction);
      visitedCells.add(`${startCell.r}_${startCell.c}`);
      applyAction(r, c, dragAction);
      visitedCells.add(key);
    } else {
      if (!dragAction || visitedCells.has(key)) return;
      applyAction(r, c, dragAction);
      visitedCells.add(key);
    }
  }

  function onPointerUp(e) {
    if (!isDragging) return;
    // simple click?
    if (!hasDragged && startCell) {
      const { r, c } = startCell;
      const curr = gameState.user_board[r][c] || "";
      const moveType = curr === ""  ? "cross"
                     : curr === "X" ? "queen"
                     :                "clear";
      doMove(r, c, moveType);
    }
    // reset
    isDragging  = false;
    hasDragged  = false;
    dragAction  = null;
    startCell   = null;
    startState  = null;
    visitedCells.clear();
  }

  // hook pointer events
  document.addEventListener("pointermove", onPointerMove, { passive: false });
  document.addEventListener("pointerup",   onPointerUp);
  document.addEventListener("pointercancel", onPointerUp);

  // ----- Build Board & Attach Listeners -----
  function buildBoard(state) {
    gameState = state;
    boardEl.innerHTML = "";
    boardEl.style.setProperty("--board-size", boardSize);

    for (let r = 0; r < boardSize; r++) {
      for (let c = 0; c < boardSize; c++) {
        const cell = document.createElement("div");
        cell.className = "cell";
        cell.dataset.row = r;
        cell.dataset.col = c;
        const rgb = state.colored_board[r]?.[c];
        if (rgb) cell.style.backgroundColor = `rgb(${rgb.join(",")})`;

        const content = document.createElement("div");
        content.className = "cell-content";
        cell.appendChild(content);

        // unified pointerdown
        cell.addEventListener("pointerdown", onPointerDown);
        boardEl.appendChild(cell);
      }
    }

    // initial render
    document.querySelectorAll(".cell").forEach(cell => {
      updateCell(cell,
                 gameState,
                 +cell.dataset.row,
                 +cell.dataset.col);
    });
  }

  // ----- UI Controls -----
  // Dark mode
  darkSwitch.checked = window.matchMedia("(prefers-color-scheme: dark)").matches;
  darkSwitch.addEventListener("change", () => {
    document.body.classList.toggle("dark-mode", darkSwitch.checked);
  });

  // Settings panel
  settingsBtn.addEventListener("click",      () => overlay.classList.add("show"));
  closeSettingsBtn.addEventListener("click", () => overlay.classList.remove("show"));
  sizeValue.textContent = sizeInput.value;
  sizeInput.addEventListener("input", () => {
    sizeValue.textContent = sizeInput.value;
  });
  applySettingsBtn.addEventListener("click", () => {
    boardSize = parseInt(sizeInput.value, 10);
    boardEl.style.setProperty("--board-size", boardSize);
    doReset(boardSize);
    overlay.classList.remove("show");
  });

  resetBtn.addEventListener("click", () => doReset(boardSize));
  clearBtn.addEventListener("click", () => {
    for (let r = 0; r < boardSize; r++) {
      for (let c = 0; c < boardSize; c++) {
        if (gameState.user_board[r][c] === "X") {
          doMove(r, c, "clear");
        }
      }
    }
  });

  // ----- Init -----
  buildBoard(gameState);
  timerEl.textContent = gameState.elapsed_time;
  startTimer();
});
