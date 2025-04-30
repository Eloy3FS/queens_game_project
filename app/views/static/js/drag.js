// app/views/static/js/drag.js
import * as dom   from "./dom.js";
import * as state from "./state.js";
import { applyLocalMove } from "./utils.js";

let hasDragged, dragAction, startCell, startState, visitedCells;

export function initDrag() {
  hasDragged   = false;
  dragAction   = null;
  startCell    = null;
  startState   = null;
  visitedCells = new Set();

  dom.boardEl.addEventListener("pointerdown", onPointerDown);
  document.addEventListener("pointermove", onPointerMove, { passive: false });
  document.addEventListener("pointerup",   onPointerUp);
  document.addEventListener("pointercancel", onPointerUp);
}

function onPointerDown(e) {
  const cell = e.target.closest(".cell");
  if (!cell) return;
  e.preventDefault();
  hasDragged = false;
  startCell  = { r:+cell.dataset.row, c:+cell.dataset.col };
  startState = state.userBoard[startCell.r][startCell.c] || "";
  dragAction = null;
  visitedCells.clear();
}

function onPointerMove(e) {
  const el = document.elementFromPoint(e.clientX, e.clientY)?.closest(".cell");
  if (!el || !startCell) return;
  const r = +el.dataset.row, c = +el.dataset.col;
  if (!hasDragged) {
    if (r===startCell.r && c===startCell.c) return;
    hasDragged = true;
    dragAction = startState==="" 
               ? "cross"
               : startState==="X"
                 ? "clear"
                 : null;
    if (dragAction) applyLocalMove(startCell.r, startCell.c, dragAction), visitedCells.add(`${startCell.r}_${startCell.c}`);
  }
  const key = `${r}_${c}`;
  if (dragAction && !visitedCells.has(key)) {
    applyLocalMove(r, c, dragAction);
    visitedCells.add(key);
  }
}

function onPointerUp(e) {
  if (!startCell) return;
  if (!hasDragged) {
    let moveType = startState==="" ? "cross"
                 : startState==="X" ? "queen"
                 : "clear";
    applyLocalMove(startCell.r, startCell.c, moveType);
  }
  startCell = null;
}
