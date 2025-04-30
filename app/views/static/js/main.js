// app/views/static/js/main.js

import "./dom.js";         // inicializa referencias
import "./state.js";       // inicializa estado
import "./utils.js";       // registra utilidades
import { initDrag }    from "./drag.js";
import { buildBoard }  from "./buildBoard.js";
import { initHint }    from "./hint.js";
import { initSettings} from "./settings.js";
import { startTimer }  from "./timer.js";

// ── DEBUG: main.js has been loaded as a module ──
console.log("✅ [main.js] module loaded, waiting for DOMContentLoaded");

document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ [main.js] DOMContentLoaded: building board with size=", window.INITIAL_BOARD_SIZE);
  buildBoard();
  initDrag();
  initHint();
  initSettings();
  startTimer();
});
