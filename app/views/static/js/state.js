// File: app/views/static/js/state.js

// Pull in server-injected constants
const {
    INITIAL_BOARD_SIZE,
    INITIAL_STATE,
    INITIAL_GEN_MODE
  } = window;
  
  // Reactive game state
  export let boardSize           = INITIAL_BOARD_SIZE;
  export let generationMode      = INITIAL_GEN_MODE;
  export let autoCompleteEnabled = true;
  
  export let userBoard    = INITIAL_STATE.user_board.map(row => row.slice());
  export let coloredBoard = INITIAL_STATE.colored_board.map(row =>
    row.map(cell => (cell ? [...cell] : null))
  );
  export let errorBoard   = INITIAL_STATE.error_board.map(row => row.slice());
  export let autoCrossCounts = Array.from(
    { length: boardSize },
    () => Array(boardSize).fill(0)
  );
  
  // Called after a /reset response to overwrite the entire state
  export function updateState(newState) {
    boardSize           = newState.user_board.length;
    generationMode      = newState.gen_mode;
    autoCompleteEnabled = newState.auto_complete_enabled ?? true;
  
    userBoard    = newState.user_board.map(row => row.slice());
    coloredBoard = newState.colored_board.map(row =>
      row ? row.map(cell => (cell ? [...cell] : null)) : null
    );
    errorBoard   = newState.error_board.map(row => row.slice());
  
    // rebuild autoCrossCounts
    autoCrossCounts = Array.from(
      { length: boardSize },
      () => Array(boardSize).fill(0)
    );
  }
  
  // Reset just the autoCrossCounts matrix
  export function resetAutoCrossCounts() {
    autoCrossCounts = Array.from(
      { length: boardSize },
      () => Array(boardSize).fill(0)
    );
  }
  
  // ─── New setter exports for settings.js ───
  export function setAutoCompleteEnabled(val) {
    autoCompleteEnabled = val;
  }
  
  export function setBoardSize(val) {
    boardSize = val;
    resetAutoCrossCounts();
  }
  
  export function setGenerationMode(val) {
    generationMode = val;
  }
  