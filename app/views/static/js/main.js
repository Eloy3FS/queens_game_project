// static/js/main.js

document.addEventListener("DOMContentLoaded", () => {
    let boardSize   = INITIAL_BOARD_SIZE;
    let gameState   = INITIAL_STATE || {};
    let isMouseDown = false;
    let moved       = false;
    let startCell   = null;
    let dragAction  = null;
    let pendingInitial = false;
  
    const boardSizeInput = document.getElementById("board-size");
    const resetBtn       = document.getElementById("reset-btn");
    const boardElement   = document.getElementById("board");
    const timerElement   = document.getElementById("timer");
    const statusMessage  = document.getElementById("status-message");
  
    function applyBoardSize(n) {
      boardSize = n;
      boardSizeInput.value = n;
      boardElement.style.setProperty("--board-size", n);
    }
  
    function createBoard(state) {
      boardElement.innerHTML = "";
      applyBoardSize(boardSize);
  
      for (let r = 0; r < boardSize; r++) {
        for (let c = 0; c < boardSize; c++) {
          const cell = document.createElement("div");
          cell.className = "cell";
          cell.dataset.row = r;
          cell.dataset.col = c;
  
          // solution color background
          const colRGB = state.colored_board[r]?.[c];
          if (colRGB) cell.style.backgroundColor = `rgb(${colRGB.join(',')})`;
  
          const content = document.createElement("div");
          content.className = "cell-content";
          cell.appendChild(content);
  
          updateCell(cell, state, r, c);
  
          // Mousedown: start drag or pending initial
          cell.addEventListener("mousedown", e => {
            e.preventDefault();
            isMouseDown    = true;
            moved          = false;
            pendingInitial = true;
            startCell      = { r, c };
  
            const cur = gameState.user_board[r][c] || "";
            dragAction = cur === "" ? "cross"
                       : cur === "X" ? "clear"
                       : null;
          });
  
          // Mouseover: handle drag
          cell.addEventListener("mouseover", () => {
            if (isMouseDown && dragAction) {
              if (pendingInitial) {
                doMove(startCell.r, startCell.c, dragAction);
                pendingInitial = false;
              }
              moved = true;
              doMove(r, c, dragAction);
            }
          });
  
          boardElement.appendChild(cell);
        }
      }
    }
  
    document.addEventListener("mouseup", () => {
      if (!isMouseDown) return;
      isMouseDown = false;
  
      const { r, c } = startCell;
      if (!moved) {
        // treat as simple click
        doCycle(r, c);
      }
      // reset flags
      startCell      = null;
      dragAction     = null;
      pendingInitial = false;
      moved          = false;
    });
  
    function doCycle(r, c) {
      const cur = gameState.user_board[r][c] || "";
      const move_type = cur === ""   ? "cross"
                       : cur === "X"  ? "queen"
                       :                 "clear";
      doMove(r, c, move_type);
    }
  
    function doMove(r, c, move_type) {
      return fetch("/move", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ row: r, col: c, move_type })
      })
      .then(res => res.json())
      .then(data => {
        gameState = data.state;
        timerElement.textContent = gameState.elapsed_time;
        statusMessage.textContent = data.message || "";
  
        // update UI
        if (move_type === "queen" || move_type === "clear") {
          // full refresh
          document.querySelectorAll(".cell").forEach(cell => {
            const rr = +cell.dataset.row,
                  cc = +cell.dataset.col;
            updateCell(cell, gameState, rr, cc);
          });
        } else {
          // only that cell for cross/clear
          const sel = `.cell[data-row="${r}"][data-col="${c}"]`;
          const cell = document.querySelector(sel);
          if (cell) updateCell(cell, gameState, r, c);
        }
  
        // if complete, show overlay
        if (gameState.is_complete) {
          showWinOverlay();
        }
      })
      .catch(() => {
        statusMessage.textContent = "Network error.";
      });
    }
  
    function updateCell(cell, state, r, c) {
      const content = cell.firstChild;
      content.innerHTML = "";
      const val = state.user_board[r][c] || "";
      const err = state.error_board[r][c];
  
      if (val === "X") {
        const img = document.createElement("img");
        img.src       = "/static/assets/cross.png";
        img.className = "cross-icon";
        content.appendChild(img);
      }
      if (val === "Q") {
        const img = document.createElement("img");
        img.src       = "/static/assets/queen.png";
        img.className = "queen-icon";
        content.appendChild(img);
      }
      if (err) {
        const img = document.createElement("img");
        img.src       = "/static/assets/error.png";
        img.className = "error-icon";
        content.appendChild(img);
      }
    }
  
    resetBtn.addEventListener("click", () => {
      const sz = parseInt(boardSizeInput.value, 10) || boardSize;
      fetch("/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ board_size: sz })
      })
      .then(res => res.json())
      .then(data => {
        gameState = data.state;
        applyBoardSize(sz);
        createBoard(gameState);
        timerElement.textContent = gameState.elapsed_time;
        statusMessage.textContent = "";
        // remove any existing overlay
        document.getElementById("win-overlay")?.remove();
      });
    });
  
    // Show initial board
    applyBoardSize(boardSize);
    createBoard(gameState);
    timerElement.textContent = gameState.elapsed_time;
  
  
    // ───── Win Overlay ─────
    function showWinOverlay() {
      // Avoid multiple overlays
      if (document.getElementById("win-overlay")) return;
  
      const overlay = document.createElement("div");
      overlay.id = "win-overlay";
      overlay.innerHTML = `
        <div class="win-box">
          <h2>🎉 You Win! 🎉</h2>
          <p>Time: ${gameState.elapsed_time}</p>
          <button id="close-win">Close</button>
        </div>
      `;
      document.body.appendChild(overlay);
      document.getElementById("close-win")
        .addEventListener("click", () => overlay.remove());
    }
  });
  